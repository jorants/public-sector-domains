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


class GetterInfo(Base):
    name = CharField(unique=True)
    last_run = DateTimeField(index=True)
    time_seconds = IntegerField()
    success = IntegerField()
    number_found = IntegerField(null=True)
    error = CharField(null=True)


class DomainInfo(Base):
    country = CharField(index=True)
    category = CharField(index=True)
    subcategory = CharField(index=True)
    domain = CharField(unique=True)
    meta = JSONField()
    last_found = DateTimeField(index=True)
    first_found = DateTimeField(index=True)
    found_by = ForeignKeyField(GetterInfo, backref="all_found")


def handle_result(result: RunResult):
    now = datetime.now()
    # Create or overwrite due to uniqueness of name
    getter_id = (
        GetterInfo.insert(
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
            conflict_target=GetterInfo.name,
            preserve=[
                GetterInfo.last_run,
                GetterInfo.time_seconds,
                GetterInfo.success,
                GetterInfo.number_found,
                GetterInfo.error,
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
            found_by=getter_id,
        )
        for d in result.domains
    ]

    with db.atomic():
        for batch in chunked(rows_to_add, 800):
            DomainInfo.insert_many(batch).on_conflict(
                "update",
                conflict_target=DomainInfo.domain,
                preserve=[
                    DomainInfo.country,
                    DomainInfo.category,
                    DomainInfo.subcategory,
                    DomainInfo.meta,
                    DomainInfo.last_found,
                    DomainInfo.found_by,
                ],
            ).execute()


def get_due() -> list[str]:
    """
    We need to query all getters, as the logic is to much for a database query
    A getter is due if:
      It has been more than 90 days
      It failed last time
      If the number of seconds for it last run is more than 20 times the hnumber of days since that run. (140 second run = every week, 30 minute run = every three months)
    """
    from .base import _all_getters

    now = datetime.now()
    all_getter_db = list(GetterInfo.select())
    from_db = [
        s.name
        for s in all_getter_db
        if ((now - s.last_run) / DAY > min(90, s.time_seconds / 20) or not s.success)
    ]
    db_names = [s.name for s in all_getter_db]
    return from_db + [
        getter.name for getter in _all_getters if getter.name not in db_names
    ]


def create_tables():
    db.create_tables([GetterInfo, DomainInfo])


def remove_old_getters():
    """
    Removes all:
      - Non-existing getters
      - Domains belonging to those getters
    """
    from .base import _all_getters

    in_db = set(GetterInfo.select().distinct())
    in_code = set(_all_getters)
    to_remove = in_db - in_code
    for getter in to_remove:
        DomainInfo.delete().join(GetterInfo).where(GetterInfo.name == getter).execute()
        GetterInfo.delete().where(GetterInfo.name == getter).execute()


def remove_old_results():
    """
    Removes all domains not found in last run
    """
    DomainInfo.delete().join(GetterInfo).where(
        GetterInfo.last_run != DomainInfo.last_found
    ).execute()


def clean_db():
    """
    Removes all:
      - Non-existing scrapers (old scrapers)
      - Domains belonging to those scrapers
      - Domains not found in last run
    """
    remove_old_getters()
    remove_old_results()


def clear_db():
    """
    Removes all data from the database.
    """
    DomainInfo.delete().execute()
    GetterInfo.delete().execute()


if __name__ == "__main__":
    create_tables()
