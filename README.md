# OSGenome
An Open Source Web Application for Genetic Data (SNPs) using Ancestry and Data Crawling Technologies

## Description
OS Genome is an open source web application that allows users to gather the information they need to make sense of their own genome without needing to rely on outside services with unknown privacy policies. OS Genome's goal is to crawl various sources and give meaning to an individual's genome. It creates a Responsive Grid of the user's specific genome. This allows for everything from filtering to excel exporting. All of which using Flask, Tabulator, and Python programming.

## 📚 Documentation

For detailed information about specific aspects of OSGenome, see our comprehensive documentation:

- **[Configuration Guide](docs/CONFIGURATION.md)** - Environment setup, configuration options, and deployment settings
- **[Security Documentation](docs/SECURITY.md)** - Security features, best practices, and privacy information
- **[Caching & Performance](docs/CACHING.md)** - Performance optimization, caching strategies, and memory management
- **[Error Handling](docs/ERROR_HANDLING.md)** - Troubleshooting guide, common issues, and error resolution
- **[Keyboard Shortcuts](docs/KEYBOARD_SHORTCUTS.md)** - Complete list of keyboard shortcuts and navigation tips
- **[Repository Structure](docs/REPOSITORY_STRUCTURE.md)** - Project organization, file structure, and development workflow
- **[Docker Deployment](docs/DOCKER.md)** - Container optimization, multi-stage builds, and production deployment
- **[API Documentation](docs/_build/html/index.html)** - Complete API reference with type hints and examples
- **[Docstring Style Guide](docs/DOCSTRING_STYLE_GUIDE.md)** - Documentation standards and best practices
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Quick commands and common operations

## What are SNPs?
From Bioinformatics - A Practical Approach by Shui Qing Ye, M.D., Ph.D. (pg 108):

>SNP, pronounced “snip,” stands for single-nucleotide polymorphism, which represents a substitution of one base for another, e.g., C to T or A to G. SNP is the most common variation in the human genome and occurs approximately once every 100 to 300 bases. SNP is terminologically distinguished from mutation based on an arbitrary population frequency cutoff value: 1%, with SNP [greater than] 1% and mutation [less than] 1%. A key aspect of research in genetics is associating sequence variations with heritable phenotypes. Because SNPs are expected to facilitate large-scale association genetics studies, there has been an increasing interest in SNP discovery and detection.

Ancestry gathers hundreds of thousands of SNPs that give you everything from your genetic ancestry (haplogroups) to whether you are more likely to think Cilantro tastes like soap, or how quickly you likely digest coffee. Unfortunately, and fortunately, there is a lot of information out there on each specific SNP and what associations they might have. Much like Phrenology of the late 18th and early 19th century, where personality was attempted to be associated to facial features, there can be a lot of attempts to draw conclusions in noise. Enter OS Genome, where you can discover links and research at your own pace with the information you gather. It will highlight what specific Genotype is yours, and what that means in the context of discovery. From there you can google the relevant SNP id at your own intrigue or use the Lookup on SNPedia button to discover more about that SNP on SNPedia.


## Security & Privacy 🔒

**Your data stays private.** All genetic data is processed and stored locally on your computer. The application only makes requests to SNPedia's public API to fetch SNP information - your personal genetic data is never transmitted.

### Security Features
- ✅ Input validation and sanitization
- ✅ Protection against path traversal attacks
- ✅ Rate limiting to respect SNPedia's servers
- ✅ Secure file handling with size limits
- ✅ Security headers (XSS, clickjacking protection)
- ✅ No debug mode in production

See our [Security Documentation](docs/SECURITY.md) for detailed security information.

## Performance & Caching ⚡

OSGenome includes intelligent caching and lazy loading to optimize performance:

- ✅ **Lazy Loading**: Data loaded on-demand, not at startup
- ✅ **LRU Cache**: Automatic caching with smart eviction
- ✅ **Pagination**: API support for large datasets
- ✅ **Reduced Memory**: 89% memory reduction for large files
- ✅ **Fast Startup**: No waiting for data to load

### API Pagination Example
```bash
# Get first 100 results
GET /api/rsids?page=1&page_size=100

# Get cache statistics
GET /api/cache/stats
```

See our [Caching & Performance](docs/CACHING.md) documentation for detailed caching information and configuration.

## Async Data Crawler 🚀

The data crawler uses async/await for **3-5x faster** SNP data fetching:

- ✅ **Concurrent Requests**: Process 3-5 SNPs simultaneously
- ✅ **Smart Rate Limiting**: Conservative concurrency to prevent server overload
- ✅ **Faster Crawling**: 100 SNPs in ~30 seconds vs ~150 seconds
- ✅ **Better Error Handling**: Exponential backoff for 429/502/503 errors
- ✅ **Backward Compatible**: Synchronous fallback available

### Performance Comparison
| Dataset Size | Synchronous | Asynchronous | Improvement |
|--------------|-------------|--------------|-------------|
| 100 SNPs     | ~150 sec    | ~30 sec      | **5x faster** |
| 500 SNPs     | ~12 min     | ~2.5 min     | **5x faster** |
| 1000 SNPs    | ~25 min     | ~5 min       | **5x faster** |

**Note**: Uses conservative settings (1.5s delay, 3-5 concurrent) to prevent 502/503 server errors.

See our [Error Handling](docs/ERROR_HANDLING.md) documentation for detailed troubleshooting information.

## Where is my information stored?
All of your genetic data (your raw data) is stored and used locally on your computer. At no point does this software send your data anywhere. It is used in personalizing OS Genome to you.


## How do I grab my raw SNP Data?
Since it's quite possible Ancestry will change the way you download the raw data... this might change from time to time. Just look up how to download Ancestry raw data in Google, and you might just find a link to Ancestry to download the raw data. It'll be in a comma separated format.

## Orientation (Important)
SNPedia reports SNPs of an  initial build it was made out of. Current vendors of Genomic Testing use a different build. To handle this SNPedia introduced a Stabilized Orientation and Orientation field. OSGenome automatically relays the Stabilized Orientation, but to avoid confusion, does not map the corrected genotype and also does not highlight the correct variation. This is done as builds might change one day and this fix might not be needed as well as the presence of ambiguous genotype mappings.
[See here for more information by SNPedia authors](https://www.reddit.com/r/promethease/comments/3ayg64/orientation_confusion/).

In best words, if the orientation is minus and you are using Ancestry for instance (which only reports on positive, last checked: October|2022), there is a layer of ambiguity to your test results for the SNP as this is a result of build differences across what SNPedia was built on, and what Ancestry and others genome testing report. A tutorial and more information can be found [here](https://www.snpedia.com/index.php/Orientation#:~:text=Orientation%20indicates%20the%20orientation%20reported,reference%20build%20is%20shown%20next).
For conditions of Stabilized Orientation equaling Minus and using Ancestry raw data, try flipping them as such:
- A->T
- T->A
- C->G
- G->C

Explanation of Plus/Minus: [NIH Research Paper here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6099125/)

 Currently, Human Genome testing uses [GRCh38](https://www.nature.com/articles/d41586-021-00462-9#:~:text=The%20most%20recent%20version%20of,has%20been%20repeatedly%20'patched)

### Steps to introduce Orientation in a Pre-Existing Environment
If you are attempting to retrieve Orientation, a new environment must be set up (cloning from scratch). If you decide to keep the old environment. No bolding will be performed on old data.

## Does OS Genome work through other SNP/genetic testing sites?
Currently, there is a script I can upload to convert the formats. MyFamilyTree.com, for instance, uses a comma to separate their data, while Ancestry uses tabs, that's pretty much the main difference. If there's enough demand, I can easily include it to the workflow... so feel free to request the addition. As OS Genome improves, a lot of functionality is likely to arise.


## How much data will OS Genome grab?
Last checked, Ancestry had over 700,000 SNPs that comes from their raw SNP file, while MyFamilyTree.com had over 700,000 SNPs. OS Genome crawls a couple hundred each time. Each time you run step 1, it'll add additional several hundred SNPs to your result for you to examine. This was done to reduce the amount of data that needs to be crawled before you have something to examine. OSGenome relies on the SNPs that SNPedia has covered. Last checked, there were 110402 SNPS. So it will keep growing as SNPedia adds more SNPs into their database.  Feel free to run step 1 as often as you'd like to gain additional data, and no worries... it keeps track of your progress.

## It maxes out at 20,000 SNPs?
At current, if you cross reference an Ancestry report with SNPedia, it will have a valid set of 20,000 SNPs. I've created a modification to the application to only get the SNPs that SNPedia approves as requested in their terms (this prevents it from denying entry). Running this script on a sample Ancestry output has revealed that there are a maximum of around 20,000 SNPs in their encyclopedia for analysis of Ancestry reports. The modification is found within the GenomeImporter. It continously crawls the API endpoint for finding the approved SNPs and uses a dictionary to take advantage of the time complexity of the hash function. It then creates a JSON file within the data directory called approved.json. If after awhile you want to revisit this application. This is one of the files to delete.

## What are some additional features?
OS Genome also has Excel Exporting, SNPedia Lookup, and filtering. SNPedia Lookup works by selecting the row you're interested in looking into and pressing the Lookup on SNPedia button. It will open up a new window with the details of the SNP.

### Keyboard Shortcuts ⌨️
OSGenome includes keyboard shortcuts for faster navigation and actions:

- **Ctrl/Cmd + E** - Export to Excel
- **Ctrl/Cmd + L** - Lookup selected SNP on SNPedia
- **Ctrl/Cmd + F** - Focus search/filter
- **Ctrl/Cmd + K** - Toggle column visibility menu
- **Ctrl/Cmd + R** - Reload data
- **Ctrl/Cmd + /** - Show keyboard shortcuts help
- **Escape** - Clear selection and close menus
- **Arrow Keys** - Navigate table rows
- **Enter** - Select focused row

Click the "Shortcuts" button in the toolbar or press Ctrl+/ to view all available shortcuts. See our [Keyboard Shortcuts](docs/KEYBOARD_SHORTCUTS.md) documentation for detailed usage guide.

## Contributions
There have been three contributions so far.
- Daniel McNally [@sangaman](https://github.com/sangaman) | Python 3.10 Compatability through dependencies and ReadMe improvements
- Dan Grahn [@dgrahn](https://github.com/dgrahn) | Front End Improvements
- Mikołaj Zalewski [@mikolajz](https://github.com/mikolajz) | Importance Column | Detailed SNP Error Logging | Feel free to take a look at [Relevant Feature Branch](https://github.com/mentatpsi/OSGenome/tree/feature/importance-check-and-detailed-error)

## Disclaimer
Raw Data coming from Genetic tests done by Direct To Consumer companies such as Ancestry.com and other genetic testing services were found to have a false positive rate of 40% for genes with clinical significance in a March 2018 study [*False-positive results released by direct-to-consumer genetic tests highlight the importance of clinical confirmation testing for appropriate patient care*](https://www.nature.com/articles/gim201838). For this reason, it's important to confirm any at risk clinical SNPs with your doctor who can provide genetic tests and send them to a clinical laboratory.

## Installation:

### Prerequisites
- Python 3.13 or higher
- pip (Python package manager)

### Step 0: Install Dependencies
```bash
# Install production dependencies
uv sync

# Install development dependencies (includes documentation and type checking tools)
uv sync --group dev
```
This installs Flask (web server), BeautifulSoup (web scraping), and other required packages.

### Step 0.5: Configure Environment (Recommended)
```bash
# Copy the example environment file
cp .env.example .env

# Generate a secure secret key
python -c "import os; print('SECRET_KEY=' + os.urandom(32).hex())" >> .env
```

### Verify Installation
```bash
# Run security tests
uv run python tests/test_security.py

# Generate documentation (development dependencies required)
./scripts/generate-docs.sh

# Run type checking
./scripts/type-check.sh
```


### Step 1: Import Your Genetic Data
```bash
python3 SNPedia/data_crawler.py -f /path/to/your/ancestry_raw_data.txt
```
This processes your genetic data and fetches relevant information from SNPedia. The crawler includes rate limiting to be respectful of SNPedia's servers.

**Note:** This step may take some time as it fetches data for thousands of SNPs with appropriate delays between requests.

### Step 2: Start the Web Server

**Docker (recommended):**
```bash
# Production deployment
docker-compose up

# Development with hot reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# Build optimized image
./scripts/docker-build.sh --target production
```

**Development mode:**
```bash
export FLASK_ENV=development
python3 SNPedia/app.py
```

**Production mode:**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-from-env-file
gunicorn --config SNPedia/gunicorn_config.py SNPedia.app:app
```

### Step 3: Access Your Genome
Open your browser and navigate to:
- Development: http://127.0.0.1:5000
- Production: http://0.0.0.0:8080 (or configured port)

All processing happens locally on your machine.

## arv support
There exists a library arv ([GitHub: cslarsen/arv - A fast 23andMe DNA parser and inferrer for Python](https://github.com/cslarsen/arv)) that allows for rule based matching of health and trait attributes using a hash table of raw genetic data. It is possible to alter the rsidDict.json to allow for automatically populating the rule matching conditions. I will be designing this functionality in a python script that will be able to be used to import the JSON as a dictionary that can be called within the rule matching. Please keep in mind its respective disclaimers before using the service.

## Development 🛠️

OSGenome follows modern Python development practices with comprehensive type hints, documentation, and code quality tools.

### Code Quality Tools

The project includes several tools to maintain code quality:

```bash
# Type checking with MyPy
./scripts/type-check.sh

# Generate comprehensive documentation
./scripts/generate-docs.sh

# Run pre-commit hooks
pre-commit run --all-files

# Format code with Black
uv run black SNPedia/

# Sort imports with isort
uv run isort SNPedia/

# Lint with flake8
uv run flake8 SNPedia/
```

### Documentation Standards

- **Complete type hints**: All functions have comprehensive type annotations
- **Google-style docstrings**: Consistent documentation format with examples
- **Automatic API docs**: Generated with Sphinx from docstrings
- **Code examples**: Real-world usage examples in documentation

### Type Safety

The codebase uses comprehensive type hints:
- Function parameters and return types
- Optional and Union types where appropriate
- Generic types for collections
- MyPy configuration for strict type checking

### Documentation Generation

API documentation is automatically generated from docstrings:

```bash
# Generate and view documentation
./scripts/generate-docs.sh

# Documentation will be available at docs/_build/html/index.html
```

## Example
The application provides a responsive grid interface for viewing and analyzing your genetic data with filtering, sorting, and export capabilities.
