"""
Code for the commandline functionality.
"""

import click
from tabulate import tabulate

from .base import run_all, run_by_names, run_due
from .common import RunResult


@click.group()
def main():
    pass


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
    pass


@db.command()
def clean():
    pass


@db.command()
def clear():
    pass


@main.group()
def export():
    pass


@export.command()
def csv():
    pass


@export.command()
def json():
    pass


# def main():
#     if len(sys.argv) > 1:
#         results = [run_by_name(arg) for arg in sys.argv[1:]]
#     else:
#         results = run_all()
#     print(
#         tabulate(
#             [
#                 {
#                     "Name": r.getter_name,
#                     "Status": "Success" if r.success else "Failed",
#                     "Description": f"Found {len(r.domains)} domains"
#                     if r.success and r.domains is not None
#                     else str(r.exception),
#                 }
#                 for r in results
#             ]
#         )
#     )

#     output_to_csv("out.csv", results)


if __name__ == "__main__":
    main()
