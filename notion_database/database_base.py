from .enums import PROPERTY_TYPE


def contentGen(type):
    type_case = {
        PROPERTY_TYPE.TITLE: lambda data: {"title": [{"text": {"content": data}}]},
        PROPERTY_TYPE.RICH_TEXT: lambda data: {
            "rich_text": [{"text": {"content": data}}]
        },
        PROPERTY_TYPE.NUMBER: lambda data: {"number": data},
        PROPERTY_TYPE.DATE: lambda data: {"date": {"start": data}},
        PROPERTY_TYPE.SELECT: lambda data: {"select": {"name": data}},
    }
    return type_case.get(type)


class DatabaseBase:
    def __init__(self, database_id, client) -> None:
        self.client = client
        self.database_id = database_id

    def query(self):
        return self.client.databases.query(database_id=self.database_id)

    def updateRow(self, page_id, properties):
        return self.client.pages.update(page_id=page_id, properties=properties)

    def insertRow(self, row_cells):
        properties = {}
        for cell in row_cells:
            properties[cell.name] = contentGen(cell.type)(cell.data)

        return self.client.pages.create(
            parent={"database_id": self.database_id}, properties=properties
        )

    def updateByTitle(self, key, text, row_cells):
        response = self.query()
        page_id = None
        for page in response["results"]:
            if page["properties"][key]["title"][0]["plain_text"] == text:
                page_id = page["id"]  # 记录页面ID

        if not page_id:
            print(f"not find recork with key = {key} v= {text}")

        properties = {}
        for cell in row_cells:
            properties[cell.name] = contentGen(cell.type)(cell.data)

        self.updateRow(page_id, properties)
