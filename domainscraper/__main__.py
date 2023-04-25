"""
Code for the commandline functionality.
"""

import click
from tabulate import tabulate

from .base import _all_getters, run_all, run_by_names, run_due
from .common import RunResult
from .db import clean_db, clear_db, create_tables


@click.group()
def main():
    pass


@main.command("list")
def list_getters():
    for g in _all_getters:
        print(g.name)


@main.group()
def run():
    pass


def print_result(res: list[RunResult]):
    print(
        tabulate(
            [
                {
                    "Name": r.getter_name,
                    "Status": "Success" if r.success else "Failed",
                    "Description": f"Found {len(r.domains)} domains"
                    if r.success and r.domains is not None
                    else str(r.exception),
                }
                for r in res
            ]
        )
    )


@run.command()
def all():
    res = run_all()
    print_result(res)


@run.command()
@click.argument("names", nargs=-1)
def getters(names):
    if not names:
        return 0
    res = run_by_names(names)
    print_result(res)


@run.command()
def due():
    res = run_due()
    print_result(res)


@main.group()
def db():
    pass


@db.command()
def create():
    create_tables()


@db.command()
def clean():
    clean_db()


@db.command()
def clear():
    clear_db()


@main.group()
def export():
    pass


@export.command()
def csv():
    pass


@export.command()
def json():
    pass


if __name__ == "__main__":
    main()
