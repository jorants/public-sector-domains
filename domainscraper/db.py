import json
from datetime import datetime, timedelta

from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
    chunked,
)

from .common import RunResult


class JSONField(TextField):
    """
    Class to "fake" a JSON field with a text field. Not efficient but works nicely
    """

    def db_value(self, value):
        """Convert the python value for storage in the database."""
        return value if value is None else json.dumps(value)

    def python_value(self, value):
        """Convert the database value to a pythonic value."""
        return value if value is None else json.loads(value)


db = SqliteDatabase("results.db")
DAY = timedelta(days=1)


class Base(Model):
    class Meta:
        database = db  # This model uses the "people.db" database.


class Scraper(Base):
    name = CharField(unique=True)
    last_run = DateTimeField(index=True)
    time_seconds = IntegerField()
    success = IntegerField()
    number_found = IntegerField(null=True)
    error = CharField(null=True)


class Domain(Base):
    country = CharField(index=True)
    category = CharField(index=True)
    subcategory = CharField(index=True)
    domain = CharField(unique=True)
    meta = JSONField()
    last_found = DateTimeField(index=True)
    first_found = DateTimeField(index=True)
    found_by = ForeignKeyField(Scraper, backref="all_found")


def handle_result(result: RunResult):
    now = datetime.now()
    # Create or overwrite due to uniqueness of name
    scraper_id = (
        Scraper.insert(
            name=result.getter_name,
            last_run=now,
            time_seconds=result.time,
            success=result.success,
            number_found=len(result.domains)
            if (result.success and result.domains is not None)
            else None,
            error=None if result.success else str(result.exception),
        )
        .on_conflict(
            "update",
            conflict_target=Scraper.name,
            preserve=[
                Scraper.last_run,
                Scraper.time_seconds,
                Scraper.success,
                Scraper.number_found,
                Scraper.error,
            ],
        )
        .execute()
    )
    if not result.success or result.domains is None:
        return
    rows_to_add = [
        dict(
            country=str(d.country),
            category=str(d.category),
            subcategory=str(d.sub_category),
            domain=str(d.domain),
            meta=d.meta,
            last_found=now,
            first_found=now,
            found_by=scraper_id,
        )
        for d in result.domains
    ]

    with db.atomic():
        for batch in chunked(rows_to_add, 800):
            Domain.insert_many(batch).on_conflict(
                "update",
                conflict_target=Domain.domain,
                preserve=[
                    Domain.country,
                    Domain.category,
                    Domain.subcategory,
                    Domain.meta,
                    Domain.last_found,
                    Domain.found_by,
                ],
            ).execute()


def get_due() -> list[str]:
    """
    We need to query all scrapers, as the logic is to much for a database query
    A scraper is due if:
      It has been more than 90 days
      It failed last time
      If the number of seconds for it last run is more than 20 times the hnumber of days since that run. (140 second run = every week, 30 minute run = every three months)
    """
    from .base import _all_getters

    now = datetime.now()
    all_scrapers_db = list(Scraper.select())
    from_db = [
        s.name
        for s in all_scrapers_db
        if ((now - s.last_run) / DAY > min(90, s.time_seconds / 20) or not s.success)
    ]
    db_names = [s.name for s in all_scrapers_db]
    return from_db + [
        scraper.name for scraper in _all_getters if scraper.name not in db_names
    ]


def create_tables():
    db.create_tables([Scraper, Domain])


def remove_old_scrapers():
    """
    Removes all:
      - Non-existing scrapers (old scrapers)
      - Domains belonging to those scrapers
    """
    from .base import _all_getters

    in_db = set(Scraper.select().distinct())
    in_code = set(_all_getters)
    to_remove = in_db - in_code
    for scraper in to_remove:
        Domain.delete().join(Scraper).where(Scraper.name == scraper).execute()
        Scraper.delete().where(Scraper.name == scraper).execute()


def remove_old_results():
    """
    Removes all domains not found in last run
    """
    Domain.delete().join(Scraper).where(Scraper.last_run != Domain.last_found).execute()


def clean_db():
    """
    Removes all:
      - Non-existing scrapers (old scrapers)
      - Domains belonging to those scrapers
      - Domains not found in last run
    """
    remove_old_scrapers()
    remove_old_results()


def clear_db():
    """
    Removes all data from the database.
    """
    Domain.delete().execute()
    Scraper.delete().execute()


if __name__ == "__main__":
    create_tables()
