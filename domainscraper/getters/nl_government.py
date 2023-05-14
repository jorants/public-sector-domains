import time
from typing import Iterable
from urllib.parse import urljoin

from bs4 import Tag

from ..getterutils import (
    Category,
    Country,
    Domain,
    dicts_to_domains,
    dicts_translate,
    get_excel_sheet,
    get_soup,
    getter,
    meta_type,
)


def kvk_to_url(kvknummer: str | int) -> str | None:
    """
    Scrapes the KvK website to learn a domain name corresponding with a kvk number
    """
    if isinstance(kvknummer, int):
        kvknummer = str(kvknummer)
    base = "https://www.kvk.nl/orderstraat/product-kiezen/"
    soup = get_soup(base, params={"kvknummer": kvknummer})
    time.sleep(1)
    data = soup.find("div", {"class": "info show"})
    if data is None:
        return None

    a_ell = data.find("a")
    if a_ell is not None and not isinstance(a_ell, int):
        url = a_ell.text.strip()
        if url.strip():
            return url.strip()
    return None


# Sorted in order of importance. If multple types are present, the top one is picked.
TYPE_TRANSLATION = {
    "Kabinet van de Koning": "kabinet van de koning",
    "Hoog College van Staat": "hoog college van staat",
    "Caribisch openbaar lichaam": "caribisch openbaar lichaam",
    "Zelfstandig bestuursorgaan": "independent governing body",
    "Ministerie": "ministry",
    "Provincie": "province",
    "Gemeente": "municipality",
    "Waterschap": "waterschap",
    "Rechtspraak": "legal system",
    "Agentschap": "agency",
    "Interdepartementale commissie": "interdepartmental committee",
    "Koepelorganisatie": "koepelorganisatie",
    "Politie en brandweer": "emergency services",
    "Adviescollege": "advisory board",
    "Openbaar lichaam voor beroep en bedrijf": "openbaar lichaam voor beroep en bedrijf",
    "Grensoverschrijdend regionaal samenwerkingsorgaan": "grensoverschrijdend regionaal samenwerkingsorgaan",
    "Regionaal samenwerkingsorgaan": "regionaal samenwerkingsorgaan",
    "Organisatie met overheidsbemoeienis": "organisatie met overheidsbemoeienis",
    "Organisatieonderdeel": "suborganisation",
}
TYPE_ORDER = list(TYPE_TRANSLATION)
TYPE_ORDER_PARSED = list(TYPE_TRANSLATION.values())


def type_order(typ: str) -> int:
    if typ in TYPE_ORDER:
        return TYPE_ORDER.index(typ)
    else:
        return 1000


def handle_org(org: Tag) -> meta_type:
    """
    Parses a single organization tag form organisaties.overheid.nl into a dict
    """
    res: meta_type = {}
    for ch in org.contents:
        if not isinstance(ch, Tag):
            continue
        if ch.name == "naam":
            res["name"] = ch.text.strip()
        elif ch.name == "types":
            types = [x.text for x in ch.contents]
            types.sort(key=type_order)
            res["types"] = list(types)
            res["type"] = types[0]
        elif ch.name == "adressen":
            for adress in ch.contents:
                if not isinstance(adress, Tag):
                    continue
                fields = {
                    item.name: item.text.strip()
                    for item in adress.contents
                    if isinstance(item, Tag)
                }
                typ = str(fields.pop("type"))
                res[typ] = dict(fields)
        elif ch.name == "identificatiecodes":
            kvk = ch.find("resourceIdentifier", {"p:naam": "KVK-nummer"})
            if kvk is not None:
                res["kvk"] = kvk.text.strip()
        elif ch.name == "contact":
            for typ, key in [
                ("telefoonnummer", "nummer"),
                ("emailadres", "email"),
                ("internetadres", "url"),
            ]:
                all_items: dict[str, str] = dict()
                i = 0

                for item in (tag for tag in ch.find_all(typ) if isinstance(tag, Tag)):
                    label = item.find("label")
                    value = item.find(key)
                    if value is None:
                        continue
                    if label is not None:
                        all_items[label.text] = value.text
                    else:
                        all_items[f"other_{i}"] = value.text
                        i += 1
                res[typ] = dict(all_items)
            assert isinstance(res["internetadres"], dict)
            res["internetadres"].update(
                {
                    f"contactpagina_{i}": x.text
                    for i, x in enumerate(
                        item
                        for item in ch.find_all("p:contactpagina")
                        if isinstance(item, Tag)
                    )
                }
            )
    assert isinstance(res["internetadres"], dict)
    res["internetadres"] = list(res["internetadres"].values())

    return res


def add_domain_from_kvk(org: meta_type) -> meta_type:
    if not org["internetadres"] and "kvk" in org:
        # back-up option if no domainname is supplied, the kvk is checked.
        assert isinstance(org["kvk"], str)
        url = kvk_to_url(org["kvk"])
        if url:
            org["internetadres"] = [url]
    if org["internetadres"]:
        print(org["internetadres"])
    return org


# @getter
def nl_organisaties_overheid() -> Iterable[Domain]:
    soup = get_soup("https://organisaties.overheid.nl/archive/exportOO.xml", xml=True)

    orgs = soup.find("organisaties")
    if not isinstance(orgs, Tag):
        raise Exception("Format of organisaties.overheid.nl xml seems to have changed")

    orgs_parsed = [handle_org(org) for org in orgs.contents if isinstance(org, Tag)]
    results_org = [add_domain_from_kvk(org) for org in orgs_parsed]
    results_org.sort(
        key=lambda x: type_order(x["type"]) if isinstance(x["type"], str) else 9999
    )
    # TODO map type translation?
    return dicts_to_domains(
        results_org,
        "internetadres",
        Country.NL,
        Category.Government,
        sub_category_collumn="type",
    )


@getter
def nl_rijksoverheids_webregister() -> Iterable[Domain]:
    """
    The dutch nationaal government publicises a ODS file of all websites they run.
    The filename changes over time but the page witht the link does not (appart form the filename).
    """
    base_url = "https://www.communicatierijk.nl/vakkennis/rijkswebsites/verplichte-richtlijnen/websiteregister-rijksoverheid"  # noqa: E501
    soup = get_soup(base_url)
    # The link is in the 'intro' paragraph, and is the only link their.
    intro = soup.find("div", {"class": "intro"})
    if not isinstance(intro, Tag):
        raise Exception("The websiteregister page seems to have changed format")

    atag = intro.find("a")
    if not isinstance(atag, Tag):
        raise Exception("The websiteregister page seems to have changed format")

    odspath = str(atag["href"])

    ods_url = urljoin(base_url, odspath)

    entries = get_excel_sheet(ods_url, header=1)

    entries = dicts_translate(
        {
            "URL": "URL",
            "Organisatie": "organisation",
            "Suborganisatie": "suborganisation",
            "Afdeling": "department",
            "Bezoeken/mnd": "visitors/month",
            "Platformgebruik": "hosting platform",
        },
        entries,
    )

    return dicts_to_domains(
        entries, "URL", Country.NL, Category.Government, "national government"
    )
