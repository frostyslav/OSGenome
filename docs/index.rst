OSGenome Documentation
======================

Welcome to OSGenome's documentation! OSGenome is an open source web application 
for genetic data (SNPs) analysis using ancestry data and crawling technologies.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   api_reference
   user_guides
   developer_guides
   configuration
   deployment

Quick Start
-----------

OSGenome allows users to analyze their genetic data privately and securely:

1. **Import your genetic data** from services like Ancestry.com
2. **Process and enrich** the data with SNPedia information
3. **Analyze and explore** your genetic variants through a web interface

Key Features
------------

* **Privacy-focused**: All data processing happens locally
* **Comprehensive analysis**: Enriches personal genetic data with SNPedia information
* **Web interface**: User-friendly interface for exploring genetic variants
* **Export capabilities**: Export results to Excel and other formats
* **Performance optimized**: Async processing and intelligent caching

Installation
------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/your-repo/OSGenome.git
   cd OSGenome

   # Install dependencies
   uv sync

   # Configure environment
   cp .env.example .env

   # Import your genetic data
   python SNPedia/data_crawler.py -f /path/to/your/ancestry_data.txt

   # Start the application
   python SNPedia/app.py

Docker Deployment
-----------------

For production deployment, use Docker:

.. code-block:: bash

   # Build and run with Docker Compose
   docker-compose up

   # Or build manually
   ./scripts/docker-build.sh --target production
   docker run -p 8080:8080 osgenome:latest

API Reference
=============

.. toctree::
   :maxdepth: 2

   api/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`