import os
import pytest

from src.toolkit.database.jsondb.json_db import JsonDB

TEST_FILE_PATH = f"{os.path.relpath(os.path.dirname(__file__))}{os.sep}test_json_db.json"


@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up test database before and after each test."""
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    yield
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)


class TestJsonDB:
    """Test suite for JsonDB class."""

    @staticmethod
    def _get_db():
        """Get a fresh JsonDB instance."""
        return JsonDB(TEST_FILE_PATH)

    def test_insert_and_find_document(self):
        """Test inserting and finding a single document."""
        db = self._get_db()
        doc = {"name": "test", "value": 1}
        db.insert_document(doc)
        found = db.find_document({"name": "test"})
        assert found["name"] == "test"
        assert found["value"] == 1

    def test_insert_documents(self):
        """Test inserting multiple documents."""
        db = self._get_db()
        docs = [
            {"name": "doc1", "value": 1},
            {"name": "doc2", "value": 2}
        ]
        db.insert_documents(docs)
        all_docs = db.find_documents()
        assert len(all_docs) == 2
        assert all_docs[0] in docs
        assert all_docs[1] in docs

    def test_update_document(self):
        """Test updating a document."""
        db = self._get_db()
        doc = {"name": "test", "value": 1}
        db.insert_document(doc)
        found = db.find_document({"name": "test"})
        _id = found["id"]
        updated_doc = {"name": "test", "value": 2}
        db.update_document(_id, updated_doc)
        found = db.find_document({"name": "test"})
        assert found["name"] == "test"
        assert found["value"] == 2

    def test_find_documents(self):
        """Test retrieving all documents."""
        db = self._get_db()
        docs = [
            {"name": "doc1", "value": 1},
            {"name": "doc2", "value": 2}
        ]
        db.insert_documents(docs)
        all_docs = db.find_documents()
        assert len(all_docs) == 2

    def test_first_documents(self):
        """Test retrieving the first N documents."""
        db = self._get_db()
        docs = [
            {"name": "doc1", "value": 1},
            {"name": "doc2", "value": 2},
            {"name": "doc3", "value": 3}
        ]
        db.insert_documents(docs)
        first_two = db.first(2)
        assert len(first_two) == 2
        assert first_two[0]["name"] == "doc1"
        assert first_two[1]["name"] == "doc2"

    def test_clear(self):
        """Test clearing all documents."""
        db = self._get_db()
        doc = {"name": "test", "value": 1}
        db.insert_document(doc)
        db.clear()
        all_docs = db.find_documents()
        assert len(all_docs) == 0
