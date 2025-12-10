# Docstring Style Guide for OSGenome

This document defines the docstring standards for the OSGenome project. We follow the Google docstring style with some project-specific conventions.

## General Principles

1. **All public functions, classes, and modules must have docstrings**
2. **Use Google-style docstrings** for consistency with Sphinx autodoc
3. **Include type hints in function signatures** rather than in docstrings
4. **Provide examples for complex functions** to aid understanding
5. **Document exceptions that may be raised**

## Module Docstrings

Every module should start with a comprehensive docstring:

```python
"""Module for handling SNP data processing.

This module provides functionality for processing Single Nucleotide Polymorphism
(SNP) data from various genetic testing services. It includes data validation,
format conversion, and enrichment with reference databases.

The module supports multiple input formats and provides a unified interface
for genetic data analysis workflows.

Example:
    Basic usage:
        >>> from SNPedia.services import snp_service
        >>> service = snp_service.SNPService()
        >>> data = service.get_snp_data("rs1234567")

    Batch processing:
        >>> enriched_snps = service.process_genome_data()
        >>> print(f"Processed {len(enriched_snps)} SNPs")

Attributes:
    SUPPORTED_FORMATS (List[str]): List of supported file formats.
    DEFAULT_TIMEOUT (int): Default timeout for network requests.
"""
```

## Class Docstrings

Classes should document their purpose, key attributes, and usage:

```python
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
        
    Example:
        >>> service = SNPService()
        >>> snp_data = service.get_snp_data("rs1234567")
        >>> if snp_data:
        ...     print(f"Genotype: {snp_data.genotype}")
    """
```

## Function Docstrings

Functions should document parameters, return values, exceptions, and include examples:

```python
def process_genetic_data(file_path: str, format_type: str = "ancestry") -> List[SNPData]:
    """Process genetic data from a file.
    
    Reads and processes genetic data from various file formats, performing
    validation and converting to standardized SNPData objects.
    
    Args:
        file_path (str): Path to the genetic data file.
        format_type (str, optional): Format of the input file. 
                                   Supported: "ancestry", "23andme", "myheritage".
                                   Defaults to "ancestry".
    
    Returns:
        List[SNPData]: List of processed SNP data objects.
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        ValueError: If the file format is not supported or data is invalid.
        PermissionError: If the file cannot be read due to permissions.
        
    Example:
        >>> snps = process_genetic_data("/path/to/data.txt", "ancestry")
        >>> print(f"Loaded {len(snps)} SNPs")
        >>> valid_snps = [snp for snp in snps if snp.has_genotype()]
        
    Note:
        Large files may take significant time to process. Consider using
        progress callbacks for user feedback in interactive applications.
    """
```

## Method Docstrings

Methods follow the same pattern as functions but may omit the class context:

```python
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
```

## Property Docstrings

Properties should document what they represent and any side effects:

```python
@property
def is_valid(self) -> bool:
    """Check if the SNP data is valid.
    
    Returns:
        bool: True if the SNP has a valid genotype and RSID, False otherwise.
        
    Example:
        >>> snp = SNPData(rsid="rs1234567", genotype="(A;T)")
        >>> if snp.is_valid:
        ...     print("SNP data is valid")
    """
```

## Exception Docstrings

Custom exceptions should document when they're raised:

```python
class InvalidGenomeFormatError(ValueError):
    """Raised when genetic data file format is invalid or unsupported.
    
    This exception is raised when the genetic data file cannot be parsed
    due to format issues, missing required fields, or unsupported file types.
    
    Attributes:
        file_path (str): Path to the problematic file.
        format_type (str): Expected format type.
        line_number (Optional[int]): Line number where error occurred, if applicable.
    """
```

## Docstring Sections

Use these sections in order when applicable:

1. **Summary**: One-line description
2. **Extended description**: Detailed explanation (optional)
3. **Args**: Function/method parameters
4. **Returns**: Return value description
5. **Yields**: For generators (instead of Returns)
6. **Raises**: Exceptions that may be raised
7. **Example**: Usage examples
8. **Note**: Additional important information
9. **Warning**: Important warnings for users
10. **See Also**: References to related functions/classes

## Type Hints

- **Always use type hints** in function signatures
- **Import types** from `typing` module when needed
- **Use `Optional[Type]`** for values that can be None
- **Use `Union[Type1, Type2]`** for multiple possible types
- **Use `List[Type]`, `Dict[Key, Value]`** for collections

```python
from typing import Dict, List, Optional, Union

def analyze_snps(
    snp_data: List[SNPData], 
    filters: Optional[Dict[str, str]] = None
) -> Dict[str, Union[int, float]]:
    """Analyze SNP data with optional filtering."""
```

## Examples

- **Always include examples** for public functions
- **Use doctest format** when possible for testable examples
- **Show realistic usage** rather than trivial cases
- **Include error handling** in examples when relevant

## Documentation Generation

The project uses Sphinx with the following extensions:
- `sphinx.ext.autodoc`: Automatic API documentation
- `sphinx.ext.napoleon`: Google/NumPy docstring support
- `sphinx_autodoc_typehints`: Type hint integration
- `myst_parser`: Markdown support

To generate documentation:

```bash
# Generate API docs and build HTML
./scripts/generate-docs.sh

# Type checking
./scripts/type-check.sh

# View documentation
open docs/_build/html/index.html
```

## Tools and Validation

Use these tools to maintain docstring quality:

1. **MyPy**: Type checking with `mypy SNPedia/`
2. **Sphinx**: Documentation generation with `make html`
3. **Docstring coverage**: Check with `interrogate SNPedia/`
4. **Linting**: Use `flake8` with docstring plugins

## Common Patterns

### Repository Methods
```python
def get_by_id(self, item_id: str) -> Optional[ModelType]:
    """Get item by ID.
    
    Args:
        item_id (str): Unique identifier for the item.
        
    Returns:
        Optional[ModelType]: Item if found, None otherwise.
    """
```

### Service Methods
```python
def process_data(self, input_data: InputType) -> OutputType:
    """Process input data and return results.
    
    Args:
        input_data (InputType): Data to process.
        
    Returns:
        OutputType: Processed results.
        
    Raises:
        ProcessingError: If data cannot be processed.
    """
```

### API Endpoints
```python
@app.route("/api/data/<item_id>")
def get_data(item_id: str) -> Response:
    """Get data by ID endpoint.
    
    Args:
        item_id (str): Unique identifier from URL path.
        
    Returns:
        Response: JSON response with data or error message.
        
    Example:
        GET /api/data/rs1234567
        Response: {"success": true, "data": {...}}
    """
```

This style guide ensures consistent, comprehensive documentation across the OSGenome codebase.