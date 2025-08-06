import argparse
import json
import time
import urllib.request

from bs4 import BeautifulSoup
from genome_importer import PersonalData
from logger import logger
from typing_extensions import Self
from utils import export_to_file, load_from_file


class SNPCrawl:
    def __init__(self: Self, rsid_file: str = None, snp_file: str = None):
        self.rsid_info = load_from_file(filename=rsid_file)
        self.personal_snps = load_from_file(filename=snp_file)
        self.rsid_list = []
        self.enriched_snps = {}

        if self.personal_snps:
            self.init_crawl(self.personal_snps)
            self.export()
            self.create_list()
        else:
            logger.error("No SNPs to crawl")

    def init_crawl(self: Self, rsids: dict):
        count = 0
        delay_count = 0
        self.delay_count = 0

        for rsid in rsids.keys():
            if rsid not in self.rsid_info.keys():
                delay_count += 1
            self.grab_table(rsid)
            count += 1
            if count > 0 and count % 10 == 0:
                logger.info("%i out of %s completed" % (count, len(rsids)))
            # add delay for snpedia crawling
            # if count == 500:
            #     break
            if (
                delay_count > 0
                and delay_count % 10 == 0
                and delay_count != self.delay_count
            ):
                self.delay_count = delay_count
                logger.info("Exporting intermediate results...")
                self.export()
                self.create_list()
                logger.info("Sleeping for 30 seconds...")
                time.sleep(30)
        logger.info("Done")

    def grab_table(self: Self, rsid: str):  # noqa C901
        try:
            url = "https://bots.snpedia.com/index.php/" + rsid
            if rsid not in self.rsid_info.keys():
                logger.info("Grabbing data about SNP: {}".format(rsid))
                self.rsid_info[rsid.lower()] = {
                    "Description": "",
                    "Variations": [],
                    "StabilizedOrientation": "",
                }
                response = urllib.request.urlopen(url)
                html = response.read()
                bs = BeautifulSoup(html, "html.parser")
                table = bs.find("table", {"class": "sortable smwtable"})
                description = bs.find(
                    "table",
                    {
                        "style": "border: 1px; background-color: #FFFFC0; border-style: solid; margin:1em; width:90%;"
                    },
                )

                # Orientation Finder
                orientation = bs.find("td", string="Rs_StabilizedOrientation")
                if orientation:
                    plus = orientation.parent.find("td", string="plus")
                    minus = orientation.parent.find("td", string="minus")
                    if plus:
                        self.rsid_info[rsid]["StabilizedOrientation"] = "plus"
                    if minus:
                        self.rsid_info[rsid]["StabilizedOrientation"] = "minus"
                else:
                    link = bs.find("a", {"title": "StabilizedOrientation"})
                    if link:
                        table_row = link.parent.parent
                        plus = table_row.find("td", string="plus")
                        minus = table_row.find("td", string="minus")
                        if plus:
                            self.rsid_info[rsid]["StabilizedOrientation"] = "plus"
                        if minus:
                            self.rsid_info[rsid]["StabilizedOrientation"] = "minus"

                logger.debug(
                    "{} stabilized orientation: {}".format(
                        rsid, self.rsid_info[rsid]["StabilizedOrientation"]
                    )
                )

                if description:
                    d1 = self.table_to_list(description)
                    self.rsid_info[rsid]["Description"] = d1[0][0]
                    logger.debug(
                        "{} description: {}".format(
                            rsid, self.rsid_info[rsid]["Description"]
                        )
                    )
                if table:
                    d2 = self.table_to_list(table)
                    self.rsid_info[rsid]["Variations"] = d2[1:]
                    logger.debug(
                        "{} variations: {}".format(
                            rsid, self.rsid_info[rsid]["Variations"]
                        )
                    )
        except urllib.error.HTTPError:
            logger.error(
                "{} was not found or contained no valid information".format(url)
            )

    def table_to_list(self: Self, table):
        rows = table.find_all("tr")
        data = []
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        return data

    def flip_alleles(
        self: Self, rsid: str, genotype: str, stabilized_orientation: str
    ) -> dict:
        if stabilized_orientation == "minus" and genotype != "":
            original_genotype = genotype
            modified_genotype = [None] * 2

            for i, allele in enumerate(original_genotype.strip("()").split(";")):
                if allele == "A":
                    modified_genotype[i] = "T"
                    continue
                if allele == "T":
                    modified_genotype[i] = "A"
                    continue
                if allele == "C":
                    modified_genotype[i] = "G"
                    continue
                if allele == "G":
                    modified_genotype[i] = "C"
                    continue
                modified_genotype[i] = allele
            updated_genotype = "({};{})".format(
                modified_genotype[0], modified_genotype[1]
            )
            self.enriched_snps[rsid.lower()] = updated_genotype
            return {"genotype": updated_genotype, "flipped": True}
        else:
            self.enriched_snps[rsid.lower()] = genotype
            return {"genotype": genotype, "flipped": False}

    def create_entry(
        self: Self,
        rsid: str,
        description: str,
        variations: list,
        stabilized_orientation: str,
        is_flipped: bool,
        is_interesting: bool,
        is_abnormal: bool,
    ) -> dict:
        genotype = ""
        if rsid.lower() in self.enriched_snps.keys():
            genotype = self.personal_snps[rsid.lower()]
            if is_flipped:
                genotype += "<br><i>flipped<br>{}</i>".format(
                    self.enriched_snps[rsid.lower()]
                )
        else:
            genotype = "(-;-)"

        return {
            "Name": rsid,
            "Description": description,
            "Genotype": str(genotype),
            "Variations": str.join("<br>", variations),
            "StabilizedOrientation": stabilized_orientation,
            "IsInteresting": "Yes" if is_interesting else "No",
            "IsAbnormal": "Yes" if is_abnormal else "No",
        }

    def format_cell(
        self: Self, rsid: str, variation: list, stabilized_orientation: str
    ) -> str:
        genotype = variation[0]
        if (
            rsid.lower() in self.enriched_snps.keys()
            and self.enriched_snps[rsid.lower()] == genotype
            # and stabilized_orientation == "plus"
        ):
            return "<b>" + str.join(" ", variation) + "</b>"
        else:
            return str.join(" ", variation)

    def is_interesting(self: Self, variation: list) -> bool:
        if len(variation) > 2 and not variation[2].startswith("common"):
            return True

        return False

    def is_abnormal(self: Self, rsid: str, variation: list) -> bool:
        if (
            rsid.lower() in self.enriched_snps.keys()
            and self.enriched_snps[rsid.lower()] == variation[0]
            and len(variation) > 2
            and not variation[2].startswith(("common", "normal", "average"))
        ):
            return True

        return False

    def create_list(self: Self):
        self.rsid_list = []
        messaged_once = False
        for rsid, values in self.rsid_info.items():
            self.enriched_snps[rsid.lower()] = self.personal_snps[rsid.lower()]
            if "StabilizedOrientation" in values:
                stbl_orient = values["StabilizedOrientation"]
                flipped_data = self.flip_alleles(
                    rsid=rsid.lower(),
                    genotype=self.personal_snps[rsid.lower()],
                    stabilized_orientation=stbl_orient,
                )
            else:
                stbl_orient = "Old Data Format"
                if not messaged_once:
                    logger.error(
                        "Old Data Detected, Will not display variations bolding with old data."
                    )
                    logger.error("See ReadMe for more details")
                    messaged_once = True

            interesting_snp = False
            abnormal_snp = False
            for variation in values["Variations"]:
                if self.is_interesting(variation):
                    interesting_snp = True
                    continue

            for variation in values["Variations"]:
                if self.is_abnormal(rsid, variation):
                    abnormal_snp = True
                    continue

            variations = [
                self.format_cell(rsid, variation, stbl_orient)
                for variation in values["Variations"]
            ]

            maker = self.create_entry(
                rsid,
                values["Description"],
                variations,
                stbl_orient,
                flipped_data["flipped"],
                interesting_snp,
                abnormal_snp,
            )

            self.rsid_list.append(maker)

        export_to_file(data=self.rsid_list, filename="result_table.json")
        logger.debug(json.dumps(self.rsid_list[:5]))

    def export(self: Self):
        export_to_file(data=self.rsid_info, filename="results.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--filepath",
        help="Filepath for Ancestry raw data to be used for import",
        required=False,
    )

    args = vars(parser.parse_args())

    if args["filepath"]:
        personal = PersonalData(args["filepath"])
        snps_of_interest = {}
        for rsid, gene in personal.snps.items():
            if personal.hasGenotype(rsid):
                snps_of_interest[rsid] = gene
        logger.info(
            "Found {} SNPs to be mapped to SNPedia".format(len(snps_of_interest))
        )

    SNPCrawl(rsid_file="results.json", snp_file="personal_snps.json")
