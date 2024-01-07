import pymongo
from pymongo import WriteConcern


def copy_databases(
        origin_database_name: str,
        origin_database_address: str,
        destination_database_name: str,
        destination_database_address: str
):
    origin = pymongo.MongoClient(origin_database_address)[origin_database_name]
    destination = pymongo.MongoClient(destination_database_address)[destination_database_name]

    for collection in origin.list_collection_names():
        collections_cursor = origin[collection].find()
        clt = destination[collection]
        clt.drop()
        for document in collections_cursor:
            clt.with_options(write_concern=WriteConcern(w=0)).insert_one(document)


class MongoDB:
    def __init__(self, client_url: str, project_name: str, collection: str) -> None:
        super().__init__()
        self.collection = pymongo.MongoClient(client_url)[project_name][collection]

    def find_one(self, query: dict):
        return self.collection.find_one(query)

    def update_one(self, query: dict, values: dict):
        self.collection.update_one(query, update={"$set": values}, upsert=True)

    def insert_one(self, document: dict):
        self.collection.insert_one(document=document)

    def insert_many(self, documents: list[dict]):
        self.collection.insert_many(documents=documents)

    def aggregate(self, pipeline: list[dict]):
        return self.collection.aggregate(pipeline=pipeline)

    def find_all(self, query: dict, sort_field='_id', limit: int = 9999999):
        return list(self.collection.find(query).sort([(sort_field, pymongo.ASCENDING)]).limit(limit))

    def last(self, query: dict, sort_field: str = '_id', limit: int = 5):
        return list(self.collection.find(query).sort([(sort_field, pymongo.DESCENDING)]).limit(limit))

    def clear(self):
        self.collection.drop()

    def delete_one(self, query: dict):
        self.collection.delete_one(query)

    def delete_many(self, query: dict) -> int:
        return self.collection.delete_many(query).deleted_count

    def distinct(self, key: str):
        return self.collection.distinct(key=key)
