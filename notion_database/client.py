from collections import namedtuple

from .database_base import DatabaseBase
from .enums import PROPERTY_TYPE

Cell = namedtuple("Cell", ["type", "name", "data"])


class DatabaseClient:
    def __init__(self, database_id, client, template_cells) -> None:
        self.database = DatabaseBase(database_id, client)
        self.template = {}
        for cell in template_cells:
            self.template[cell.name] = cell

    def query(self):
        return self.database.query()

    def _getRowData(self, **kwargs):
        cells = []
        for k, v in kwargs.items():
            if k not in self.template:
                continue
            cell = Cell(name=k, type=self.template[k].type, data=v)
            cells.append(cell)

        return cells

    def insertRow(self, **kwargs):
        cells = self._getRowData(**kwargs)
        return self.database.insertRow(cells)

    def updateByTitle(self, key, text, **kwargs):
        cells = self._getRowData(**kwargs)
        return self.database.updateByTitle(key, text, cells)
