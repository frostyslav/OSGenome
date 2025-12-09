import argparse
import json
import os

import requests
from SNPedia.core.logger import logger
from typing_extensions import Self
from SNPedia.utils.file_utils import export_to_file
from SNPedia.core.config import get_config

# Load configuration
config = get_config()

# Configuration values
MAX_FILE_SIZE = config.MAX_FILE_SIZE_IMPORT
MAX_LINE_COUNT = config.MAX_LINE_COUNT
REQUEST_TIMEOUT = config.REQUEST_TIMEOUT
MAX_RETRIES = config.MAX_RETRIES
RETRY_DELAY = config.RETRY_DELAY
SNPEDIA_API_URL = config.SNPEDIA_API_URL


class PersonalData:
    def __init__(self: Self, file_path: str) -> None:
        # Validate file path
        if not file_path or not isinstance(file_path, str):
            raise ValueError("Invalid file path provided")
        
        # Check file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file size (prevent loading huge files)
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (max {MAX_FILE_SIZE})")
        
        # Check file is readable
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {file_path}")
        
        self.read_data(file_path)
        self.export()

    def read_data(self: Self, file_path: str) -> None:
        """Read and parse genetic data file with validation."""
        relevant_data = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                line_count = 0
                for line in file:
                    line_count += 1
                    
                    # Safety limit on number of lines
                    if line_count > MAX_LINE_COUNT:
                        logger.warning(f"File exceeds {MAX_LINE_COUNT} lines, truncating")
                        break
                    
                    # Skip comments and headers
                    if line.startswith("#") or line.startswith("rsid"):
                        continue
                    
                    # Basic validation - line should have content
                    stripped = line.strip()
                    if stripped:
                        relevant_data.append(stripped)
        except UnicodeDecodeError:
            logger.error(f"File encoding error in {file_path}")
            raise ValueError("File must be UTF-8 encoded")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise

        # crawl SNPedia for the available RSIDs
        snpedia_rsids = SNPediaRSIDs()
        known_rsids = dict(
            zip(snpedia_rsids.known, [i for i in range(len(snpedia_rsids.known))])
        )  # use dict for faster lookups

        personal_data = []
        # split lines into separate items
        for line in relevant_data:
            personal_data.append(line.split("\t"))

        self.personal_data = []
        # we will work only with rsids that exist both in personal raw and inside snpedia
        for item in personal_data:
            if not item or len(item) == 0:
                continue
            snp = item[0]
            if snp.lower() in known_rsids:
                self.personal_data.append(item)

        self.snps = {}
        for item in self.personal_data:
            if len(item) < 1:
                continue
            
            rsid = item[0]
            
            # Validate rsid format (should start with 'rs' or 'i')
            if not (rsid.lower().startswith('rs') or rsid.lower().startswith('i')):
                logger.warning(f"Skipping invalid rsid format: {rsid}")
                continue
            
            if len(item) > 4:
                allele1 = item[3].strip() if len(item[3].strip()) <= 10 else '-'
                allele2 = item[4].strip() if len(item[4].strip()) <= 10 else '-'
                
                # Validate alleles (should be single nucleotides or '-')
                valid_alleles = {'A', 'T', 'C', 'G', '-', 'I', 'D'}
                if allele1.upper() not in valid_alleles:
                    allele1 = '-'
                if allele2.upper() not in valid_alleles:
                    allele2 = '-'
                
                self.snps[rsid] = "({};{})".format(allele1, allele2)

    def hasGenotype(self: Self, rsid: str) -> bool:
        genotype = self.snps[rsid]
        return not genotype == "(-;-)"

    def export(self: Self) -> None:
        export_to_file(data=self.snps, filename="personal_snps.json")


class SNPediaRSIDs:
    def __init__(self: Self) -> None:
        if not self.last_session_exists():
            self.crawl()
            self.export()
        else:
            self.load()

    def load(self: Self) -> None:
        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir

        filepath = os.path.join(joiner, "data", "snpedia_snps.json")
        with open(filepath) as f:
            self.known = json.load(f)

    def last_session_exists(self: Self) -> None:
        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir

        filepath = os.path.join(joiner, "data", "snpedia_snps.json")
        return os.path.isfile(filepath)

    def crawl(self: Self, cmcontinue: str = None) -> None:
        """Crawl SNPedia API for known SNPs with error handling."""
        count = 0
        self.known = []

        category_member_limit = 500
        snpedia_initial_url = f"{SNPEDIA_API_URL}?action=query&list=categorymembers&cmtitle=Category:Is_a_snp&cmlimit={category_member_limit}&format=json"

        logger.info("Grabbing known SNPs from SNPedia")
        
        # Initial request
        if not cmcontinue:
            for attempt in range(MAX_RETRIES):
                try:
                    curgen = snpedia_initial_url
                    response = requests.get(curgen, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    jd = response.json()

                    if "query" not in jd or "categorymembers" not in jd["query"]:
                        logger.error("Unexpected API response format")
                        return

                    cur = jd["query"]["categorymembers"]
                    for item in cur:
                        if "title" in item:
                            self.known.append(item["title"].lower())
                    
                    if "continue" in jd and "cmcontinue" in jd["continue"]:
                        cmcontinue = jd["continue"]["cmcontinue"]
                    else:
                        logger.info(f"Retrieved {len(self.known)} SNPs from SNPedia")
                        return
                    break
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"Request timeout on attempt {attempt + 1}/{MAX_RETRIES}")
                    if attempt < MAX_RETRIES - 1:
                        import time
                        time.sleep(RETRY_DELAY)
                    else:
                        logger.error("Failed to fetch SNPs after multiple timeouts")
                        return
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"Network error fetching SNPs: {e}")
                    if attempt < MAX_RETRIES - 1:
                        import time
                        time.sleep(RETRY_DELAY)
                    else:
                        return
                        
                except (KeyError, ValueError, json.JSONDecodeError) as e:
                    logger.error(f"Error parsing SNPedia response: {e}")
                    return

        # Continue fetching pages
        while cmcontinue:
            for attempt in range(MAX_RETRIES):
                try:
                    curgen = "{}&cmcontinue={}".format(snpedia_initial_url, cmcontinue)
                    response = requests.get(curgen, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    jd = response.json()
                    
                    if "query" not in jd or "categorymembers" not in jd["query"]:
                        logger.error("Unexpected API response format")
                        return
                    
                    cur = jd["query"]["categorymembers"]
                    for item in cur:
                        if "title" in item:
                            self.known.append(item["title"].lower())
                    
                    try:
                        cmcontinue = jd["continue"]["cmcontinue"]
                    except KeyError:
                        cmcontinue = None
                    
                    count += 1
                    if count % 10 == 0:
                        logger.info(f"Retrieved {len(self.known)} SNPs so far...")
                    break
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"Request timeout on page {count}, attempt {attempt + 1}/{MAX_RETRIES}")
                    if attempt < MAX_RETRIES - 1:
                        import time
                        time.sleep(RETRY_DELAY)
                    else:
                        logger.warning(f"Stopping after {len(self.known)} SNPs due to timeouts")
                        return
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"Network error on page {count}: {e}")
                    if attempt < MAX_RETRIES - 1:
                        import time
                        time.sleep(RETRY_DELAY)
                    else:
                        logger.warning(f"Stopping after {len(self.known)} SNPs due to network errors")
                        return
                        
                except (KeyError, ValueError, json.JSONDecodeError) as e:
                    logger.error(f"Error parsing response on page {count}: {e}")
                    return
        
        logger.info(f"Successfully retrieved {len(self.known)} SNPs from SNPedia")

    def export(self: Self) -> None:
        export_to_file(data=self.known, filename="snpedia_snps.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import and process genetic data from raw files"
    )
    parser.add_argument(
        "-f",
        "--filepath",
        help="Filepath for genetic data file to be imported",
        required=False,
    )

    try:
        args = vars(parser.parse_args())

        if args["filepath"]:
            try:
                logger.info(f"Importing genetic data from: {args['filepath']}")
                pd = PersonalData(file_path=args["filepath"])
                
                if not pd.snps:
                    logger.warning("No SNPs found in the file")
                else:
                    logger.info(
                        "Number of SNPs in the raw data that correlate to SNPedia: {}".format(
                            len(pd.snps)
                        )
                    )
                    logger.info("Import completed successfully")
                    
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
                logger.error(f"Error importing genetic data: {e}")
                exit(1)
        else:
            logger.error("No filepath provided. Use -f or --filepath to specify a file")
            parser.print_help()
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("Import interrupted by user")
        exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)
