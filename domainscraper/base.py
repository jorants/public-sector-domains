from .common import Getter, GetterDesc, RunResult

_all_getters: list[GetterDesc] = []


def getter(f: Getter) -> Getter:
    global _all_getters
    _all_getters.append(GetterDesc(function=f, name=f.__name__))
    return f


# This ensures all getters will be found
from .getters import *  # noqa: F403, E402, F401


def run_getter(thegetter: GetterDesc) -> RunResult:
    print(f"Running {thegetter.name}...")
    try:
        res = list(thegetter.function())
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        return RunResult(success=False, exception=e, getter_name=thegetter.name)
    return RunResult(success=True, domains=res, getter_name=thegetter.name)


def run_by_name(name: str) -> RunResult:
    thegetter = next((g for g in _all_getters if g.name == name.strip()), None)
    if thegetter is None:
        raise ValueError(f"No getter named {name}")
    return run_getter(thegetter)


def run_all() -> list[RunResult]:
    return [run_getter(g) for g in _all_getters]
