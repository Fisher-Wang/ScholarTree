import argparse
import os

from notion_client import Client

from citations import update_citations
from draw import draw

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--draw", action="store_true")
    parser.add_argument("--update_citations", action="store_true")
    parser.add_argument(
        "--scholars", nargs="+", help="List of scholars to update citation count"
    )
    args = parser.parse_args()

    notion = Client(auth=os.getenv("NOTION_TOKEN"))

    if args.update_citations:
        update_citations(notion, scholar_names=args.scholars)

    if args.draw:
        draw(notion)
