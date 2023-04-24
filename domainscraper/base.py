"""
Basic handeling of the getter functions.

"""
import timeit

from .common import Getter, GetterDesc, RunResult
from .db import get_due

_all_getters: list[GetterDesc] = []


def getter(f: Getter) -> Getter:
    global _all_getters
    _all_getters.append(GetterDesc(function=f, name=f.__name__))
    return f


# This ensures all getters will be found
from .getters import *  # noqa: F403, E402, F401


def run_getter(thegetter: GetterDesc) -> RunResult:
    print("Starting getter {thegetter.name}...")
    start = timeit.default_timer()
    try:
        res = list(thegetter.function())
    except Exception as e:
        stop = timeit.default_timer()
        print("Getter {thegetter.name} finished with error: {e}")
        return RunResult(
            success=False, exception=e, getter_name=thegetter.name, time=stop - start
        )

    stop = timeit.default_timer()
    print(
        "Getter {thegetter.name} finished succesfully after {int(stop-start}) seconds with {len(res)} domains."
    )
    return RunResult(
        success=True, domains=res, getter_name=thegetter.name, time=stop - start
    )


def run_by_name(name: str) -> RunResult:
    thegetter = next((g for g in _all_getters if g.name == name.strip()), None)
    if thegetter is None:
        raise ValueError(f"No getter named {name}")
    return run_getter(thegetter)


def run_by_names(names: list[str]) -> list[RunResult]:
    return [run_by_name(name) for name in names]


def run_all() -> list[RunResult]:
    return [run_getter(g) for g in _all_getters]


def run_due() -> list[RunResult]:
    names = get_due()
    return run_by_names(names)
