import csv
import json
import pathlib
from datetime import date, datetime
from typing import TypeVar

from tabulate import tabulate

from .db import DomainInfo, GetterInfo

PathLike = TypeVar("PathLike", str, pathlib.Path)


def markdown_results():
    return tabulate(
        [
            {
                "Name": r.name,
                "Status": "Success" if r.success else "Failed",
                "Description": f"Found {r.number_found} domains"
                if r.success
                else str(r.error),
            }
            for r in GetterInfo.select()
        ],
        headers="keys",
        tablefmt="github",
    )


README = """# Public Sector Domains - Results

**This repository is temporarly hosted here, it will likely be moved in the future**

This is the *result* branch of this project, check out the [main branch](https://github.com/jorants/public-sector-domains) for the underlying code.

"""


def update_readme(path: PathLike) -> None:
    with open(path, "w") as fp:
        fp.write(f"{README}\n\n## Report\n\n{markdown_results()}")


def get_domains_as_dict():
    results = list(
        DomainInfo.select(DomainInfo, GetterInfo.name).join(GetterInfo).dicts()
    )
    for r in results:
        r["getter_name"] = r.pop("name")

    return results


def output_to_csv(path: PathLike) -> None:
    results = get_domains_as_dict()
    with open(path, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def output_to_json(path: PathLike) -> None:
    results = get_domains_as_dict()
    with open(path, "w") as jsonfile:
        json.dump(results, jsonfile, default=json_serial)
