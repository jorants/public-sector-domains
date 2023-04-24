from datetime import datetime, timedelta

from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
)

from .common import RunResult

db = SqliteDatabase("results.db")
DAY = timedelta(days=1)


class Base(Model):
    class Meta:
        database = db  # This model uses the "people.db" database.


class Scraper(Base):
    name = CharField()
    last_run = DateTimeField(index=True)
    time_seconds = IntegerField()
    success = IntegerField()
    number_found = IntegerField()
    error = CharField()


class Domain(Base):
    country = CharField(index=True)
    category = CharField(index=True)
    subcategory = CharField(index=True)
    domain = CharField(unique=True)
    last_found = DateTimeField(index=True)
    first_found = DateTimeField(index=True)
    found_by = ForeignKeyField(Scraper, backref="all_found")


def handle_result(result: RunResult):
    pass


def get_due() -> list[str]:
    # We need to query all scrapers, as the logic is to much for a database query
    # A scraper is due if:
    #   It has been more than 90 days
    #   It failed last time
    #   If the number of seconds for it last run is more than 20 times the hnumber of days since that run. (140 second run = every week, 30 minute run = every three months)
    now = datetime.now()
    return [
        s.name
        for s in Scraper.select()
        if ((now - s.last_run) / DAY > min(90, s.time_seconds / 20) or not s.success)
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
