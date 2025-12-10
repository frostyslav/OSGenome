"""Data models for SNP and genetic data."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SNPData:
    """Represents a single SNP entry."""

    rsid: str
    genotype: str
    chromosome: Optional[str] = None
    position: Optional[int] = None

    def __post_init__(self):
        """Validate SNP data after initialization."""
        if not self.rsid or not isinstance(self.rsid, str):
            raise ValueError("RSID must be a non-empty string")

        if not self.genotype or not isinstance(self.genotype, str):
            raise ValueError("Genotype must be a non-empty string")

    def has_genotype(self) -> bool:
        """Check if SNP has a valid genotype (not missing)."""
        return self.genotype != "(-;-)" and self.genotype.strip() != ""


@dataclass
class PersonalGenome:
    """Represents a collection of personal SNP data."""

    snps: Dict[str, SNPData]
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()

    def get_snp(self, rsid: str) -> Optional[SNPData]:
        """Get SNP data by RSID."""
        return self.snps.get(rsid.lower())

    def has_snp(self, rsid: str) -> bool:
        """Check if genome contains a specific SNP."""
        return rsid.lower() in self.snps

    def get_valid_snps(self) -> Dict[str, SNPData]:
        """Get only SNPs with valid genotypes."""
        return {rsid: snp for rsid, snp in self.snps.items() if snp.has_genotype()}

    def count_total(self) -> int:
        """Get total number of SNPs."""
        return len(self.snps)

    def count_valid(self) -> int:
        """Get number of SNPs with valid genotypes."""
        return len(self.get_valid_snps())


@dataclass
class SNPediaEntry:
    """Represents SNPedia data for a specific SNP."""

    rsid: str
    description: str
    variations: List[List[str]]
    stabilized_orientation: str

    def __post_init__(self):
        """Validate SNPedia entry data."""
        if not self.rsid or not isinstance(self.rsid, str):
            raise ValueError("RSID must be a non-empty string")

        if not isinstance(self.variations, list):
            self.variations = []

        if not isinstance(self.description, str):
            self.description = ""

    def has_variations(self) -> bool:
        """Check if entry has variation data."""
        return len(self.variations) > 0

    def get_genotype_info(self, genotype: str) -> Optional[List[str]]:
        """Get variation info for a specific genotype."""
        for variation in self.variations:
            if variation and len(variation) > 0 and variation[0] == genotype:
                return variation
        return None

    def is_interesting(self) -> bool:
        """Check if any variations are marked as interesting."""
        common_words = [
            "common",
            "very common",
            "most common",
            "normal",
            "average",
            "miscall in ancestry",
            "ancestry miscall",
            "miscall by ancestry",
        ]

        for variation in self.variations:
            if len(variation) > 2:
                description = variation[2].lower()
                if not description.startswith(tuple(common_words)):
                    return True
        return False

    def is_uncommon_for_genotype(self, genotype: str) -> bool:
        """Check if a specific genotype is uncommon."""
        variation_info = self.get_genotype_info(genotype)
        if not variation_info or len(variation_info) <= 2:
            return False

        description = variation_info[2].lower()
        common_words = [
            "common",
            "very common",
            "most common",
            "normal",
            "average",
            "miscall in ancestry",
            "ancestry miscall",
            "miscall by ancestry",
        ]

        return (
            not description.startswith(tuple(common_words))
            and "common in clinvar" not in description
        )


@dataclass
class EnrichedSNP:
    """Represents a SNP enriched with SNPedia data."""

    rsid: str
    genotype: str
    description: str
    variations: List[str]
    stabilized_orientation: str
    is_flipped: bool
    is_interesting: bool
    is_uncommon: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "Name": self.rsid,
            "Description": self.description,
            "Genotype": self.genotype,
            "Variations": "<br>".join(self.variations),
            "StabilizedOrientation": self.stabilized_orientation,
            "IsInteresting": "Yes" if self.is_interesting else "No",
            "IsUncommon": "Yes" if self.is_uncommon else "No",
        }
