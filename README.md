# Public Sector Domains

**This repository is temporarly hosted here, it will likely be moved in the future. We are also still working on the basic infrastructure, so we will add more documentation and feutures in the comming weeks.**

This branch houses the code used for scraping, for the list of domains, see [the result branch](https://github.com/jorants/public-sector-domains/tree/results).

## Background

The goal of this project is to gather domain names in use by government and public sector institutes, for use in research. In particulair, the results are used as an input for [GDPR.Observer](https://github.com/hermescenter/gdpr.observer).

Instead of gathering such lists ones, the project consists of 'getter' scripts that scrape these domains from the web. Some scripts are as simple as downloading a `csv` file, others require more complicated webscraping.
This projects also gives a unified framework for running such scripts, and outputting the results. The goal is to make it minimal work to add new datasets.

The scraping is done periodacly by Bits of Freedom, with faster getters being updated more regulairly.
If you have any questions, please email at `<joran at bitsoffreedom dot nl>`.

## Contributing
If you would like to add a dataset, but you are not a (python) programmer, feel free to open an issue of email to the email adres above, we are happy to help!

You can also fork and create a pull request, either to add a getter or to improve the base code. 

## Development

### Development environment

Please ensure you have [poetry](https://github.com/python-poetry/poetry) installed. Then run
```
poetry install
```
to install all dependencies and create a virtual environment.

You can enter a shell for the virtual enviorment using `poetry shell`.

This also installs [pre-commit](https://pre-commit.com/) and ensures you have pre-commit setup for this repo.

### Running

The module is callable, while in the virtual enviorment (`poetry shell`), you can call it using `python -m domainscraper`.
The command has extensive help output when you run it.

### Datamodel

For each domain the following fields are populated:

 - `domain`, a normalized domain, no `http:\\` prefixes or paths. Might contain a port number.
 - `country`, the country code for the country the institute resides in. `EU` is used for EU wide institutes.
 - `category`, one of a  fixed list of main categories, this list is now limited to:
   - Government
   - Education
   - Healtcare
 - `sub_category`, a free-form string describing a specific category. Where possible the English translation is used. For example, for government domain this might be `municipality`. The convention is to use lower-case names.
 - `found_on`, when the scraper was run to find this domain.
 - `meta`, any other source-specific meta data in JSON format. The top level object should always be a `dict`, and at most two levels of depth should be used for simplicity.

### Adding Getters

Getters can be added by creating a script in `domainscraper/getters`. The filename convention is `<countrycode>_<catogory>_<other description>.py`. A basic example that returns one hard-coded domain would be:
```python
from ..getterutils import (
    Category,
    Country,
    Domain,
    getter,
)

from typing import Iterable

@getter
def nl_example_getter_name() -> Iterable[Domain]:
    return [Domain("www.rijksoverheid.nl",Country.NL,Category.Government,'national',meta={'note':'hardcoded'})]

```

The `@getter` decorator ensures the script will automatically be picked up. A getter is should return a list of `Domain` objects.

`getterutils` contains many more helper functions. Also consider looking at other getters to see these in actions.

*Adding countries and categories*: these can be added by modifying `domainscraper/common.py`.

## Licence

The code and other work in this directory is licenced under the [GPL 3](Licence)
