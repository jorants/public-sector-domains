import sys

from tabulate import tabulate

from .base import run_all, run_by_name
from .output import output_to_csv

if __name__ == "__main__":
    if len(sys.argv) > 1:
        results = [run_by_name(arg) for arg in sys.argv[1:]]
    else:
        results = run_all()
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
                for r in results
            ]
        )
    )

    output_to_csv("out.csv", results)
