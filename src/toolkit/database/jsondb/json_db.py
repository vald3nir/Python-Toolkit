from typing import Optional

from pysondb import db


class JsonDB:
    """A simple JSON database wrapper using pysondb."""

    def __init__(self, path: str = "localdb.jsondb") -> None:
        self.database = db.getDb(path)

    def find_document(self, query: dict) -> Optional[dict]:
        """Find a single document matching the query."""
        try:
            return self.database.getByQuery(query)[0]
        except IndexError:
            return None

    def insert_document(self, data: dict) -> None:
        """Insert a single document into the database."""
        self.database.add(new_data=data)

    def insert_documents(self, data: list[dict]) -> None:
        """Insert multiple documents into the database."""
        self.database.addMany(new_data=data)

    def update_document(self, _id: int, data: dict) -> None:
        """Update a document by its ID."""
        self.database.updateById(pk=_id, new_data=data)

    def find_documents(self) -> list[dict]:
        """Retrieve all documents from the database."""
        return list(self.database.getAll())

    def first(self, limit: int = 5) -> list[dict]:
        """Retrieve the first N documents from the database."""
        return self.database.get(num=limit)
        all_docs = self.database.getAll()
        return list(all_docs)[-limit:]

    def clear(self) -> None:
        """Delete all documents from the database."""
        self.database.deleteAll()
