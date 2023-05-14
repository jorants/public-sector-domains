"""
Code for the commandline functionality.
"""

import os
import shutil

import click
from tabulate import tabulate

from .base import _all_getters, run_all, run_by_names, run_due
from .common import RunResult
from .db import clean_db, clear_db, create_tables
from .output import output_to_csv, output_to_json, update_readme


@click.group()
def main():
    pass


@main.command("list")
def list_getters():
    for g in _all_getters:
        print(g.name)


@main.group(help="Run the getters")
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


@run.command(help="Runs all getters that have not been run for a while")
def due():
    res = run_due()
    print_result(res)


@main.group(help="Contains subcommands to do with database mangement.")
def db():
    pass


@db.command(help="Setup the database and tables")
def create():
    create_tables()


@db.command(help="Removes old results and getters from the database.")
def clean():
    clean_db()


@db.command(help="Fully empties the database")
def clear():
    clear_db()


@main.group(help="Contains subcommands to dump information from the database")
def export():
    pass


@export.command()
@click.argument("csvfile", default="results/result.csv", type=click.Path())
def csv(csvfile):
    output_to_csv(csvfile)


@export.command()
@click.argument("jsonfile", default="results/result.json", type=click.Path())
def json(jsonfile):
    output_to_json(jsonfile)


@export.command(help="Writes the README.md file for the results branch")
@click.argument("readme", default="results/README.md", type=click.Path())
def readme(readme):
    update_readme(readme)


@export.command(help="Outputs all formats to `results/`")
def full():
    if not os.path.exists("results"):
        os.makedirs("results")
    update_readme("result/README.md")
    output_to_json("results/result.json")
    output_to_csv("results/result.csv")
    shutil.copyfile("results.db", "results/result.db")


if __name__ == "__main__":
    main()
