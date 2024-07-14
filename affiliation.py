import os

from notion_client import Client

from utils.affiliation import get_scholar_affiliation
from utils.common import get_scholar_names, safe_get

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def get_homepages(notion: Client, names: list[str]):
    db_rows = notion.databases.query(database_id=DATABASE_ID)
    for row in db_rows["results"]:
        name = safe_get(row, "properties.Name.title.0.plain_text")
        if name in names:
            homepage = safe_get(row, "properties.Homepage.url")
            affiliation = get_scholar_affiliation(homepage)
            print(f"[INFO] Update {name} with affiliation {affiliation}")
            # break


def update_affiliation(notion: Client, scholar_names=None):
    scholar_names = scholar_names or get_scholar_names(notion)
    get_homepages(notion, scholar_names)
