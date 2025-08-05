import argparse
import json
import logging
import os
import urllib.request

from bs4 import BeautifulSoup
from genome_importer import PersonalData
from typing_extensions import Self

logger = logging.getLogger("data_crawler")
logging.basicConfig()
logger.setLevel("DEBUG")


class SNPCrawl:
    def __init__(self: Self, file_path: str = None, snp_path: str = None):
        if file_path and os.path.isfile(file_path):
            self.rsid_info = self.import_json(filepath=file_path)
        else:
            self.rsid_info = {}

        if snp_path and os.path.isfile(snp_path):
            self.personal_snps = self.import_json(filepath=snp_path)
        else:
            self.personal_snps = {}

        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir

        file_path = os.path.join(joiner, "data", "results.json")
        if file_path and os.path.isfile(file_path):
            with open(file_path) as jsonfile:
                self.rsid_info = json.load(jsonfile)
        else:
            self.rsid_info = {}

        self.rsid_list = []

        if self.personal_snps:
            self.init_crawl(self.personal_snps)
        self.export()
        self.create_list()

    def init_crawl(self: Self, rsids: dict):
        count = 0
        for rsid, gene in rsids.items():
            logger.info("Grabbing data about SNP: {}".format(rsid))
            self.grab_table(rsid)
            count += 1
            if count % 10 == 0:
                logger.info("%i out of %s completed" % (count, len(rsids)))
                logger.info("Exporting current results...")
                self.export()
                break

    def grab_table(self, rsid):  # noqa C901
        try:
            url = "https://bots.snpedia.com/index.php/" + rsid
            if rsid not in self.rsid_info.keys():
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

                logger.info(
                    "{} stabilized orientation: {}".format(
                        rsid, self.rsid_info[rsid]["StabilizedOrientation"]
                    )
                )

                if description:
                    d1 = self.table_to_list(description)
                    self.rsid_info[rsid]["Description"] = d1[0][0]
                    logger.info(
                        "{} description: {}".format(
                            rsid, self.rsid_info[rsid]["Description"]
                        )
                    )
                if table:
                    d2 = self.table_to_list(table)
                    self.rsid_info[rsid]["Variations"] = d2[1:]
                    logger.info(
                        "{} variations: {}".format(
                            rsid, self.rsid_info[rsid]["Variations"]
                        )
                    )
        except urllib.error.HTTPError:
            logger.error(
                "{} was not found or contained no valid information".format(url)
            )

    def table_to_list(self, table):
        rows = table.find_all("tr")
        data = []
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        return data

    def flip_alleles(self: Self, genotype: str, stabilized_orientation: str) -> dict:
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
            return {"genotype": updated_genotype, "flipped": True}
        else:
            return {"genotype": genotype, "flipped": False}

    def make(
        self: Self,
        rsid: str,
        description: str,
        variations: list,
        stabilized_orientation: str,
        is_flipped: bool,
        is_interesting: bool,
    ) -> dict:
        genotype = ""
        if rsid.lower() in self.personal_snps.keys():
            genotype = self.personal_snps[rsid.lower()]
            if is_flipped:
                genotype += "<br><i>flipped</i>"
        else:
            genotype = "(-;-)"

        return {
            "Name": rsid,
            "Description": description,
            "Genotype": str(genotype),
            "Variations": str.join("<br>", variations),
            "StabilizedOrientation": stabilized_orientation,
            "IsInteresting": "★" if is_interesting else "",
        }

    def format_cell(
        self: Self, rsid: str, variation: list, stabilized_orientation: str
    ) -> str:
        genotype = variation[0]
        if (
            rsid.lower() in self.personal_snps.keys()
            and self.personal_snps[rsid.lower()] == genotype
            # and stabilized_orientation == "plus"
        ):
            return "<b>" + str.join(" ", variation) + "</b>"
        else:
            return str.join(" ", variation)

    def is_interesting(self: Self, variation: list) -> bool:
        if len(variation) > 2 and not variation[2].startswith("common"):
            return True

        return False

    def create_list(self: Self):
        messaged_once = False
        for rsid, values in self.rsid_info.items():
            if "StabilizedOrientation" in values:
                stbl_orient = values["StabilizedOrientation"]
                flipped_data = self.flip_alleles(
                    genotype=self.personal_snps[rsid.lower()],
                    stabilized_orientation=stbl_orient,
                )
                self.personal_snps[rsid.lower()] = flipped_data["genotype"]
            else:
                stbl_orient = "Old Data Format"
                if not messaged_once:
                    logger.error(
                        "Old Data Detected, Will not display variations bolding with old data."
                    )
                    logger.error("See ReadMe for more details")
                    messaged_once = True

            interesting_snp = False
            for variation in values["Variations"]:
                if self.is_interesting(variation):
                    interesting_snp = True
                    continue

            variations = [
                self.format_cell(rsid, variation, stbl_orient)
                for variation in values["Variations"]
            ]

            maker = self.make(
                rsid,
                values["Description"],
                variations,
                stbl_orient,
                flipped_data["flipped"],
                interesting_snp,
            )

            self.rsid_list.append(maker)

        logger.debug(self.rsid_list[:5])

    def import_json(self, filepath) -> dict:
        with open(filepath) as jsonfile:
            return json.load(jsonfile)

    def export(self):
        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir
        filepath = os.path.join(joiner, "data", "results.json")
        with open(filepath, "w") as jsonfile:
            json.dump(self.rsid_info, jsonfile)


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

    if os.path.exists("SNPedia"):
        joiner = os.path.join(os.path.curdir, "SNPedia")
    else:
        joiner = os.path.curdir
    file_path = os.path.join(joiner, "data", "personal_snps.json")
    if os.path.isfile(file_path):
        #     with open(file_path) as jsonfile:
        #         rsids = json.load(jsonfile)
        dfCrawl = SNPCrawl(snp_path=file_path)
    else:
        logger.info("No SNPs to crawl")
