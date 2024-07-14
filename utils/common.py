import json
import os

from notion_client import Client

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def safe_get(data, dot_chained_keys):
    keys = dot_chained_keys.split(".")
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data


def extract_json_from_response(response):
    # Check if the response starts with a Markdown code block
    if response.startswith("```json") and response.endswith("```"):
        # Extract the JSON portion
        json_str = response[7:-3].strip()
    else:
        json_str = response.strip()

    return json.loads(json_str)


def get_scholar_names(notion: Client):
    db_rows = notion.databases.query(database_id=DATABASE_ID)
    names = [
        safe_get(row, "properties.Name.title.0.plain_text")
        for row in db_rows["results"]
    ]
    return names
