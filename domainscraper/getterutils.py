"""
This file contains helper functions for the getters.
Logic on how to handle the getters belongs in base.py
"""
import os
from collections.abc import Iterable, Mapping
from typing import Any, Callable, Iterator, TypeVar

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from .base import getter  # noqa: F401
from .common import Category, Country, Domain, meta_type


def get_csv_sheet(
    url: str, header: None | int = 0, names: None | list[str] = None
) -> list[dict[str, Any]]:
    df = pd.read_csv(url, on_bad_lines="skip", header=header, names=names)
    df.replace(np.nan, None)
    return [{str(k): v for k, v in d.items()} for d in df.to_dict("records")]


def get_excel_sheet(
    url: str, header: int | list[int] = 0, names: None | list[str] = None
) -> list[dict[str, Any]]:
    df = pd.read_excel(url, header=header, names=names)
    df.replace(np.nan, None)
    return [{str(k): v for k, v in d.items()} for d in df.to_dict("records")]


T = TypeVar("T")


def dict_translate(lookup: Mapping[str, str], dic: dict[str, T]) -> dict[str, T]:
    return {v: dic[k] for k, v in lookup.items() if k in dic}


def dicts_translate(
    lookup: Mapping[str, str], dicts: list[dict[str, T]]
) -> list[dict[str, T]]:
    return [dict_translate(lookup, dic) for dic in dicts]


S = TypeVar("S")

# @overload
# def multi_map(function : Callable[[S], Iterable[T]], source: Iterable[S], fold_lists : Literal[True]) -> list[T]: ...

# @overload
# def multi_map(function : Callable[[S], T], source: Iterable[S], fold_lists : Literal[False]) -> list[T]: ...


def multi_map(function: Callable[[S], T], source: Iterable[S]) -> list[T]:
    from multiprocessing import Pool

    # We assume we will be io limited, so we can make more threaths then if we would be computationally limited
    count = os.cpu_count()
    if count is None:
        count = 4

    with Pool(count * 8) as p:
        result = list(p.map(function, source))

    return list(result)


def multi_map_fold(
    function: Callable[[S], Iterable[T]], source: Iterable[S]
) -> list[T]:
    return [x for itt in multi_map(function, source) for x in itt]


def dicts_to_domains(
    dicts: list[meta_type],
    domain_collumn: str,
    country: Country,
    category: Category,
    sub_category: str | None = None,
    sub_category_collumn: str | None = None,
    meta: meta_type | None = None,
) -> Iterator[Domain]:
    """
    maps a list of dicts to a iterator over Domains.
    meta will be extended with all other collumns.
    domain_collumn is the value to use for the domain name
    domain_collumn may contain lists, in which case multple domains wil be generated
    either sub_category or sub_category_list should be set.
    """

    if meta is None:
        meta = {}

    if sub_category_collumn is not None:
        for x in dicts:
            domain_spec = x.pop(domain_collumn, None)
            if domain_spec is None:
                # allow empty domains, just skip
                continue
            if isinstance(domain_spec, str):
                yield Domain(
                    domain=str(domain_spec),
                    country=country,
                    category=category,
                    sub_category=str(x[sub_category_collumn]),
                    meta={**meta, **x},
                )
            elif isinstance(domain_spec, Iterable):
                for d in domain_spec:
                    yield Domain(
                        domain=str(d),
                        country=country,
                        category=category,
                        sub_category=str(x[sub_category_collumn]),
                        meta={**meta, **x},
                    )

    elif sub_category is not None:
        for x in dicts:
            domain_spec = x.pop(domain_collumn, None)
            if domain_spec is None:
                # allow empty domains, just skip
                continue

            if isinstance(domain_spec, str):
                yield Domain(
                    domain=str(domain_spec),
                    country=country,
                    category=category,
                    sub_category=sub_category,
                    meta={**meta, **x},
                )
            elif isinstance(domain_spec, Iterable):
                for d in domain_spec:
                    yield Domain(
                        domain=str(d),
                        country=country,
                        category=category,
                        sub_category=sub_category,
                        meta={**meta, **x},
                    )

    else:
        raise ValueError("either sub_catogory or sub_catogory_list should be set.")


def get_soup(
    url: str, xml: bool = False, params: None | dict[str, str] = None
) -> BeautifulSoup:
    """
    Gets a beatifullsoup object for a urllib
    """
    req = requests.get(url, params=params)
    if xml:
        soup = BeautifulSoup(req.content, features="xml")
    else:
        soup = BeautifulSoup(req.content, "html.parser")

    return soup
