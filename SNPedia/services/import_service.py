"""Service for importing genetic data from files."""

import json
import os
from typing import Dict, Optional

import requests

from SNPedia.core.config import get_config
from SNPedia.core.logger import logger
from SNPedia.models.snp_models import PersonalGenome, SNPData
from SNPedia.utils.file_utils import export_to_file


class ImportService:
    """Service for importing and processing genetic data files."""

    def __init__(self) -> None:
        """Initialize the import service.

        Sets up configuration for genetic data file processing
        and validation operations.
        """
        self.config = get_config()

    def has_existing_data(self) -> bool:
        """Check if personal genome data already exists."""
        data_file = "data/personal_snps.json"

        # Check if file exists and has content
        if os.path.exists(data_file):
            try:
                with open(data_file) as f:
                    data = json.load(f)
                    if data and len(data) > 0:
                        logger.info(f"Found existing data with {len(data)} SNPs")
                        return True
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Existing data file is corrupted: {e}")
                return False

        return False

    def import_genome_file(self, file_path: str) -> Optional[PersonalGenome]:
        """Import genome data from file and return PersonalGenome object."""
        try:
            # Validate file path
            if not file_path or not isinstance(file_path, str):
                raise ValueError("Invalid file path provided")

            # Check file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Check file size (prevent loading huge files)
            file_size = os.path.getsize(file_path)
            if file_size > self.config.MAX_FILE_SIZE_IMPORT:
                raise ValueError(
                    f"File too large: {file_size} bytes (max {self.config.MAX_FILE_SIZE_IMPORT})"
                )

            # Check file is readable
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"Cannot read file: {file_path}")

            # Read and parse the file
            snps = self._parse_genetic_file(file_path)

            if not snps:
                logger.warning("No valid SNPs found in file")
                return None

            # Create PersonalGenome object
            genome = PersonalGenome(snps=snps)

            # Export to JSON for compatibility with existing system
            snp_dict = {rsid: snp.genotype for rsid, snp in snps.items()}
            export_to_file(data=snp_dict, filename="personal_snps.json")

            logger.info(f"Successfully imported {len(snps)} SNPs")
            return genome

        except Exception as e:
            logger.error(f"Error importing genome file: {e}")
            raise

    def _parse_genetic_file(self, file_path: str) -> Dict[str, SNPData]:
        """Parse genetic data file and return SNP dictionary."""
        relevant_data = []

        try:
            with open(file_path, encoding="utf-8") as file:
                line_count = 0
                for line in file:
                    line_count += 1

                    # Safety limit on number of lines
                    if line_count > self.config.MAX_LINE_COUNT:
                        logger.warning(
                            f"File exceeds {self.config.MAX_LINE_COUNT} lines, truncating"
                        )
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

        # Get known RSIDs from SNPedia
        known_rsids = self._get_known_rsids()
        known_rsids_dict = dict(zip(known_rsids, range(len(known_rsids))))

        # Parse lines into SNP data
        personal_data = []
        for line in relevant_data:
            personal_data.append(line.split("\t"))

        # Filter to only known RSIDs
        filtered_data = []
        for item in personal_data:
            if not item or len(item) == 0:
                continue
            snp = item[0]
            if snp.lower() in known_rsids_dict:
                filtered_data.append(item)

        # Convert to SNPData objects
        snps = {}
        for item in filtered_data:
            if len(item) < 1:
                continue

            rsid = item[0]

            # Validate rsid format (should start with 'rs' or 'i')
            if not (rsid.lower().startswith("rs") or rsid.lower().startswith("i")):
                logger.warning(f"Skipping invalid rsid format: {rsid}")
                continue

            if len(item) > 4:
                allele1 = item[3].strip() if len(item[3].strip()) <= 10 else "-"
                allele2 = item[4].strip() if len(item[4].strip()) <= 10 else "-"

                # Validate alleles (should be single nucleotides or '-')
                valid_alleles = {"A", "T", "C", "G", "-", "I", "D"}
                if allele1.upper() not in valid_alleles:
                    allele1 = "-"
                if allele2.upper() not in valid_alleles:
                    allele2 = "-"

                genotype = f"({allele1};{allele2})"
                snps[rsid] = SNPData(rsid=rsid, genotype=genotype)

        return snps

    def _get_known_rsids(self) -> list:
        """Get known RSIDs from SNPedia or cached file."""
        # Try to load from existing file first
        if os.path.exists("SNPedia/data/snpedia_snps.json"):
            try:
                with open("SNPedia/data/snpedia_snps.json") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading cached SNPedia RSIDs: {e}")

        # If no cached file, fetch from SNPedia API
        logger.info("Fetching known SNPs from SNPedia API...")
        return self._fetch_snpedia_rsids()

    def _fetch_snpedia_rsids(self) -> list:
        """Fetch known RSIDs from SNPedia API."""
        known_rsids = []
        category_member_limit = 500
        snpedia_initial_url = f"{self.config.SNPEDIA_API_URL}?action=query&list=categorymembers&cmtitle=Category:Is_a_snp&cmlimit={category_member_limit}&format=json"

        cmcontinue = None
        count = 0

        try:
            while True:
                # Build URL
                if cmcontinue:
                    url = f"{snpedia_initial_url}&cmcontinue={cmcontinue}"
                else:
                    url = snpedia_initial_url

                # Make request with retry logic
                for attempt in range(self.config.MAX_RETRIES):
                    try:
                        response = requests.get(
                            url, timeout=self.config.REQUEST_TIMEOUT
                        )
                        response.raise_for_status()
                        data = response.json()

                        if (
                            "query" not in data
                            or "categorymembers" not in data["query"]
                        ):
                            logger.error("Unexpected API response format")
                            break

                        # Extract RSIDs
                        for item in data["query"]["categorymembers"]:
                            if "title" in item:
                                known_rsids.append(item["title"].lower())

                        # Check for continuation
                        if "continue" in data and "cmcontinue" in data["continue"]:
                            cmcontinue = data["continue"]["cmcontinue"]
                        else:
                            cmcontinue = None

                        count += 1
                        if count % 10 == 0:
                            logger.info(f"Retrieved {len(known_rsids)} SNPs so far...")

                        break  # Success, exit retry loop

                    except requests.exceptions.Timeout:
                        logger.warning(
                            f"Request timeout on attempt {attempt + 1}/{self.config.MAX_RETRIES}"
                        )
                        if attempt < self.config.MAX_RETRIES - 1:
                            import time

                            time.sleep(self.config.RETRY_DELAY)
                        else:
                            logger.warning(
                                f"Stopping after {len(known_rsids)} SNPs due to timeouts"
                            )
                            cmcontinue = None
                            break

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Network error: {e}")
                        if attempt < self.config.MAX_RETRIES - 1:
                            import time

                            time.sleep(self.config.RETRY_DELAY)
                        else:
                            logger.warning(
                                f"Stopping after {len(known_rsids)} SNPs due to network errors"
                            )
                            cmcontinue = None
                            break

                if not cmcontinue:
                    break

            logger.info(f"Successfully retrieved {len(known_rsids)} SNPs from SNPedia")

            # Cache the results
            export_to_file(data=known_rsids, filename="snpedia_snps.json")

            return known_rsids

        except Exception as e:
            logger.error(f"Error fetching SNPedia RSIDs: {e}")
            return []
