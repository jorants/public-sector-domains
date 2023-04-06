import re

from ..getterutils import (
    Category,
    Country,
    Domain,
    get_soup,
    getter,
    multi_map,
    multi_map_fold,
)


def clean_up_text(text):
    return re.sub("[ \t\n]+", " ", text)


def page_to_domain(url):
    soup = get_soup(url)

    infodiv = soup.find(class_="modal-address")
    name = clean_up_text(infodiv.find("h2").text.strip())
    typ = clean_up_text(infodiv.find("p", class_="mb-2").text.strip())
    address = clean_up_text(infodiv.find("address").text.strip().replace("\n", " "))
    site = None
    telephone = None
    for link in infodiv.find_all("a", href=True):
        href = link["href"]
        if href.startswith("https://") or href.startswith("http://"):
            site = href
        if href.startswith("tel:"):
            telephone = href.partition(":")[-1]

    if site:
        return Domain(
            site,
            Country.NL,
            Category.Healthcare,
            typ,
            meta={"telephone": telephone, "address": address, "name": name},
        )


def org_searches():
    """
    Gets a list of all organisaiton types.
    As we need to search on at least parameter, and this field is unique for each entry, this seems like a good chooice.
    """
    soup = get_soup("https://www.zorgkaartnederland.nl/overzicht/organisatietypes")
    return [
        f"https://www.zorgkaartnederland.nl{tag['href']}"
        for tag in soup.find_all("a", class_="filter-radio", href=True)
    ]


def iter_links_from_searchpage(searchpage):
    # 20 results per page, no more than 200,000 entries....
    # We quite earlier, but this seems safer than `while True`
    for i in range(1, 10000):
        url = f"{searchpage}/pagina{i}"
        soup = get_soup(url)
        tags = soup.find_all("a", class_="filter-result__name", href=True)
        if len(tags) == 0:
            break
        yield from (f"https://www.zorgkaartnederland.nl{tag['href']}" for tag in tags)


def links_from_searchpage(searchpage):
    return list(iter_links_from_searchpage(searchpage))


@getter
def nl_healtcare_zorgkaart():
    """
    There does not seem to be a general database of healtcare providers publisched by the government, but zorgkaart.nl keeps one.
    The best we can do is scrape their search function...
    """
    org_links = org_searches()
    links = multi_map_fold(links_from_searchpage, org_links)
    return [x for x in multi_map(page_to_domain, links) if x]
