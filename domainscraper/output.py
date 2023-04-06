import csv
import pathlib
from collections.abc import Sequence
from dataclasses import asdict
from typing import TypeVar

from .common import Domain, RunResult

PathLike = TypeVar("PathLike", str, pathlib.Path)


def without_repeats(results: Sequence[RunResult]) -> list[Domain]:
    seen: set[str] = set()
    filtered = []
    for result in results:
        if result.success and result.domains is not None:
            for domain in result.domains:
                if domain.domain not in seen:
                    seen.add(domain.domain)
                    filtered.append(domain)
    return filtered


def output_to_csv(path: PathLike, results: Sequence[RunResult]) -> None:
    domains = without_repeats(results)
    with open(path, "w") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            extrasaction="ignore",
            fieldnames=[
                "domain",
                "country",
                "category",
                "sub_category",
                "found_on",
                "meta",
            ],
        )
        writer.writeheader()
        writer.writerows((asdict(d) for d in domains))
