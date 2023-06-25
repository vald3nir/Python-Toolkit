from bson import ObjectId

import toolkit.utils.backup_utils as backup_utils
from toolkit.database.mongodb.mongo_sdk import MongoDB


# ------------------------------------------------------------------------------------------------------
# MongoDB-based DAO
# ------------------------------------------------------------------------------------------------------
class MongoDAO:

    def __init__(self, client_url: str, project_name: str, collection: str) -> None:
        self._db = MongoDB(
            client_url=client_url,
            project_name=project_name,
            collection=collection)

    def list_documents(self, query: dict = {}, sort_field='_id', limit: int = 9999999) -> list[dict]:
        return self._db.find_all(query, sort_field, limit)

    def insert_documents(self, documents: list[dict]):
        self._db.insert_many(documents)

    def insert_document(self, document: dict):
        self._db.insert_one(document)

    def clear(self):
        self._db.clear()

    def delete_objects(self, _ids: list[ObjectId]) -> int:
        return self.delete_documents(query={"_id": {"$in": _ids}})

    def delete_documents(self, query: dict) -> int:
        return self._db.delete_many(query=query).deleted_count

    # ------------------------------------------------------------------------------------------------------
    # BACKUP AND RESTORE DATABASE
    # ------------------------------------------------------------------------------------------------------

    def _all_documents(self):
        _data = self.list_documents(sort_field='_id')
        [doc.pop('_id') for doc in _data]
        return _data

    def _insert_documents(self, _data):
        self.clear()
        self.insert_documents(_data)

    def backup_to_json(self, file: str):
        backup_utils.save_list_to_json(file, self._all_documents())

    def backup_to_csv(self, file: str):
        backup_utils.save_list_to_csv(file, self._all_documents())

    def restore_from_json(self, file: str):
        self._insert_documents(backup_utils.load_list_from_json(file))

    def restore_from_csv(self, file: str):
        self._insert_documents(backup_utils.load_list_from_csv(file))
