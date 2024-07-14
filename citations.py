import datetime
import os

from notion_client import Client
from scholarly import scholarly

from notion_database.client import Cell, DatabaseClient
from notion_database.enums import PROPERTY_TYPE
from utils.common import get_scholar_names, safe_get

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def get_citations(names):
    rst = {}
    for i, name in enumerate(names):
        search_query = scholarly.search_author(name)

        for _ in range(1):
            author = next(search_query, None)
            if author is None:
                break

            if author["name"].lower().strip().replace(
                " ", ""
            ) == name.lower().strip().replace(" ", ""):
                rst[name] = author["citedby"]
                print(
                    f"[INFO] Find scholar {author['name']} with citation count {author['citedby']}"
                )
                break
            else:
                print(f"[INFO] Result {author['name']} not match {name}")

        if name not in rst:
            print(f"[INFO] Cannot find scholar {name}")

    return rst


def filter_scholar_names(notion: Client, names):
    db_rows = notion.databases.query(database_id=DATABASE_ID)
    names_filtered = []
    for row in db_rows["results"]:
        name = safe_get(row, "properties.Name.title.0.plain_text")
        if name in names:
            citation_update_time = safe_get(
                row, "properties.Citations last updated time.date.start"
            )
            if citation_update_time:
                citation_update_time = datetime.datetime.fromisoformat(
                    citation_update_time
                )
                time_diff = (
                    citation_update_time.astimezone()
                    - datetime.datetime.now().astimezone()
                )
                if time_diff > datetime.timedelta(days=7):
                    names_filtered.append(name)
            else:
                names_filtered.append(name)
    return names_filtered


def update_citations(notion: Client, scholar_names=None):
    scholar_names = get_scholar_names(notion) if not scholar_names else scholar_names
    scholar_names = filter_scholar_names(notion, scholar_names)
    print(f"[INFO] Updating citations for {scholar_names}")
    citations = get_citations(scholar_names)

    template_cells = [
        Cell(type=PROPERTY_TYPE.TITLE, name="Name", data=""),
        Cell(type=PROPERTY_TYPE.NUMBER, name="Citations", data=""),
        Cell(type=PROPERTY_TYPE.DATE, name="Citations last updated time", data=""),
    ]

    database = DatabaseClient(DATABASE_ID, notion, template_cells)

    for name, citation in citations.items():
        date = datetime.datetime.now().astimezone().isoformat()
        database.updateByTitle(
            "Name", name, **{"Citations": citation, "Citations last updated time": date}
        )
