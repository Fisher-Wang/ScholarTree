import os

from notion_client import Client
from scholarly import scholarly

from notion_database.client import Cell, DatabaseClient
from notion_database.enums import PROPERTY_TYPE
from utils.safe_get import safe_get

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


def get_scholar_names(notion: Client):
    db_rows = notion.databases.query(database_id=DATABASE_ID)
    names = [
        safe_get(row, "properties.Name.title.0.plain_text")
        for row in db_rows["results"]
    ]
    return names


def update_citations(notion: Client, scholar_names=None):
    scholar_names = get_scholar_names(notion) if not scholar_names else scholar_names
    citations = get_citations(scholar_names)

    template_cells = [
        Cell(type=PROPERTY_TYPE.TITLE, name="Name", data=""),
        Cell(type=PROPERTY_TYPE.NUMBER, name="Citations", data=""),
    ]

    database = DatabaseClient(DATABASE_ID, notion, template_cells)

    for name, citation in citations.items():
        database.updateByTitle("Name", name, Citations=citation)
