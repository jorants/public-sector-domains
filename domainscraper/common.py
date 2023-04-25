"""
THis file contains common data types.
"""
import dataclasses
import urllib.parse
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime

# StrEnum in 3.11 should be used in the future.
from enum import Enum, auto
from typing import Iterable

base_types = str | int | float | bool | None
simple_types = base_types | list[base_types] | tuple[base_types] | dict[str, base_types]
meta_type = dict[str, simple_types]


class Country(Enum):
    NL = auto()
    EU = auto()

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__


class Category(Enum):
    Government = auto()
    Healthcare = auto()
    Education = auto()

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__


@dataclass
class Domain:
    """
    A domain object always has the following fields:

      - domain:
           The domain name that was found.
           This is the pure domain (possibly with subdomain),
           any other URL components will be stripped.
      - country:
           This is an Enum type that takes country codes as values
           and should be one of the predefined list.
      - catogory:
           Also an Enum type, these are universal categories.
           Scanners for different countries should still use the same caterogy names.
      - subcategory:
           This is a free string, as this might change per country.
           Where possible use the english name.

    There is also an optinal meta field for any other information that is gathered
    about the domain (e.g., vister numbers, data protection officer)
    """

    domain: str
    found_on: datetime = field(init=False, default_factory=datetime.now)
    country: Country
    category: Category
    sub_category: str
    # meta: Mapping[Any,Any] = field(default_factory=dict)
    meta: meta_type = field(default_factory=dict)

    def __post_init__(self) -> None:
        if "//" not in self.domain and not self.domain.startswith("http"):
            self.domain = f"http://{self.domain}"
        parsed = urllib.parse.urlparse(self.domain)
        if parsed.hostname is None:
            print(parsed)
            raise ValueError(f"Url does not contian hostname: {self.domain}")
        self.domain = parsed.hostname

    def __str__(self) -> str:
        return f"{self.domain} ({self.country.name}, {self.category.name}-{self.sub_category})"

    def __repr__(self) -> str:
        return str(self)

    asdict = dataclasses.asdict


Getter = Callable[[], Iterable[Domain]]


@dataclass
class GetterDesc:
    """Result of a getters run"""

    function: Getter
    name: str


@dataclass
class RunResult:
    """Result of a getters run"""

    success: bool
    getter_name: str
    time: float
    exception: Exception | None = None
    domains: Sequence[Domain] | None = None

    def __post_init__(self) -> None:
        from . import db

        db.handle_result(self)
