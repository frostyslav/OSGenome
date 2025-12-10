import argparse
import asyncio
import json
import time
import urllib.request
from typing import Optional
from urllib.error import HTTPError, URLError

import aiohttp
from bs4 import BeautifulSoup
from SNPedia.genome_importer import PersonalData
from SNPedia.core.logger import logger
from typing_extensions import Self
from SNPedia.utils.file_utils import export_to_file, load_from_file
from SNPedia.core.config import get_config

# Load configuration
config = get_config()

# Rate limiting configuration from config
REQUEST_DELAY = config.REQUEST_DELAY
MAX_RETRIES = config.MAX_RETRIES
RETRY_DELAY = config.RETRY_DELAY
REQUEST_TIMEOUT = config.REQUEST_TIMEOUT
SAVE_PROGRESS_INTERVAL = config.SAVE_PROGRESS_INTERVAL
SNPEDIA_INDEX_URL = config.SNPEDIA_INDEX_URL


class SNPCrawl:
    def __init__(self: Self, rsid_file: str = None, snp_file: str = None):
        self.rsid_info = load_from_file(filename=rsid_file)
        self.personal_snps = load_from_file(filename=snp_file)
        self.rsid_list = []
        self.enriched_snps = {}
        self.common_words = [
            "common",
            "very common",
            "most common",
            "normal",
            "average",
            "miscall in ancestry",
            "ancestry miscall",
            "miscall by ancestry",
        ]

        if self.personal_snps:
            self.init_crawl(self.personal_snps)
            self.export()
            self.create_list()
        else:
            logger.error("No SNPs to crawl")

    def init_crawl(self: Self, rsids: dict, use_async: bool = True):
        """Initialize crawl using async or sync implementation.
        
        Args:
            rsids: Dictionary of RSIDs to crawl
            use_async: If True, use async implementation (default). If False, use sync.
        """
        if use_async:
            logger.info("Using async crawl implementation")
            asyncio.run(self.async_crawl(rsids))
        else:
            logger.info("Using synchronous crawl implementation")
            self.sync_crawl(rsids)
    
    def sync_crawl(self: Self, rsids: dict):
        """Synchronous crawl implementation (original behavior)."""
        count = 0
        delay_count = 0
        self.delay_count = 0

        for rsid in rsids.keys():
            if rsid not in self.rsid_info.keys():
                delay_count += 1
            
            # Add rate limiting delay before each request
            time.sleep(REQUEST_DELAY)
            self.grab_table(rsid)
            
            count += 1
            if count > 0 and count % 10 == 0:
                logger.info("%i out of %s completed" % (count, len(rsids)))
            
            # Export intermediate results and add longer delay
            if (
                delay_count > 0
                and delay_count % SAVE_PROGRESS_INTERVAL == 0
                and delay_count != self.delay_count
            ):
                self.delay_count = delay_count
                logger.info("Exporting intermediate results...")
                self.export()
                self.create_list()
                logger.info(f"Sleeping for {RETRY_DELAY * 3} seconds...")
                time.sleep(RETRY_DELAY * 3)
        logger.info("Done")

    async def async_crawl(self: Self, rsids: dict):
        """Async crawl implementation with concurrent requests and rate limiting."""
        # Calculate concurrent requests based on delay - more conservative
        # Lower concurrency to reduce server load and avoid 502 errors
        max_concurrent = max(3, min(5, int(5 * REQUEST_DELAY)))
        semaphore = asyncio.Semaphore(max_concurrent)
        
        rsids_to_fetch = [rsid for rsid in rsids.keys() if rsid not in self.rsid_info.keys()]
        total_rsids = len(rsids)
        new_rsids = len(rsids_to_fetch)
        
        logger.info(f"Starting async crawl: {new_rsids} new RSIDs out of {total_rsids} total")
        logger.info(f"Using {max_concurrent} concurrent requests with {REQUEST_DELAY}s delay")
        logger.info(f"Estimated time: ~{(new_rsids * REQUEST_DELAY / max_concurrent):.0f} seconds")
        
        # Create session with timeout
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = []
            for rsid in rsids.keys():
                task = self.fetch_rsid_with_semaphore(session, rsid, semaphore)
                tasks.append(task)
            
            # Process with progress tracking
            completed = 0
            
            for coro in asyncio.as_completed(tasks):
                await coro
                completed += 1
                
                if completed % 10 == 0:
                    logger.info(f"{completed} out of {total_rsids} completed")
                
                # Export intermediate results periodically
                if completed > 0 and completed % SAVE_PROGRESS_INTERVAL == 0:
                    logger.info("Exporting intermediate results...")
                    self.export()
                    self.create_list()
        
        logger.info("Done")
    
    async def fetch_rsid_with_semaphore(
        self: Self, session: aiohttp.ClientSession, rsid: str, semaphore: asyncio.Semaphore
    ):
        """Fetch RSID with semaphore-based rate limiting."""
        async with semaphore:
            await self.grab_table_async(session, rsid)
            # Add delay between requests to respect rate limits
            await asyncio.sleep(REQUEST_DELAY)
    
    async def grab_table_async(
        self: Self, session: aiohttp.ClientSession, rsid: str
    ) -> Optional[dict]:
        """Async version of grab_table with retry logic."""
        # Validate rsid format
        if not rsid or not isinstance(rsid, str):
            logger.error(f"Invalid rsid format: {rsid}")
            return None
        
        # Skip if already fetched
        if rsid in self.rsid_info.keys():
            return self.rsid_info[rsid]
        
        url = f"{SNPEDIA_INDEX_URL}/{rsid}"
        logger.info(f"Grabbing data about SNP: {rsid}")
        
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url) as response:
                    if response.status == 404:
                        logger.warning(f"{rsid} not found (404)")
                        return None
                    
                    # Handle rate limiting
                    if response.status == 429:
                        backoff = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limited (429) on attempt {attempt + 1}/{MAX_RETRIES}, waiting {backoff}s")
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(backoff)
                            continue
                        else:
                            logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts (rate limited)")
                            return None
                    
                    # Handle server errors (502, 503, 504)
                    if response.status in (502, 503, 504):
                        backoff = RETRY_DELAY * (2 ** attempt)
                        logger.warning(f"Server error ({response.status}) for {rsid} on attempt {attempt + 1}/{MAX_RETRIES}, waiting {backoff}s")
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(backoff)
                            continue
                        else:
                            logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts (server error {response.status})")
                            return None
                    
                    response.raise_for_status()
                    html = await response.text()
                    
                    # Parse HTML
                    bs = BeautifulSoup(html, "html.parser")
                    
                    self.rsid_info[rsid.lower()] = {
                        "Description": "",
                        "Variations": [],
                        "StabilizedOrientation": "",
                    }
                    
                    table = bs.find("table", {"class": "sortable smwtable"})
                    description = bs.find(
                        "table",
                        {
                            "style": "border: 1px; background-color: #FFFFC0; border-style: solid; margin:1em; width:90%;"
                        },
                    )

                    # Orientation Finder
                    orientation = bs.find("td", string="Rs_StabilizedOrientation")
                    if orientation:
                        plus = orientation.parent.find("td", string="plus")
                        minus = orientation.parent.find("td", string="minus")
                        if plus:
                            self.rsid_info[rsid]["StabilizedOrientation"] = "plus"
                        if minus:
                            self.rsid_info[rsid]["StabilizedOrientation"] = "minus"
                    else:
                        link = bs.find("a", {"title": "StabilizedOrientation"})
                        if link:
                            table_row = link.parent.parent
                            plus = table_row.find("td", string="plus")
                            minus = table_row.find("td", string="minus")
                            if plus:
                                self.rsid_info[rsid]["StabilizedOrientation"] = "plus"
                            if minus:
                                self.rsid_info[rsid]["StabilizedOrientation"] = "minus"

                    logger.debug(
                        "{} stabilized orientation: {}".format(
                            rsid, self.rsid_info[rsid]["StabilizedOrientation"]
                        )
                    )

                    if description:
                        d1 = self.table_to_list(description)
                        self.rsid_info[rsid]["Description"] = d1[0][0]
                        logger.debug(
                            "{} description: {}".format(
                                rsid, self.rsid_info[rsid]["Description"]
                            )
                        )
                    if table:
                        d2 = self.table_to_list(table)
                        self.rsid_info[rsid]["Variations"] = d2[1:]
                        logger.debug(
                            "{} variations: {}".format(
                                rsid, self.rsid_info[rsid]["Variations"]
                            )
                        )
                    
                    return self.rsid_info[rsid]
                    
            except aiohttp.ClientError as e:
                logger.error(f"Network error for {rsid}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts")
                    
            except asyncio.TimeoutError:
                logger.error(f"Timeout fetching {rsid}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts")
                    
            except Exception as e:
                logger.error(f"Unexpected error fetching {rsid}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts")
        
        return None

    def grab_table(self: Self, rsid: str):  # noqa C901
        """Fetch SNP data from SNPedia with retry logic and error handling."""
        # Validate rsid format
        if not rsid or not isinstance(rsid, str):
            logger.error(f"Invalid rsid format: {rsid}")
            return
        
        url = f"{SNPEDIA_INDEX_URL}/{rsid}"
        
        if rsid in self.rsid_info.keys():
            return
        
        logger.info(f"Grabbing data about SNP: {rsid}")
        
        for attempt in range(MAX_RETRIES):
            try:
                # Set timeout to prevent hanging
                response = urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT)
                html = response.read()
                bs = BeautifulSoup(html, "html.parser")
                
                self.rsid_info[rsid.lower()] = {
                    "Description": "",
                    "Variations": [],
                    "StabilizedOrientation": "",
                }
                table = bs.find("table", {"class": "sortable smwtable"})
                description = bs.find(
                    "table",
                    {
                        "style": "border: 1px; background-color: #FFFFC0; border-style: solid; margin:1em; width:90%;"
                    },
                )

                # Orientation Finder
                orientation = bs.find("td", string="Rs_StabilizedOrientation")
                if orientation:
                    plus = orientation.parent.find("td", string="plus")
                    minus = orientation.parent.find("td", string="minus")
                    if plus:
                        self.rsid_info[rsid]["StabilizedOrientation"] = "plus"
                    if minus:
                        self.rsid_info[rsid]["StabilizedOrientation"] = "minus"
                else:
                    link = bs.find("a", {"title": "StabilizedOrientation"})
                    if link:
                        table_row = link.parent.parent
                        plus = table_row.find("td", string="plus")
                        minus = table_row.find("td", string="minus")
                        if plus:
                            self.rsid_info[rsid]["StabilizedOrientation"] = "plus"
                        if minus:
                            self.rsid_info[rsid]["StabilizedOrientation"] = "minus"

                logger.debug(
                    "{} stabilized orientation: {}".format(
                        rsid, self.rsid_info[rsid]["StabilizedOrientation"]
                    )
                )

                if description:
                    d1 = self.table_to_list(description)
                    self.rsid_info[rsid]["Description"] = d1[0][0]
                    logger.debug(
                        "{} description: {}".format(
                            rsid, self.rsid_info[rsid]["Description"]
                        )
                    )
                if table:
                    d2 = self.table_to_list(table)
                    self.rsid_info[rsid]["Variations"] = d2[1:]
                    logger.debug(
                        "{} variations: {}".format(
                            rsid, self.rsid_info[rsid]["Variations"]
                        )
                    )
                
                # Success - break retry loop
                break
                
            except HTTPError as e:
                if e.code == 404:
                    logger.warning(f"{rsid} not found (404)")
                    break  # Don't retry 404s
                elif e.code == 429:
                    logger.warning(f"Rate limited (429) on attempt {attempt + 1}/{MAX_RETRIES}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
                    else:
                        logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts (rate limited)")
                else:
                    logger.error(f"HTTP error {e.code} for {rsid}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                    
            except URLError as e:
                logger.error(f"Network error for {rsid}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts")
                    
            except Exception as e:
                logger.error(f"Unexpected error fetching {rsid}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Failed to fetch {rsid} after {MAX_RETRIES} attempts")

    def table_to_list(self: Self, table):
        """Parse HTML table to list with error handling."""
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
                        # Only add non-empty rows
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

    def flip_alleles(
        self: Self, rsid: str, genotype: str, stabilized_orientation: str
    ) -> dict:
        if stabilized_orientation == "minus" and genotype != "":
            original_genotype = genotype
            modified_genotype = [None] * 2

            for i, allele in enumerate(original_genotype.strip("()").split(";")):
                if allele == "A":
                    modified_genotype[i] = "T"
                    continue
                if allele == "T":
                    modified_genotype[i] = "A"
                    continue
                if allele == "C":
                    modified_genotype[i] = "G"
                    continue
                if allele == "G":
                    modified_genotype[i] = "C"
                    continue
                modified_genotype[i] = allele
            updated_genotype = "({};{})".format(
                modified_genotype[0], modified_genotype[1]
            )
            self.enriched_snps[rsid.lower()] = updated_genotype
            return {"genotype": updated_genotype, "flipped": True}
        else:
            self.enriched_snps[rsid.lower()] = genotype
            return {"genotype": genotype, "flipped": False}

    def create_entry(
        self: Self,
        rsid: str,
        description: str,
        variations: list,
        stabilized_orientation: str,
        is_flipped: bool,
        is_interesting: bool,
        is_uncommon: bool,
    ) -> dict:
        genotype = ""
        if rsid.lower() in self.enriched_snps.keys():
            genotype = self.personal_snps[rsid.lower()]
            if is_flipped:
                genotype += "<br><i>flipped<br>{}</i>".format(
                    self.enriched_snps[rsid.lower()]
                )
        else:
            genotype = "(-;-)"

        return {
            "Name": rsid,
            "Description": description,
            "Genotype": str(genotype),
            "Variations": str.join("<br>", variations),
            "StabilizedOrientation": stabilized_orientation,
            "IsInteresting": "Yes" if is_interesting else "No",
            "IsUncommon": "Yes" if is_uncommon else "No",
        }

    def format_cell(
        self: Self, rsid: str, variation: list, stabilized_orientation: str
    ) -> str:
        genotype = variation[0]
        if (
            rsid.lower() in self.enriched_snps.keys()
            and self.enriched_snps[rsid.lower()] == genotype
            # and stabilized_orientation == "plus"
        ):
            return "<b>" + str.join(" ", variation) + "</b>"
        else:
            return str.join(" ", variation)

    def is_interesting(self: Self, variation: list) -> bool:
        if len(variation) > 2 and not variation[2].lower().startswith(
            tuple(self.common_words)
        ):
            return True

        return False

    def is_uncommon(self: Self, rsid: str, variation: list) -> bool:
        if (
            rsid.lower() in self.enriched_snps.keys()
            and self.enriched_snps[rsid.lower()] == variation[0]
            and len(variation) > 2
            and not variation[2].lower().startswith(tuple(self.common_words))
            and "common in clinvar" not in variation[2].lower()
        ):
            return True

        return False

    def create_list(self: Self):
        """Create final list of SNP entries with error handling."""
        self.rsid_list = []
        messaged_once = False
        errors = 0
        
        for rsid, values in self.rsid_info.items():
            try:
                # Validate rsid exists in personal SNPs
                if rsid.lower() not in self.personal_snps:
                    logger.debug(f"Skipping {rsid} - not in personal SNPs")
                    continue
                
                self.enriched_snps[rsid.lower()] = self.personal_snps[rsid.lower()]
                
                # Handle orientation
                if "StabilizedOrientation" in values:
                    stbl_orient = values["StabilizedOrientation"]
                    try:
                        flipped_data = self.flip_alleles(
                            rsid=rsid.lower(),
                            genotype=self.personal_snps[rsid.lower()],
                            stabilized_orientation=stbl_orient,
                        )
                    except Exception as e:
                        logger.error(f"Error flipping alleles for {rsid}: {e}")
                        flipped_data = {"genotype": self.personal_snps[rsid.lower()], "flipped": False}
                else:
                    stbl_orient = "Old Data Format"
                    flipped_data = {"genotype": self.personal_snps[rsid.lower()], "flipped": False}
                    if not messaged_once:
                        logger.warning(
                            "Old Data Detected, Will not display variations bolding with old data."
                        )
                        logger.warning("See ReadMe for more details")
                        messaged_once = True

                # Check if interesting
                interesting_snp = False
                if "Variations" in values and isinstance(values["Variations"], list):
                    for variation in values["Variations"]:
                        try:
                            if self.is_interesting(variation):
                                interesting_snp = True
                                break
                        except Exception as e:
                            logger.debug(f"Error checking if interesting for {rsid}: {e}")

                # Check if uncommon
                uncommon_snp = False
                if "Variations" in values and isinstance(values["Variations"], list):
                    for variation in values["Variations"]:
                        try:
                            if self.is_uncommon(rsid, variation):
                                uncommon_snp = True
                                break
                        except Exception as e:
                            logger.debug(f"Error checking if uncommon for {rsid}: {e}")

                # Format variations
                variations = []
                if "Variations" in values and isinstance(values["Variations"], list):
                    for variation in values["Variations"]:
                        try:
                            formatted = self.format_cell(rsid, variation, stbl_orient)
                            variations.append(formatted)
                        except Exception as e:
                            logger.debug(f"Error formatting variation for {rsid}: {e}")

                # Create entry
                try:
                    description = values.get("Description", "")
                    maker = self.create_entry(
                        rsid,
                        description,
                        variations,
                        stbl_orient,
                        flipped_data["flipped"],
                        interesting_snp,
                        uncommon_snp,
                    )
                    self.rsid_list.append(maker)
                except Exception as e:
                    logger.error(f"Error creating entry for {rsid}: {e}")
                    errors += 1
                    
            except Exception as e:
                logger.error(f"Unexpected error processing {rsid}: {e}")
                errors += 1
                continue

        if errors > 0:
            logger.warning(f"Encountered {errors} errors while creating list")
        
        logger.info(f"Created list with {len(self.rsid_list)} entries")
        
        # Export with error handling
        if not export_to_file(data=self.rsid_list, filename="result_table.json"):
            logger.error("Failed to export result table")
        else:
            logger.info("Successfully exported result table")
            
        # Log sample for debugging
        if self.rsid_list:
            try:
                logger.debug(json.dumps(self.rsid_list[:5], indent=2))
            except Exception as e:
                logger.debug(f"Could not log sample data: {e}")

    def export(self: Self):
        """Export rsid info with error handling."""
        try:
            if not self.rsid_info:
                logger.warning("No rsid info to export")
                return False
            
            if export_to_file(data=self.rsid_info, filename="results.json"):
                logger.info(f"Exported {len(self.rsid_info)} rsid entries")
                return True
            else:
                logger.error("Failed to export rsid info")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error during export: {e}")
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawl SNPedia for genetic data information"
    )

    parser.add_argument(
        "-f",
        "--filepath",
        help="Filepath for Ancestry raw data to be used for import",
        required=False,
    )

    try:
        args = vars(parser.parse_args())

        if args["filepath"]:
            try:
                logger.info(f"Processing genetic data from: {args['filepath']}")
                personal = PersonalData(args["filepath"])
                
                if not personal.snps:
                    logger.error("No SNPs found in the provided file")
                    exit(1)
                
                snps_of_interest = {}
                for rsid, gene in personal.snps.items():
                    try:
                        if personal.hasGenotype(rsid):
                            snps_of_interest[rsid] = gene
                    except Exception as e:
                        logger.debug(f"Error checking genotype for {rsid}: {e}")
                        continue
                
                logger.info(
                    "Found {} SNPs to be mapped to SNPedia".format(len(snps_of_interest))
                )
                
                if not snps_of_interest:
                    logger.error("No valid SNPs found to process")
                    exit(1)
                    
            except FileNotFoundError as e:
                logger.error(f"File not found: {e}")
                exit(1)
            except ValueError as e:
                logger.error(f"Invalid file: {e}")
                exit(1)
            except PermissionError as e:
                logger.error(f"Permission denied: {e}")
                exit(1)
            except Exception as e:
                logger.error(f"Error processing genetic data: {e}")
                exit(1)

        try:
            logger.info("Starting SNPedia crawl...")
            crawler = SNPCrawl(rsid_file="results.json", snp_file="personal_snps.json")
            logger.info("Crawl completed successfully")
            
        except Exception as e:
            logger.error(f"Error during SNPedia crawl: {e}")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("Crawl interrupted by user")
        exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)
