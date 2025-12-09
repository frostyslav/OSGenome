"""Validation utilities for OSGenome."""

import re
from typing import Optional, Tuple

# Import from parent package
try:
    from SNPedia.core import ValidationError
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import ValidationError


# Valid alleles
VALID_ALLELES = {"A", "T", "C", "G", "-", "I", "D"}

# RSid pattern (rs followed by digits, or i followed by digits)
RSID_PATTERN = re.compile(r"^(rs|i)\d+$", re.IGNORECASE)


def validate_rsid(rsid: str) -> bool:
    """Validate RSid format.

    Args:
        rsid: RSid to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_rsid('rs123456')
        True
        >>> validate_rsid('i5000001')
        True
        >>> validate_rsid('invalid')
        False
    """
    if not rsid or not isinstance(rsid, str):
        return False

    return bool(RSID_PATTERN.match(rsid))


def validate_allele(allele: str) -> bool:
    """Validate allele value.

    Args:
        allele: Allele to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_allele('A')
        True
        >>> validate_allele('X')
        False
    """
    if not allele or not isinstance(allele, str):
        return False

    # Check length
    if len(allele) > 10:
        return False

    # Check if valid allele
    return allele.upper() in VALID_ALLELES


def validate_genotype(genotype: str) -> Tuple[bool, Optional[str]]:
    """Validate genotype format.

    Args:
        genotype: Genotype string in format "(A;T)" or "(-;-)"

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_genotype('(A;T)')
        (True, None)
        >>> validate_genotype('(-;-)')
        (True, None)
        >>> validate_genotype('invalid')
        (False, 'Invalid genotype format')
    """
    if not genotype or not isinstance(genotype, str):
        return False, "Genotype must be a non-empty string"

    # Check format: (X;Y)
    if not genotype.startswith("(") or not genotype.endswith(")"):
        return False, "Genotype must be in format (X;Y)"

    # Extract alleles
    try:
        alleles = genotype.strip("()").split(";")
        if len(alleles) != 2:
            return False, "Genotype must contain exactly two alleles"

        # Validate each allele
        for allele in alleles:
            if not validate_allele(allele):
                return False, f"Invalid allele: {allele}"

        return True, None

    except Exception as e:
        return False, f"Error parsing genotype: {str(e)}"


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """Validate file extension.

    Args:
        filename: Filename to validate
        allowed_extensions: Set of allowed extensions (without dot)

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_file_extension('data.xlsx', {'xlsx', 'xls'})
        True
        >>> validate_file_extension('data.exe', {'xlsx', 'xls'})
        False
    """
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed_extensions


def sanitize_rsid(rsid: str) -> str:
    """Sanitize RSid by converting to lowercase and validating.

    Args:
        rsid: RSid to sanitize

    Returns:
        Sanitized RSid

    Raises:
        ValidationError: If RSid is invalid
    """
    if not validate_rsid(rsid):
        raise ValidationError(f"Invalid RSid format: {rsid}")

    return rsid.lower()


def sanitize_allele(allele: str) -> str:
    """Sanitize allele by converting to uppercase and validating.

    Args:
        allele: Allele to sanitize

    Returns:
        Sanitized allele or '-' if invalid
    """
    if not allele or not isinstance(allele, str):
        return "-"

    allele = allele.strip().upper()

    if len(allele) > 10:
        return "-"

    if allele not in VALID_ALLELES:
        return "-"

    return allele
