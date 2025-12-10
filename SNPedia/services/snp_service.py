"""Service layer for SNP-related business logic."""

from typing import Dict, List, Optional, Any
from SNPedia.models.snp_models import SNPData, PersonalGenome, SNPediaEntry, EnrichedSNP
from SNPedia.models.response_models import PaginatedResponse, StatisticsResponse
from SNPedia.data.repositories import SNPRepository, SNPediaRepository, ResultRepository
from SNPedia.core.logger import logger


class SNPService:
    """Service for SNP-related operations."""
    
    def __init__(self):
        self.snp_repo = SNPRepository()
        self.snpedia_repo = SNPediaRepository()
        self.result_repo = ResultRepository()
    
    def get_snp_data(self, rsid: str) -> Optional[SNPData]:
        """Get SNP data by RSID."""
        return self.snp_repo.get_by_id(rsid)
    
    def get_snpedia_data(self, rsid: str) -> Optional[SNPediaEntry]:
        """Get SNPedia data by RSID."""
        return self.snpedia_repo.get_by_id(rsid)
    
    def get_enriched_snp(self, rsid: str) -> Optional[EnrichedSNP]:
        """Get enriched SNP data by RSID."""
        return self.result_repo.get_by_id(rsid)
    
    def get_personal_genome(self) -> Optional[PersonalGenome]:
        """Get complete personal genome."""
        return self.snp_repo.get_genome()
    
    def get_results_paginated(self, page: int = 1, page_size: int = 100) -> PaginatedResponse:
        """Get paginated results."""
        try:
            result = self.result_repo.get_paginated(page=page, page_size=page_size)
            
            return PaginatedResponse(
                data=result['data'],
                page=result['page'],
                page_size=result['page_size'],
                total=result['total'],
                total_pages=result['total_pages'],
                has_next=result['has_next'],
                has_prev=result['has_prev']
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
                has_prev=False
            )
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all results as dictionaries."""
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
                total=stats['total'],
                interesting=stats['interesting'],
                uncommon=stats['uncommon']
            )
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return StatisticsResponse(
                total=0,
                interesting=0,
                uncommon=0,
                message="No data available"
            )
    
    def flip_alleles(self, genotype: str, stabilized_orientation: str) -> Dict[str, Any]:
        """Flip alleles based on stabilized orientation."""
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
    
    def create_enriched_snp(self, rsid: str, snp_data: SNPData, 
                           snpedia_data: SNPediaEntry) -> EnrichedSNP:
        """Create an enriched SNP from SNP and SNPedia data."""
        # Flip alleles if needed
        flip_result = self.flip_alleles(
            snp_data.genotype, 
            snpedia_data.stabilized_orientation
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
            is_uncommon=is_uncommon
        )
    
    def process_genome_data(self) -> List[EnrichedSNP]:
        """Process personal genome data with SNPedia information."""
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
        """Save processed results to file."""
        return self.result_repo.save_results(enriched_snps)
    
    def invalidate_caches(self):
        """Invalidate all repository caches."""
        self.snp_repo.invalidate_cache()
        self.snpedia_repo.invalidate_cache()