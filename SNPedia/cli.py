"""Command line interface for SNPedia operations."""

import argparse
import asyncio

from SNPedia.core.logger import logger
from SNPedia.data.repositories import SNPRepository
from SNPedia.services.crawler_service import CrawlerService
from SNPedia.services.import_service import ImportService
from SNPedia.services.snp_service import SNPService


def _get_missing_rsids(valid_snps: dict) -> dict:
    """Get RSIDs that are missing from existing SNPedia data."""
    import json
    import os

    results_file = "data/results.json"
    existing_rsids = set()

    # Load existing SNPedia data
    if os.path.exists(results_file):
        try:
            with open(results_file) as f:
                existing_data = json.load(f)
                if existing_data:
                    existing_rsids = {rsid.lower() for rsid in existing_data.keys()}
                    logger.info(
                        f"Found existing SNPedia data for {len(existing_rsids)} RSIDs"
                    )
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Could not load existing SNPedia data: {e}")

    # Find missing RSIDs
    missing_rsids = {}
    for rsid, snp in valid_snps.items():
        if rsid.lower() not in existing_rsids:
            missing_rsids[rsid] = snp

    if missing_rsids:
        logger.info(f"Found {len(missing_rsids)} RSIDs missing SNPedia data")
    else:
        logger.info("All RSIDs already have SNPedia data")

    return missing_rsids


def import_genome(filepath: str, force: bool = False) -> bool:
    """Import genome data from file."""
    try:
        import_service = ImportService()

        # Check if data already exists
        if not force and import_service.has_existing_data():
            logger.info("Personal genome data already exists. Use --force to reimport.")
            return True

        genome = import_service.import_genome_file(filepath)

        if not genome or not genome.snps:
            logger.error("No SNPs found in the provided file")
            return False

        logger.info(f"Successfully imported {len(genome.snps)} SNPs")
        return True

    except Exception as e:
        logger.error(f"Error importing genome data: {e}")
        return False


def crawl_snpedia(use_async: bool = True) -> bool:
    """Crawl SNPedia for genetic data."""
    try:
        # Load personal SNPs
        snp_repo = SNPRepository()
        genome = snp_repo.get_genome()

        if not genome:
            logger.error("No personal genome data found. Import genome data first.")
            return False

        valid_snps = genome.get_valid_snps()
        if not valid_snps:
            logger.error("No valid SNPs found to crawl")
            return False

        # Check which RSIDs are missing from existing SNPedia data
        missing_rsids = _get_missing_rsids(valid_snps)

        if not missing_rsids:
            logger.info("All RSIDs already have SNPedia data. Nothing to crawl.")
            return True

        logger.info(
            f"Found {len(missing_rsids)} RSIDs to crawl from SNPedia (out of {len(valid_snps)} total)"
        )

        # Create crawler service
        crawler = CrawlerService()

        # Convert missing SNPs to format expected by crawler
        snps_dict = {rsid: snp.genotype for rsid, snp in missing_rsids.items()}

        # Crawl data
        if use_async:
            logger.info("Using async crawling")
            asyncio.run(crawler.crawl_snps_async(snps_dict))
        else:
            logger.info("Using sync crawling")
            crawler.crawl_snps_sync(snps_dict)

        logger.info("SNPedia crawl completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during SNPedia crawl: {e}")
        return False


def process_results() -> bool:
    """Process and enrich SNP data with SNPedia information."""
    try:
        logger.info("Processing SNP results...")

        snp_service = SNPService()
        enriched_snps = snp_service.process_genome_data()

        if not enriched_snps:
            logger.warning("No enriched SNPs generated")
            return False

        # Save results
        success = snp_service.save_processed_results(enriched_snps)
        if success:
            logger.info(
                f"Successfully processed and saved {len(enriched_snps)} enriched SNPs"
            )
            return True
        else:
            logger.error("Failed to save processed results")
            return False

    except Exception as e:
        logger.error(f"Error processing results: {e}")
        return False


def show_statistics() -> bool:
    """Show statistics about the genetic data."""
    try:
        snp_service = SNPService()
        stats = snp_service.get_statistics()

        print("\nGenetic Data Statistics:")
        print(f"Total SNPs: {stats.total}")
        print(f"Interesting SNPs: {stats.interesting}")
        print(f"Uncommon SNPs: {stats.uncommon}")

        if stats.message:
            print(f"Note: {stats.message}")

        return True

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return False


def main() -> None:
    """Run the main CLI application."""
    parser = argparse.ArgumentParser(description="SNPedia CLI Tool")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import genome data from file")
    import_parser.add_argument(
        "-f", "--file", required=True, help="Path to genome data file"
    )
    import_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reimport even if data already exists",
    )

    # Crawl command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl SNPedia for genetic data")
    crawl_parser.add_argument(
        "--sync", action="store_true", help="Use synchronous crawling (default: async)"
    )

    # Process command
    subparsers.add_parser("process", help="Process and enrich SNP data")

    # Stats command
    subparsers.add_parser("stats", help="Show statistics about genetic data")

    # Full pipeline command
    pipeline_parser = subparsers.add_parser(
        "pipeline", help="Run full pipeline: import -> crawl -> process"
    )
    pipeline_parser.add_argument(
        "-f", "--file", required=True, help="Path to genome data file"
    )
    pipeline_parser.add_argument(
        "--sync", action="store_true", help="Use synchronous crawling (default: async)"
    )
    pipeline_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reimport even if data already exists",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "import":
            success = import_genome(args.file, force=getattr(args, "force", False))

        elif args.command == "crawl":
            success = crawl_snpedia(use_async=not args.sync)

        elif args.command == "process":
            success = process_results()

        elif args.command == "stats":
            success = show_statistics()

        elif args.command == "pipeline":
            logger.info("Starting full pipeline...")

            # Step 1: Import
            success = import_genome(args.file, force=getattr(args, "force", False))
            if not success:
                logger.error("Pipeline failed at import step")
                return

            # Step 2: Crawl
            success = crawl_snpedia(use_async=not args.sync)
            if not success:
                logger.error("Pipeline failed at crawl step")
                return

            # Step 3: Process
            success = process_results()
            if not success:
                logger.error("Pipeline failed at process step")
                return

            logger.info("Pipeline completed successfully!")
            show_statistics()

        if not success and args.command != "pipeline":
            exit(1)

    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
