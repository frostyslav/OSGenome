"""Service layer for SNP-related business logic.

This module provides the main service layer for Single Nucleotide Polymorphism (SNP)
operations, including data retrieval, processing, and enrichment with SNPedia information.

The service acts as an intermediary between the API layer and data repositories,
implementing business logic for genetic data analysis and processing.

Example:
    Basic usage:
        >>> service = SNPService()
        >>> snp_data = service.get_snp_data("rs1234567")
        >>> if snp_data:
        ...     print(f"Genotype: {snp_data.genotype}")

    Processing genome data:
        >>> enriched_snps = service.process_genome_data()
        >>> print(f"Processed {len(enriched_snps)} SNPs")
"""

from typing import Any, Dict, List, Optional

from SNPedia.core.logger import logger
from SNPedia.data.repositories import ResultRepository, SNPediaRepository, SNPRepository
from SNPedia.models.response_models import PaginatedResponse, StatisticsResponse
from SNPedia.models.snp_models import EnrichedSNP, PersonalGenome, SNPData, SNPediaEntry


class SNPService:
    """Service for SNP-related operations.

    This service provides high-level operations for working with SNP data,
    including retrieval, processing, and enrichment with SNPedia information.
    It coordinates between multiple repositories to provide comprehensive
    genetic data analysis capabilities.

    Attributes:
        snp_repo (SNPRepository): Repository for personal SNP data.
        snpedia_repo (SNPediaRepository): Repository for SNPedia reference data.
        result_repo (ResultRepository): Repository for processed results.
    """

    def __init__(self) -> None:
        """Initialize the SNP service with required repositories.

        Creates instances of all required repositories for data access.
        """
        self.snp_repo: SNPRepository = SNPRepository()
        self.snpedia_repo: SNPediaRepository = SNPediaRepository()
        self.result_repo: ResultRepository = ResultRepository()

    def get_snp_data(self, rsid: str) -> Optional[SNPData]:
        """Get SNP data by RSID.

        Retrieves personal SNP data for a specific Reference SNP ID (RSID)
        from the personal genome repository.

        Args:
            rsid (str): The Reference SNP ID to look up (e.g., "rs1234567").

        Returns:
            Optional[SNPData]: SNP data if found, None otherwise.

        Example:
            >>> service = SNPService()
            >>> snp = service.get_snp_data("rs1234567")
            >>> if snp:
            ...     print(f"Genotype: {snp.genotype}")
        """
        return self.snp_repo.get_by_id(rsid)

    def get_snpedia_data(self, rsid: str) -> Optional[SNPediaEntry]:
        """Get SNPedia reference data by RSID.

        Retrieves reference information from SNPedia for a specific RSID,
        including descriptions, variations, and clinical significance.

        Args:
            rsid (str): The Reference SNP ID to look up.

        Returns:
            Optional[SNPediaEntry]: SNPedia data if found, None otherwise.

        Example:
            >>> service = SNPService()
            >>> entry = service.get_snpedia_data("rs1234567")
            >>> if entry:
            ...     print(f"Description: {entry.description}")
        """
        return self.snpedia_repo.get_by_id(rsid)

    def get_enriched_snp(self, rsid: str) -> Optional[EnrichedSNP]:
        """Get enriched SNP data by RSID.

        Retrieves processed SNP data that combines personal genotype
        information with SNPedia reference data.

        Args:
            rsid (str): The Reference SNP ID to look up.

        Returns:
            Optional[EnrichedSNP]: Enriched SNP data if found, None otherwise.

        Example:
            >>> service = SNPService()
            >>> enriched = service.get_enriched_snp("rs1234567")
            >>> if enriched:
            ...     print(f"Is interesting: {enriched.is_interesting}")
        """
        return self.result_repo.get_by_id(rsid)

    def get_personal_genome(self) -> Optional[PersonalGenome]:
        """Get complete personal genome data.

        Retrieves the entire personal genome dataset containing all
        available SNP data for the individual.

        Returns:
            Optional[PersonalGenome]: Complete genome data if available, None otherwise.

        Example:
            >>> service = SNPService()
            >>> genome = service.get_personal_genome()
            >>> if genome:
            ...     print(f"Total SNPs: {genome.count_total()}")
        """
        return self.snp_repo.get_genome()

    def get_results_paginated(
        self, page: int = 1, page_size: int = 100
    ) -> PaginatedResponse:
        """Get paginated enriched SNP results.

        Retrieves a paginated subset of enriched SNP data, useful for
        displaying large datasets in manageable chunks.

        Args:
            page (int, optional): Page number to retrieve (1-indexed). Defaults to 1.
            page_size (int, optional): Number of results per page. Defaults to 100.

        Returns:
            PaginatedResponse: Paginated response containing data and metadata.

        Example:
            >>> service = SNPService()
            >>> results = service.get_results_paginated(page=2, page_size=50)
            >>> print(f"Page {results.page} of {results.total_pages}")
            >>> print(f"Showing {len(results.data)} of {results.total} results")
        """
        try:
            result = self.result_repo.get_paginated(page=page, page_size=page_size)

            return PaginatedResponse(
                data=result["data"],
                page=result["page"],
                page_size=result["page_size"],
                total=result["total"],
                total_pages=result["total_pages"],
                has_next=result["has_next"],
                has_prev=result["has_prev"],
            )
        except Exception as e:
            logger.error(f"Error getting paginated results: {e}")
            return PaginatedResponse(
                data=[],
                page=page,
                page_size=page_size,
                total=0,
                total_pages=0,
                has_next=False,
                has_prev=False,
            )

    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all enriched SNP results as dictionaries.

        Retrieves all processed SNP data and converts it to dictionary format
        suitable for JSON serialization and API responses.

        Returns:
            List[Dict[str, Any]]: List of SNP data dictionaries.

        Warning:
            This method loads all results into memory. For large datasets,
            consider using get_results_paginated() instead.

        Example:
            >>> service = SNPService()
            >>> all_results = service.get_all_results()
            >>> for snp_dict in all_results:
            ...     print(f"RSID: {snp_dict['Name']}")
        """
        try:
            enriched_snps = self.result_repo.get_all()
            return [snp.to_dict() for snp in enriched_snps]
        except Exception as e:
            logger.error(f"Error getting all results: {e}")
            return []

    def get_statistics(self) -> StatisticsResponse:
        """Get statistics about the genetic data."""
        try:
            stats = self.result_repo.get_statistics()
            return StatisticsResponse(
                total=stats["total"],
                interesting=stats["interesting"],
                uncommon=stats["uncommon"],
            )
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return StatisticsResponse(
                total=0, interesting=0, uncommon=0, message="No data available"
            )

    def flip_alleles(
        self, genotype: str, stabilized_orientation: str
    ) -> Dict[str, Any]:
        """Flip alleles based on stabilized orientation.

        Converts genotype alleles when the SNP orientation differs between
        the personal genome data and SNPedia reference data. This is necessary
        because different genome builds may report SNPs on different strands.

        Args:
            genotype (str): The genotype string in format "(A;T)".
            stabilized_orientation (str): The orientation from SNPedia ("plus" or "minus").

        Returns:
            Dict[str, Any]: Dictionary containing:
                - genotype (str): The (possibly flipped) genotype
                - flipped (bool): Whether alleles were flipped

        Example:
            >>> service = SNPService()
            >>> result = service.flip_alleles("(A;T)", "minus")
            >>> print(f"Flipped genotype: {result['genotype']}")
            >>> print(f"Was flipped: {result['flipped']}")

        Note:
            Flipping rules: A↔T, C↔G. Only applied when orientation is "minus".
        """
        if stabilized_orientation == "minus" and genotype != "":
            try:
                # Parse genotype format like "(A;T)"
                original_genotype = genotype.strip("()")
                alleles = original_genotype.split(";")

                if len(alleles) != 2:
                    return {"genotype": genotype, "flipped": False}

                modified_alleles = []
                flip_map = {"A": "T", "T": "A", "C": "G", "G": "C"}

                for allele in alleles:
                    allele = allele.strip()
                    modified_alleles.append(flip_map.get(allele, allele))

                updated_genotype = f"({modified_alleles[0]};{modified_alleles[1]})"
                return {"genotype": updated_genotype, "flipped": True}

            except Exception as e:
                logger.error(f"Error flipping alleles for {genotype}: {e}")
                return {"genotype": genotype, "flipped": False}
        else:
            return {"genotype": genotype, "flipped": False}

    def create_enriched_snp(
        self, rsid: str, snp_data: SNPData, snpedia_data: SNPediaEntry
    ) -> EnrichedSNP:
        """Create an enriched SNP by combining personal and reference data.

        Combines personal genotype data with SNPedia reference information
        to create a comprehensive SNP analysis including clinical significance,
        allele flipping, and formatted display information.

        Args:
            rsid (str): The Reference SNP ID.
            snp_data (SNPData): Personal genotype data.
            snpedia_data (SNPediaEntry): Reference data from SNPedia.

        Returns:
            EnrichedSNP: Combined SNP data with analysis results.

        Example:
            >>> service = SNPService()
            >>> snp_data = SNPData(rsid="rs1234567", genotype="(A;T)")
            >>> snpedia_data = SNPediaEntry(rsid="rs1234567", description="...", ...)
            >>> enriched = service.create_enriched_snp("rs1234567", snp_data, snpedia_data)
            >>> print(f"Is interesting: {enriched.is_interesting}")
        """
        # Flip alleles if needed
        flip_result = self.flip_alleles(
            snp_data.genotype, snpedia_data.stabilized_orientation
        )

        # Format genotype display
        genotype_display = snp_data.genotype
        if flip_result["flipped"]:
            genotype_display += f"<br><i>flipped<br>{flip_result['genotype']}</i>"

        # Format variations for display
        formatted_variations = []
        for variation in snpedia_data.variations:
            if variation and len(variation) > 0:
                # Bold the variation if it matches the genotype
                current_genotype = flip_result["genotype"]
                if current_genotype == variation[0]:
                    formatted_variations.append(f"<b>{' '.join(variation)}</b>")
                else:
                    formatted_variations.append(" ".join(variation))

        # Determine if interesting and uncommon
        is_interesting = snpedia_data.is_interesting()
        is_uncommon = snpedia_data.is_uncommon_for_genotype(flip_result["genotype"])

        return EnrichedSNP(
            rsid=rsid,
            genotype=genotype_display,
            description=snpedia_data.description,
            variations=formatted_variations,
            stabilized_orientation=snpedia_data.stabilized_orientation,
            is_flipped=flip_result["flipped"],
            is_interesting=is_interesting,
            is_uncommon=is_uncommon,
        )

    def process_genome_data(self) -> List[EnrichedSNP]:
        """Process personal genome data with SNPedia information.

        Processes the entire personal genome by enriching each SNP with
        corresponding SNPedia reference data. This is the main processing
        pipeline that creates the enriched dataset for analysis.

        Returns:
            List[EnrichedSNP]: List of enriched SNPs with combined data.

        Example:
            >>> service = SNPService()
            >>> enriched_snps = service.process_genome_data()
            >>> interesting_count = sum(1 for snp in enriched_snps if snp.is_interesting)
            >>> print(f"Found {interesting_count} interesting SNPs")

        Note:
            This method processes all SNPs in the personal genome and may
            take significant time for large datasets. Progress is logged
            every 100 processed SNPs.
        """
        genome = self.get_personal_genome()
        if not genome:
            logger.warning("No personal genome data available")
            return []

        enriched_snps = []
        processed_count = 0

        for rsid, snp_data in genome.snps.items():
            try:
                # Skip SNPs without valid genotypes
                if not snp_data.has_genotype():
                    continue

                # Get SNPedia data
                snpedia_data = self.get_snpedia_data(rsid)
                if not snpedia_data:
                    logger.debug(f"No SNPedia data for {rsid}")
                    continue

                # Create enriched SNP
                enriched_snp = self.create_enriched_snp(rsid, snp_data, snpedia_data)
                enriched_snps.append(enriched_snp)

                processed_count += 1
                if processed_count % 100 == 0:
                    logger.info(f"Processed {processed_count} SNPs")

            except Exception as e:
                logger.error(f"Error processing SNP {rsid}: {e}")
                continue

        logger.info(f"Successfully processed {len(enriched_snps)} SNPs")
        return enriched_snps

    def save_processed_results(self, enriched_snps: List[EnrichedSNP]) -> bool:
        """Save processed results to persistent storage.

        Saves the list of enriched SNPs to the results repository for
        future retrieval and analysis.

        Args:
            enriched_snps (List[EnrichedSNP]): List of processed SNP data to save.

        Returns:
            bool: True if save was successful, False otherwise.

        Example:
            >>> service = SNPService()
            >>> enriched_snps = service.process_genome_data()
            >>> success = service.save_processed_results(enriched_snps)
            >>> if success:
            ...     print("Results saved successfully")
        """
        return self.result_repo.save_results(enriched_snps)

    def invalidate_caches(self) -> None:
        """Invalidate all repository caches.

        Clears cached data from all repositories to ensure fresh data
        is loaded on the next access. Useful when underlying data files
        have been updated.

        Example:
            >>> service = SNPService()
            >>> service.invalidate_caches()
            >>> # Next data access will reload from files
        """
        self.snp_repo.invalidate_cache()
        self.snpedia_repo.invalidate_cache()
