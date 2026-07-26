"""
MongoDB Data Access Object (DAO) using native PyMongo driver.
Provides convenient methods for CRUD operations and aggregations.
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional

import pymongo
from bson import ObjectId
from pymongo.results import DeleteResult


class MongoDAO:
    """MongoDB Data Access Object for direct driver operations."""

    def __init__(self, client_url: str, project_name: str, collection: str) -> None:
        """
        Initialize MongoDB connection.
        Args:
            client_url: MongoDB connection string
            project_name: Database name
            collection: Collection name
        """
        self.client = pymongo.MongoClient(client_url)
        self._db = self.client[project_name][collection]

    # ------------------------------------------------------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------------------------------------------------------

    def insert_document(self, document: Dict[str, Any]) -> None:
        """
        Insert a single document.

        Args:
            document: Document to insert
        """
        self._db.insert_one(document)

    def insert_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Insert multiple documents.

        Args:
            documents: List of documents to insert
        """
        self._db.insert_many(documents)

    def update_one(self, query: Dict[str, Any], values: Dict[str, Any]) -> None:
        """
        Update a single document.

        Args:
            query: Filter to find the document
            values: Values to update
        """
        self._db.update_one(query, update={"$set": values})

    def update_many(self, query: Dict[str, Any], values: Dict[str, Any]) -> None:
        """
        Update multiple documents.

        Args:
            query: Filter to find documents
            values: Values to update
        """
        self._db.update_many(query, update={"$set": values})

    def find_document(self, query: Dict[str, Any]) -> Mapping[str, Any] | None:
        """
        Find a single document.

        Args:
            query: Filter to find the document

        Returns:
            Document matching the query or None if not found
        """
        return self._db.find_one(query)

    def find_documents(
            self,
            query: Optional[Dict[str, Any]] = None,
            sort_field: str = '_id',
            limit: int = 999999999
    ) -> list[Mapping[str, Any]]:
        """
        Find multiple documents.

        Args:
            query: Filter to find documents
            sort_field: Field to sort by (default: '_id')
            limit: Maximum number of documents to return

        Returns:
            List of documents matching the query
        """
        return list(self._db.find(query).sort(sort_field, pymongo.ASCENDING).limit(limit))

    def last(
            self,
            query: Optional[Dict[str, Any]] = None,
            sort_field: str = '_id',
            limit: int = 5
    ) -> list[Mapping[str, Any]]:
        """
        Get the last N documents (most recent based on sort_field).

        Args:
            query: Filter to find documents
            sort_field: Field to sort by (default: '_id')
            limit: Number of documents to return (default: 5)

        Returns:
            List of the last N documents in descending order
        """
        return list(
            self._db.find(query).sort([(sort_field, pymongo.DESCENDING)]).limit(limit)
        )

    # ------------------------------------------------------------------------------------------------------------------
    # Delete Operations
    # ------------------------------------------------------------------------------------------------------------------

    def delete_documents(self, query=None) -> DeleteResult:
        """
        Delete documents matching the query.

        Args:
            query: Filter to find documents to delete (None deletes all)
        """
        return self._db.delete_many(filter=query)

    def delete_objects(self, _ids: List[ObjectId]) -> DeleteResult:
        """
        Delete documents by ObjectId list.

        Args:
            _ids: List of ObjectIds to delete
        """
        return self.delete_documents(query={"_id": {"$in": _ids}})

    def clear(self) -> None:
        """Delete all documents from the collection."""
        self._db.drop()

    # ------------------------------------------------------------------------------------------------------------------
    # Query Operations
    # ------------------------------------------------------------------------------------------------------------------

    def distinct(self, key: str) -> List[Any]:
        """
        Get distinct values for a field.

        Args:
            key: Field name to get distinct values

        Returns:
            List of distinct values
        """
        return self._db.distinct(key=key)

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> list[Mapping[str, Any]]:
        """
        Execute aggregation pipeline.

        Args:
            pipeline: MongoDB aggregation pipeline stages

        Returns:
            List of aggregation results
        """
        return list(
            self._db.aggregate(pipeline=pipeline, maxTimeMS=60000, allowDiskUse=True)
        )

    def collection_size(self) -> int:
        """
        Get total number of documents in collection.

        Returns:
            Number of documents
        """
        return self._db.count_documents({})

    def count_documents(self, query) -> int:
        """
        Get the number of documents in collection.

        Returns:
            Number of documents
        """
        return self._db.count_documents(query)

    # ------------------------------------------------------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------------------------------------------------------

    def close(self) -> None:
        """Close MongoDB connection."""
        self.client.close()
