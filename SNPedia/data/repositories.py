"""Data repositories for accessing and managing genetic data."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from SNPedia.core.logger import logger
from SNPedia.models.snp_models import EnrichedSNP, PersonalGenome, SNPData, SNPediaEntry
from SNPedia.utils.cache_manager import load_json_lazy, load_json_paginated
from SNPedia.utils.file_utils import export_to_file, load_from_file


class BaseRepository(ABC):
    """Base repository interface."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Any]:
        """Get item by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Any]:
        """Get all items."""
        pass


class SNPRepository(BaseRepository):
    """Repository for managing SNP data."""

    def __init__(self, data_file: str = "personal_snps.json") -> None:
        """Initialize SNP repository.

        Args:
            data_file (str): Path to the personal SNP data file.
                           Defaults to "personal_snps.json".
        """
        self.data_file = data_file
        self._cache = None

    def get_by_id(self, rsid: str) -> Optional[SNPData]:
        """Get SNP by RSID."""
        data = self._load_data()
        if not data or rsid.lower() not in data:
            return None

        genotype = data[rsid.lower()]
        return SNPData(rsid=rsid, genotype=genotype)

    def get_all(self) -> List[SNPData]:
        """Get all SNPs."""
        data = self._load_data()
        if not data:
            return []

        return [
            SNPData(rsid=rsid, genotype=genotype) for rsid, genotype in data.items()
        ]

    def get_genome(self) -> Optional[PersonalGenome]:
        """Get complete personal genome."""
        data = self._load_data()
        if not data:
            return None

        snps = {
            rsid: SNPData(rsid=rsid, genotype=genotype)
            for rsid, genotype in data.items()
        }

        return PersonalGenome(snps=snps)

    def has_snp(self, rsid: str) -> bool:
        """Check if SNP exists."""
        data = self._load_data()
        return data is not None and rsid.lower() in data

    def _load_data(self) -> Optional[Dict[str, str]]:
        """Load SNP data from file with caching."""
        if self._cache is None:
            self._cache = load_from_file(self.data_file)
        return self._cache

    def invalidate_cache(self) -> None:
        """Invalidate the internal cache."""
        self._cache = None


class SNPediaRepository(BaseRepository):
    """Repository for managing SNPedia data."""

    def __init__(self, data_file: str = "results.json") -> None:
        """Initialize SNPedia repository.

        Args:
            data_file (str): Path to the SNPedia data file.
                           Defaults to "results.json".
        """
        self.data_file = data_file
        self._cache = None

    def get_by_id(self, rsid: str) -> Optional[SNPediaEntry]:
        """Get SNPedia entry by RSID."""
        data = self._load_data()
        if not data or rsid.lower() not in data:
            return None

        entry_data = data[rsid.lower()]
        return SNPediaEntry(
            rsid=rsid,
            description=entry_data.get("Description", ""),
            variations=entry_data.get("Variations", []),
            stabilized_orientation=entry_data.get("StabilizedOrientation", ""),
        )

    def get_all(self) -> List[SNPediaEntry]:
        """Get all SNPedia entries."""
        data = self._load_data()
        if not data:
            return []

        entries = []
        for rsid, entry_data in data.items():
            try:
                entry = SNPediaEntry(
                    rsid=rsid,
                    description=entry_data.get("Description", ""),
                    variations=entry_data.get("Variations", []),
                    stabilized_orientation=entry_data.get("StabilizedOrientation", ""),
                )
                entries.append(entry)
            except Exception as e:
                logger.warning(f"Error creating SNPedia entry for {rsid}: {e}")
                continue

        return entries

    def get_known_rsids(self) -> List[str]:
        """Get list of known RSIDs from SNPedia."""
        snpedia_data = load_from_file("snpedia_snps.json")
        return snpedia_data if snpedia_data else []

    def _load_data(self) -> Optional[Dict[str, Dict]]:
        """Load SNPedia data from file with caching."""
        if self._cache is None:
            self._cache = load_from_file(self.data_file)
        return self._cache

    def invalidate_cache(self) -> None:
        """Invalidate the internal cache."""
        self._cache = None


class ResultRepository(BaseRepository):
    """Repository for managing enriched result data."""

    def __init__(self, data_file: str = "result_table.json") -> None:
        """Initialize result repository.

        Args:
            data_file (str): Path to the enriched results data file.
                           Defaults to "result_table.json".
        """
        self.data_file = data_file

    def get_by_id(self, rsid: str) -> Optional[EnrichedSNP]:
        """Get enriched SNP by RSID."""
        data = load_json_lazy(self.data_file)
        if not data:
            return None

        for item in data:
            if item.get("Name", "").lower() == rsid.lower():
                return self._dict_to_enriched_snp(item)

        return None

    def get_all(self) -> List[EnrichedSNP]:
        """Get all enriched SNPs."""
        data = load_json_lazy(self.data_file)
        if not data:
            return []

        results = []
        for item in data:
            try:
                enriched_snp = self._dict_to_enriched_snp(item)
                results.append(enriched_snp)
            except Exception as e:
                logger.warning(f"Error converting result item: {e}")
                continue

        return results

    def get_paginated(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """Get paginated results."""
        return load_json_paginated(self.data_file, page=page, page_size=page_size)

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the results."""
        data = load_json_lazy(self.data_file)
        if not data:
            return {"total": 0, "interesting": 0, "uncommon": 0}

        total = len(data)
        interesting = sum(
            1 for item in data if item.get("IsInteresting", "").lower() == "yes"
        )
        uncommon = sum(
            1 for item in data if item.get("IsUncommon", "").lower() == "yes"
        )

        return {"total": total, "interesting": interesting, "uncommon": uncommon}

    def save_results(self, results: List[EnrichedSNP]) -> bool:
        """Save enriched results to file."""
        try:
            data = [result.to_dict() for result in results]
            return export_to_file(data=data, filename=self.data_file)
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False

    def _dict_to_enriched_snp(self, data: Dict[str, Any]) -> EnrichedSNP:
        """Convert dictionary to EnrichedSNP object."""
        return EnrichedSNP(
            rsid=data.get("Name", ""),
            genotype=data.get("Genotype", ""),
            description=data.get("Description", ""),
            variations=(
                data.get("Variations", "").split("<br>")
                if data.get("Variations")
                else []
            ),
            stabilized_orientation=data.get("StabilizedOrientation", ""),
            is_flipped="flipped" in data.get("Genotype", "").lower(),
            is_interesting=data.get("IsInteresting", "").lower() == "yes",
            is_uncommon=data.get("IsUncommon", "").lower() == "yes",
        )
