import argparse
import json
import logging
import os

import requests
from typing_extensions import Self

logger = logging.getLogger("genome_importer")
logging.basicConfig()
logger.setLevel("INFO")


class PersonalData:
    def __init__(self: Self, file_path: str) -> None:
        if os.path.exists(file_path):
            self.read_data(file_path)
            self.export()

    def read_data(self: Self, file_path: str) -> None:
        # grab relevant data from the raw DNA file
        relevant_data = []
        with open(file_path) as file:
            for line in file.readlines():
                if line.startswith("#") or line.startswith(
                    "rsid"
                ):  # this is specific to Ancestry raw file
                    # skip comments and headers
                    continue
                relevant_data.append(line.strip())

        # crawl SNPedia for the available RSIDs
        snpedia_rsids = SNPediaRSIDs()
        known_rsids = dict(
            zip(snpedia_rsids.known, [i for i in range(len(snpedia_rsids.known))])
        )  # use dict for faster lookups

        personal_data = []
        # split lines into separate items
        for line in relevant_data:
            personal_data.append(line.split("\t"))

        self.personal_data = []
        # we will work only with rsids that exist both in personal raw and inside snpedia
        for item in personal_data:
            snp = item[0]
            if snp.lower() in known_rsids:
                self.personal_data.append(item)

        self.snps = {}
        for item in self.personal_data:
            rsid = item[0]
            if len(item) > 3:
                allele1 = item[3].strip()
                allele2 = item[4].strip()
                self.snps[rsid] = "({};{})".format(allele1, allele2)

    def hasGenotype(self: Self, rsid: str) -> bool:
        genotype = self.snps[rsid]
        return not genotype == "(-;-)"

    def export(self: Self) -> None:
        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir

        file_path = os.path.join(joiner, "data", "personal_snps.json")
        with open(file_path, "w") as json_file:
            json.dump(self.snps, json_file)


class SNPediaRSIDs:
    def __init__(self: Self) -> None:
        if not self.last_session_exists():
            self.crawl()
            self.export()
        else:
            self.load()

    def load(self: Self) -> None:
        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir

        filepath = os.path.join(joiner, "data", "snpedia_snps.json")
        with open(filepath) as f:
            self.known = json.load(f)

    def last_session_exists(self: Self) -> None:
        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir

        filepath = os.path.join(joiner, "data", "snpedia_snps.json")
        return os.path.isfile(filepath)

    def crawl(self: Self, cmcontinue: str = None) -> None:
        count = 0
        self.known = []

        category_member_limit = 500
        snpedia_initial_url = "https://bots.snpedia.com/api.php?action=query&list=categorymembers&cmtitle=Category:Is_a_snp&cmlimit={}&format=json".format(
            category_member_limit
        )

        logger.info("Grabbing known SNPs")
        if not cmcontinue:
            curgen = snpedia_initial_url
            response = requests.get(curgen)
            jd = response.json()

            cur = jd["query"]["categorymembers"]
            for item in cur:
                self.known += [item["title"].lower()]
            cmcontinue = jd["continue"]["cmcontinue"]

        while cmcontinue:
            curgen = "{}&cmcontinue={}".format(snpedia_initial_url, cmcontinue)
            response = requests.get(curgen)
            jd = response.json()
            cur = jd["query"]["categorymembers"]
            for item in cur:
                self.known += [item["title"].lower()]
            try:
                cmcontinue = jd["continue"]["cmcontinue"]
            except KeyError:
                cmcontinue = None
            count += 1

    def export(self: Self) -> None:
        if os.path.exists("SNPedia"):
            joiner = os.path.join(os.path.curdir, "SNPedia")
        else:
            joiner = os.path.curdir

        filepath = os.path.join(joiner, "data", "snpedia_snps.json")
        with open(filepath, "w") as jsonfile:
            json.dump(self.known, jsonfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--filepath",
        help="Filepath for json dump to be used for import",
        required=False,
    )

    args = vars(parser.parse_args())

    if args["filepath"]:
        pd = PersonalData(file_path=args["filepath"])
        logger.info(
            "Number of SNPs in the raw data that correlate to the SNPedia: {}".format(
                len(pd.snps)
            )
        )
