"""Service for SNPedia crawling operations."""

import asyncio
import time
import urllib.request
from typing import Optional, Dict, List
from urllib.error import HTTPError, URLError

import aiohttp
from bs4 import BeautifulSoup

from SNPedia.models.snp_models import SNPediaEntry
from SNPedia.data.repositories import SNPRepository, SNPediaRepository
from SNPedia.core.logger import logger
from SNPedia.core.config import get_config


class CrawlerService:
    """Service for crawling SNPedia data."""
    
    def __init__(self):
        self.config = get_config()
        self.snp_repo = SNPRepository()
        self.snpedia_repo = SNPediaRepository()
        self.rsid_info = self._load_existing_data()
        self.common_words = [
            "common", "very common", "most common", "normal", "average",
            "miscall in ancestry", "ancestry miscall", "miscall by ancestry"
        ]
    
    def _load_existing_data(self) -> Dict[str, Dict]:
        """Load existing SNPedia data from file."""
        import os
        import json
        
        results_file = "data/results.json"
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    existing_data = json.load(f)
                    if existing_data:
                        logger.info(f"Loaded existing SNPedia data for {len(existing_data)} RSIDs")
                        return existing_data
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load existing SNPedia data: {e}")
        
        return {}
    
    async def crawl_snps_async(self, rsids: Dict[str, str]) -> Dict[str, Dict]:
        """Crawl SNPs asynchronously."""
        max_concurrent = max(3, min(5, int(5 * self.config.REQUEST_DELAY)))
        semaphore = asyncio.Semaphore(max_concurrent)
        
        rsids_to_fetch = [rsid for rsid in rsids.keys() 
                         if rsid not in self.rsid_info.keys()]
        total_rsids = len(rsids)
        new_rsids = len(rsids_to_fetch)
        
        logger.info(f"Starting async crawl: {new_rsids} new RSIDs out of {total_rsids} total")
        logger.info(f"Using {max_concurrent} concurrent requests with {self.config.REQUEST_DELAY}s delay")
        
        timeout = aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = []
            for rsid in rsids.keys():
                task = self._fetch_rsid_with_semaphore(session, rsid, semaphore)
                tasks.append(task)
            
            completed = 0
            for coro in asyncio.as_completed(tasks):
                await coro
                completed += 1
                
                if completed % 10 == 0:
                    logger.info(f"{completed} out of {total_rsids} completed")
                
                if completed > 0 and completed % self.config.SAVE_PROGRESS_INTERVAL == 0:
                    logger.info("Exporting intermediate results...")
                    self._export_results()
        
        logger.info("Crawl completed")
        return self.rsid_info
    
    def crawl_snps_sync(self, rsids: Dict[str, str]) -> Dict[str, Dict]:
        """Crawl SNPs synchronously."""
        count = 0
        delay_count = 0
        
        for rsid in rsids.keys():
            if rsid not in self.rsid_info.keys():
                delay_count += 1
            
            time.sleep(self.config.REQUEST_DELAY)
            self._fetch_rsid_sync(rsid)
            
            count += 1
            if count > 0 and count % 10 == 0:
                logger.info(f"{count} out of {len(rsids)} completed")
            
            if (delay_count > 0 and 
                delay_count % self.config.SAVE_PROGRESS_INTERVAL == 0):
                logger.info("Exporting intermediate results...")
                self._export_results()
                time.sleep(self.config.RETRY_DELAY * 3)
        
        logger.info("Crawl completed")
        return self.rsid_info
    
    async def _fetch_rsid_with_semaphore(self, session: aiohttp.ClientSession, 
                                       rsid: str, semaphore: asyncio.Semaphore):
        """Fetch RSID with semaphore-based rate limiting."""
        async with semaphore:
            await self._fetch_rsid_async(session, rsid)
            await asyncio.sleep(self.config.REQUEST_DELAY)
    
    async def _fetch_rsid_async(self, session: aiohttp.ClientSession, 
                              rsid: str) -> Optional[Dict]:
        """Fetch RSID data asynchronously."""
        if not rsid or not isinstance(rsid, str):
            logger.error(f"Invalid rsid format: {rsid}")
            return None
        
        if rsid in self.rsid_info.keys():
            return self.rsid_info[rsid]
        
        url = f"{self.config.SNPEDIA_INDEX_URL}/{rsid}"
        logger.info(f"Fetching SNP data: {rsid}")
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                async with session.get(url) as response:
                    if response.status == 404:
                        logger.warning(f"{rsid} not found (404)")
                        return None
                    
                    if response.status == 429:
                        backoff = self.config.RETRY_DELAY * (2 ** attempt)
                        logger.warning(f"Rate limited (429) for {rsid}, waiting {backoff}s")
                        if attempt < self.config.MAX_RETRIES - 1:
                            await asyncio.sleep(backoff)
                            continue
                        return None
                    
                    if response.status in (502, 503, 504):
                        backoff = self.config.RETRY_DELAY * (2 ** attempt)
                        logger.warning(f"Server error ({response.status}) for {rsid}, waiting {backoff}s")
                        if attempt < self.config.MAX_RETRIES - 1:
                            await asyncio.sleep(backoff)
                            continue
                        return None
                    
                    response.raise_for_status()
                    html = await response.text()
                    
                    return self._parse_snpedia_page(rsid, html)
                    
            except Exception as e:
                logger.error(f"Error fetching {rsid}: {str(e)}")
                if attempt < self.config.MAX_RETRIES - 1:
                    await asyncio.sleep(self.config.RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {rsid} after {self.config.MAX_RETRIES} attempts")
        
        return None
    
    def _fetch_rsid_sync(self, rsid: str) -> Optional[Dict]:
        """Fetch RSID data synchronously."""
        if not rsid or not isinstance(rsid, str):
            logger.error(f"Invalid rsid format: {rsid}")
            return None
        
        if rsid in self.rsid_info.keys():
            return self.rsid_info[rsid]
        
        url = f"{self.config.SNPEDIA_INDEX_URL}/{rsid}"
        logger.info(f"Fetching SNP data: {rsid}")
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                response = urllib.request.urlopen(url, timeout=self.config.REQUEST_TIMEOUT)
                html = response.read()
                
                return self._parse_snpedia_page(rsid, html)
                
            except HTTPError as e:
                if e.code == 404:
                    logger.warning(f"{rsid} not found (404)")
                    break
                elif e.code == 429:
                    logger.warning(f"Rate limited (429) for {rsid}")
                    if attempt < self.config.MAX_RETRIES - 1:
                        time.sleep(self.config.RETRY_DELAY * (attempt + 1))
                    else:
                        logger.error(f"Failed to fetch {rsid} after rate limiting")
                else:
                    logger.error(f"HTTP error {e.code} for {rsid}")
                    if attempt < self.config.MAX_RETRIES - 1:
                        time.sleep(self.config.RETRY_DELAY)
                        
            except Exception as e:
                logger.error(f"Error fetching {rsid}: {str(e)}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(self.config.RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {rsid} after {self.config.MAX_RETRIES} attempts")
        
        return None
    
    def _parse_snpedia_page(self, rsid: str, html: str) -> Optional[Dict]:
        """Parse SNPedia HTML page."""
        try:
            bs = BeautifulSoup(html, "html.parser")
            
            entry_data = {
                "Description": "",
                "Variations": [],
                "StabilizedOrientation": "",
            }
            
            # Find tables
            table = bs.find("table", {"class": "sortable smwtable"})
            description = bs.find(
                "table",
                {"style": "border: 1px; background-color: #FFFFC0; border-style: solid; margin:1em; width:90%;"}
            )
            
            # Parse orientation
            orientation = bs.find("td", string="Rs_StabilizedOrientation")
            if orientation:
                plus = orientation.parent.find("td", string="plus")
                minus = orientation.parent.find("td", string="minus")
                if plus:
                    entry_data["StabilizedOrientation"] = "plus"
                elif minus:
                    entry_data["StabilizedOrientation"] = "minus"
            else:
                link = bs.find("a", {"title": "StabilizedOrientation"})
                if link:
                    table_row = link.parent.parent
                    plus = table_row.find("td", string="plus")
                    minus = table_row.find("td", string="minus")
                    if plus:
                        entry_data["StabilizedOrientation"] = "plus"
                    elif minus:
                        entry_data["StabilizedOrientation"] = "minus"
            
            # Parse description
            if description:
                desc_data = self._parse_table(description)
                if desc_data and len(desc_data) > 0 and len(desc_data[0]) > 0:
                    entry_data["Description"] = desc_data[0][0]
            
            # Parse variations
            if table:
                var_data = self._parse_table(table)
                if var_data and len(var_data) > 1:
                    entry_data["Variations"] = var_data[1:]
            
            self.rsid_info[rsid.lower()] = entry_data
            return entry_data
            
        except Exception as e:
            logger.error(f"Error parsing page for {rsid}: {e}")
            return None
    
    def _parse_table(self, table) -> List[List[str]]:
        """Parse HTML table to list."""
        try:
            if not table:
                return []
            
            rows = table.find_all("tr")
            if not rows:
                return []
            
            data = []
            for row in rows:
                try:
                    cols = row.find_all("td")
                    if cols:
                        cols = [ele.text.strip() for ele in cols if ele]
                        filtered = [ele for ele in cols if ele]
                        if filtered:
                            data.append(filtered)
                except Exception as e:
                    logger.debug(f"Error parsing table row: {e}")
                    continue
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing table: {e}")
            return []
    
    def _export_results(self):
        """Export current results."""
        from SNPedia.utils.file_utils import export_to_file
        if self.rsid_info:
            export_to_file(data=self.rsid_info, filename="results.json")
            logger.info(f"Exported {len(self.rsid_info)} entries")