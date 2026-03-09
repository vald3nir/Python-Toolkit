from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from bson import ObjectId

from src.toolkit.database.mongodb.mongo_dao import MongoDAO


class TestMongoDAO:
    """Test suite for MongoDAO class."""

    @pytest.fixture
    def mock_client(self):
        """Mock MongoDB client."""
        with patch('pymongo.MongoClient') as mock:
            yield mock

    @pytest.fixture
    def mongo_dao(self, mock_client):
        """Create a MongoDAO instance with mocked client."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        dao = MongoDAO(
            client_url="mongodb://localhost:27017/",
            project_name="test_db",
            collection="test_collection"
        )

        # Mock the collection
        dao._db = MagicMock()
        return dao

    def test_initialization(self, mock_client):
        """Test MongoDAO initialization."""
        with patch('pymongo.MongoClient') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance

            dao = MongoDAO(
                client_url="mongodb://localhost:27017/",
                project_name="test_db",
                collection="test_collection"
            )

            mock.assert_called_once_with("mongodb://localhost:27017/")
            assert dao.client == mock_instance

    def test_insert_document(self, mongo_dao):
        """Test inserting a single document."""
        doc = {"name": "John", "age": 30}
        mongo_dao.insert_document(doc)

        mongo_dao._db.insert_one.assert_called_once_with(doc)

    def test_insert_documents(self, mongo_dao):
        """Test inserting multiple documents."""
        docs = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        mongo_dao.insert_documents(docs)

        mongo_dao._db.insert_many.assert_called_once_with(docs)

    def test_update_one(self, mongo_dao):
        """Test updating a single document."""
        query = {"name": "John"}
        values = {"age": 31}

        mongo_dao.update_one(query, values)

        mongo_dao._db.update_one.assert_called_once_with(
            query,
            update={"$set": values}
        )

    def test_update_many(self, mongo_dao):
        """Test updating multiple documents."""
        query = {"age": {"$lt": 30}}
        values = {"status": "young"}

        mongo_dao.update_many(query, values)

        mongo_dao._db.update_many.assert_called_once_with(
            query,
            update={"$set": values}
        )

    def test_find_document(self, mongo_dao):
        """Test finding a single document."""
        query = {"name": "John"}
        expected_result = {"_id": ObjectId(), "name": "John", "age": 30}
        mongo_dao._db.find_one.return_value = expected_result

        result = mongo_dao.find_document(query)

        assert result == expected_result
        mongo_dao._db.find_one.assert_called_once_with(query)

    def test_find_documents(self, mongo_dao):
        """Test finding multiple documents."""
        query = {"age": {"$gt": 20}}
        mock_cursor = MagicMock()
        docs = [
            {"_id": ObjectId(), "name": "John", "age": 30},
            {"_id": ObjectId(), "name": "Jane", "age": 25}
        ]

        mongo_dao._db.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = docs

        result = mongo_dao.find_documents(query, limit=10)

        assert result == docs
        mongo_dao._db.find.assert_called_once_with(query)
        mock_cursor.sort.assert_called_once()
        mock_cursor.limit.assert_called_once()

    def test_find_documents_with_default_params(self, mongo_dao):
        """Test finding documents with default parameters."""
        mock_cursor = MagicMock()
        docs = [{"_id": ObjectId(), "name": "John"}]

        mongo_dao._db.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = docs

        result = mongo_dao.find_documents()

        assert result == docs
        mongo_dao._db.find.assert_called_once_with(None)

    def test_last(self, mongo_dao):
        """Test getting last N documents."""
        query = {"status": "active"}
        mock_cursor = MagicMock()
        docs = [
            {"_id": ObjectId(), "name": "Jane", "timestamp": 3},
            {"_id": ObjectId(), "name": "John", "timestamp": 2}
        ]

        mongo_dao._db.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = docs

        result = mongo_dao.last(query, sort_field='timestamp', limit=2)

        assert result == docs
        mongo_dao._db.find.assert_called_once_with(query)
        mock_cursor.limit.assert_called_once_with(2)

    def test_distinct(self, mongo_dao):
        """Test getting distinct values."""
        key = "category"
        expected_values = ["tech", "science", "art"]
        mongo_dao._db.distinct.return_value = expected_values

        result = mongo_dao.distinct(key)

        assert result == expected_values
        mongo_dao._db.distinct.assert_called_once_with(key=key)

    def test_delete_documents(self, mongo_dao):
        """Test deleting documents."""
        query = {"age": {"$lt": 18}}
        mongo_dao._db.delete_many.return_value = MagicMock(deleted_count=5)

        mongo_dao.delete_documents(query)

        mongo_dao._db.delete_many.assert_called_once_with(filter=query)

    def test_delete_documents_without_query(self, mongo_dao):
        """Test deleting all documents (no query)."""
        mongo_dao._db.delete_many.return_value = MagicMock(deleted_count=100)

        mongo_dao.delete_documents()

        mongo_dao._db.delete_many.assert_called_once_with(filter=None)

    def test_delete_objects(self, mongo_dao):
        """Test deleting documents by ObjectId list."""
        oid1 = ObjectId()
        oid2 = ObjectId()
        object_ids = [oid1, oid2]

        mongo_dao._db.delete_many.return_value = MagicMock(deleted_count=2)

        mongo_dao.delete_objects(object_ids)

        mongo_dao._db.delete_many.assert_called_once_with(
            filter={"_id": {"$in": object_ids}}
        )

    def test_clear(self, mongo_dao):
        """Test clearing all documents from collection."""
        mongo_dao._db.drop.return_value = None

        mongo_dao.clear()

        mongo_dao._db.drop.assert_called_once()

    def test_aggregate(self, mongo_dao):
        """Test aggregation pipeline."""
        pipeline = [
            {"$match": {"age": {"$gt": 25}}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        expected_results = [
            {"_id": "tech", "count": 5},
            {"_id": "science", "count": 3}
        ]

        mongo_dao._db.aggregate.return_value = expected_results

        result = mongo_dao.aggregate(pipeline)

        assert result == expected_results
        mongo_dao._db.aggregate.assert_called_once_with(
            pipeline=pipeline,
            maxTimeMS=60000,
            allowDiskUse=True
        )

    def test_collection_size(self, mongo_dao):
        """Test getting collection size."""
        mongo_dao._db.count_documents.return_value = 42

        result = mongo_dao.collection_size()

        assert result == 42
        mongo_dao._db.count_documents.assert_called_once_with({})

    def test_close(self, mongo_dao):
        """Test closing MongoDB connection."""
        mongo_dao.client.close = MagicMock()

        mongo_dao.close()

        mongo_dao.client.close.assert_called_once()

    def test_insert_and_find_workflow(self, mongo_dao):
        """Test complete insert and find workflow."""
        # Insert
        doc = {"name": "John", "age": 30}
        mongo_dao.insert_document(doc)

        # Find
        mongo_dao._db.find_one.return_value = doc
        result = mongo_dao.find_document({"name": "John"})

        assert result == doc
        mongo_dao._db.insert_one.assert_called_once()
        mongo_dao._db.find_one.assert_called_once()

    def test_update_and_find_workflow(self, mongo_dao):
        """Test complete update and find workflow."""
        query = {"name": "John"}
        new_values = {"age": 31}

        # Update
        mongo_dao.update_one(query, new_values)

        # Find updated document
        updated_doc = {"name": "John", "age": 31}
        mongo_dao._db.find_one.return_value = updated_doc
        result = mongo_dao.find_document(query)

        assert result == updated_doc
        mongo_dao._db.update_one.assert_called_once()
        mongo_dao._db.find_one.assert_called_once()

    def test_connection_string_formats(self):
        """Test different MongoDB connection string formats."""
        test_cases = [
            "mongodb://localhost:27017/",
            "mongodb+srv://user:pass@cluster.mongodb.net/",
            "mongodb://192.168.1.1:27017/"
        ]

        for conn_str in test_cases:
            with patch('pymongo.MongoClient') as mock_client:
                mock_instance = MagicMock()
                mock_client.return_value = mock_instance

                dao = MongoDAO(
                    client_url=conn_str,
                    project_name="test_db",
                    collection="test_col"
                )

                mock_client.assert_called_once_with(conn_str)

    def test_special_characters_in_document(self, mongo_dao):
        """Test inserting documents with special characters."""
        doc = {
            "name": "José García",
            "email": "test@example.com",
            "description": "Tëst with spëcial çharacters"
        }

        mongo_dao.insert_document(doc)

        mongo_dao._db.insert_one.assert_called_once_with(doc)

    def test_nested_documents(self, mongo_dao):
        """Test inserting nested documents."""
        doc = {
            "name": "John",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001"
            },
            "contacts": [
                {"type": "email", "value": "john@example.com"},
                {"type": "phone", "value": "+1234567890"}
            ]
        }

        mongo_dao.insert_document(doc)

        mongo_dao._db.insert_one.assert_called_once_with(doc)

    def test_large_batch_insert(self, mongo_dao):
        """Test inserting large batch of documents."""
        docs = [{"id": i, "value": f"doc_{i}"} for i in range(1000)]

        mongo_dao.insert_documents(docs)

        mongo_dao._db.insert_many.assert_called_once_with(docs)
