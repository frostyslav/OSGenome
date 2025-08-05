import json
import os


def export_to_file(data: dict, filename: str) -> None:
    filepath = os.path.join(_get_parent_path(), "data", filename)
    with open(filepath, "w") as json_file:
        json.dump(data, json_file, indent=4)


def load_from_file(filename: str) -> dict:
    filepath = os.path.join(_get_parent_path(), "data", filename)
    if filepath and os.path.isfile(filepath):
        with open(filepath) as f:
            return json.load(f)

    return {}


def _get_parent_path() -> str:
    if os.path.exists("SNPedia"):
        return os.path.join(os.path.curdir, "SNPedia")

    return os.path.curdir
