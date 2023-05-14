from ..getterutils import (
    Category,
    Country,
    dicts_to_domains,
    dicts_translate,
    get_excel_sheet,
    getter,
)

sheets = {
    "https://www.duo.nl/open_onderwijsdata/images/01.-hoofdvestigingen-basisonderwijs.xlsx": "primary education",
    "https://www.duo.nl/open_onderwijsdata/images/02.-alle-schoolvestigingen-basisonderwijs.xlsx": "primary education",
    "https://www.duo.nl/open_onderwijsdata/images/08.-hoofdvestigingen-sbo,-so-en-vso.xlsx": "speciality education",
    "https://www.duo.nl/open_onderwijsdata/images/09.-alle-vestigingen-speciaal-(basis)onderwijs.xlsx": "speciality education",
    "https://www.duo.nl/open_onderwijsdata/images/01.-hoofdvestigingen-vo.xlsx": "secondary education",
    "https://www.duo.nl/open_onderwijsdata/images/02.-alle-vestigingen-vo.xlsx": "secondary education",
    "https://www.duo.nl/open_onderwijsdata/images/04.-samenwerkingsverbanden-passend-onderwijs-vo.xlsx": "samenwerkingsverband passend onderwijs",
    "https://duo.nl/open_onderwijsdata/images/01.-adressen-instellingen.xlsx": "trade school",
    "https://duo.nl/open_onderwijsdata/images/01.-instellingen-hbo-en-wo.xlsx": "university",
}


@getter
def nl_onderwijs_all():
    result = []
    for url, typ in sheets.items():
        data = get_excel_sheet(url)
        remapped = dicts_translate(
            {
                "INSTELLINGSNAAM": "name",
                "ADRES": "adres",
                "STRAATNAAM": "adres_straat",
                "HUISNUMMER-TOEVOEGING": "adres_nummer",
                "POSTCODE": "postcode",
                "PLAATSNAAM": "plaats",
                "CORRESPONDENTIEADRES": "correspondentieadres",
                "STRAATNAAM CORRESPONDENTIEADRES": "correspondentieadres_straat",
                "HUISNUMMER-TOEVOEGING CORRESPONDENTIEADRES": "correspondentieadres_nummer",
                "POSTCODE CORRESPONDENTIEADRES": "correspondentieadres_postcode",
                "PLAATS CORRESPONDENTIEADRES": "correspondentieadres_plaats",
                "PLAATSNAAM CORRESPONDENTIEADRES": "correspondentieadres_plaats",
                "DENOMINATIE": "denominatie",
                "KVK-NUMMER": "kvknummer",
                "TELEFOONNUMMER": "telefoonnummer",
                "INTERNET": "domain",
                "INTERNETADRES": "domain",
            },
            data,
        )
        result += dicts_to_domains(
            remapped, "domain", Country.NL, Category.Education, typ
        )
    return result
