from unittest.mock import Mock
from unittest.mock import patch

import pytest

from src.toolkit.database.mongodb.mongo_api import MongoAPI


class TestMongoAPI:
    """Test suite for MongoAPI class."""

    @pytest.fixture
    def mongo_config(self):
        """MongoDB configuration fixture."""
        return {
            "api_url": "https://data.mongodb-api.com/app/test/endpoint/data/v1/action/",
            "api_key": "test_api_key_12345",
            "database": "test_db",
            "data_source": "Cluster0",
            "collection": "test_collection"
        }

    @pytest.fixture
    def mongo_api(self, mongo_config):
        """Create a MongoAPI instance."""
        return MongoAPI(
            api_url=mongo_config["api_url"],
            api_key=mongo_config["api_key"],
            database=mongo_config["database"],
            data_source=mongo_config["data_source"],
            collection=mongo_config["collection"],
            print_curl=False
        )

    def test_initialization(self, mongo_api):
        """Test MongoAPI initialization."""
        assert mongo_api._api_url == "https://data.mongodb-api.com/app/test/endpoint/data/v1/action/"
        assert mongo_api.print_curl is False
        assert mongo_api._headers["Content-Type"] == "application/json"
        assert mongo_api._headers["api-key"] == "test_api_key_12345"
        assert mongo_api._base_payload["database"] == "test_db"
        assert mongo_api._base_payload["dataSource"] == "Cluster0"
        assert mongo_api._base_payload["collection"] == "test_collection"

    @patch('requests.request')
    def test_insert_document(self, mock_request, mongo_api):
        """Test inserting a single document."""
        mock_response = Mock()
        mock_response.text = '{"insertedId": "123"}'
        mock_request.return_value = mock_response

        doc = {"name": "John", "age": 30}
        mongo_api.insert_document(doc)

        assert mock_request.called
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"
        assert "insertOne" in call_args[0][1]

    @patch('requests.request')
    def test_insert_documents(self, mock_request, mongo_api):
        """Test inserting multiple documents."""
        mock_response = Mock()
        mock_response.text = '{"insertedIds": ["123", "124"]}'
        mock_request.return_value = mock_response

        docs = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        mongo_api.insert_documents(docs)

        assert mock_request.called
        call_args = mock_request.call_args
        assert "insertMany" in call_args[0][1]

    @patch('requests.request')
    def test_find_document(self, mock_request, mongo_api):
        """Test finding a single document."""
        mock_response = Mock()
        mock_response.text = '{"document": {"_id": "123", "name": "John", "age": 30}}'
        mock_request.return_value = mock_response

        result = mongo_api.find_document({"name": "John"})

        assert result == {"_id": "123", "name": "John", "age": 30}
        assert mock_request.called
        call_args = mock_request.call_args
        assert "findOne" in call_args[0][1]

    @patch('requests.request')
    def test_find_documents(self, mock_request, mongo_api):
        """Test finding multiple documents."""
        mock_response = Mock()
        mock_response.text = '{"documents": [{"_id": "123", "name": "John"}, {"_id": "124", "name": "Jane"}]}'
        mock_request.return_value = mock_response

        result = mongo_api.find_documents(query={"age": {"$gt": 20}}, limit=10)

        assert len(result) == 2
        assert result[0]["name"] == "John"
        assert mock_request.called
        call_args = mock_request.call_args
        assert "find" in call_args[0][1]

    @patch('requests.request')
    def test_find_documents_with_sort(self, mock_request, mongo_api):
        """Test finding documents with sort parameter."""
        mock_response = Mock()
        mock_response.text = '{"documents": [{"name": "Jane"}, {"name": "John"}]}'
        mock_request.return_value = mock_response

        result = mongo_api.find_documents(sort={"name": 1})

        assert len(result) == 2
        assert mock_request.called

    @patch('requests.request')
    def test_delete_documents(self, mock_request, mongo_api):
        """Test deleting documents."""
        mock_response = Mock()
        mock_response.text = '{"deletedCount": 2}'
        mock_request.return_value = mock_response

        mongo_api.delete_documents(query={"age": {"$lt": 20}})

        assert mock_request.called
        call_args = mock_request.call_args
        assert "deleteMany" in call_args[0][1]

    @patch('requests.request')
    def test_aggregate(self, mock_request, mongo_api):
        """Test aggregation pipeline."""
        mock_response = Mock()
        mock_response.text = '{"documents": [{"_id": "30", "count": 5}]}'
        mock_request.return_value = mock_response

        pipeline = [
            {"$match": {"age": {"$gt": 25}}},
            {"$group": {"_id": "$age", "count": {"$sum": 1}}}
        ]
        result = mongo_api.aggregate(pipeline)

        assert len(result) == 1
        assert result[0]["_id"] == "30"
        assert mock_request.called
        call_args = mock_request.call_args
        assert "aggregate" in call_args[0][1]

    @patch('src.toolkit.database.mongodb.mongo_api.print_curl')
    @patch('requests.request')
    def test_print_curl_enabled(self, mock_request, mock_print_curl, mongo_config):
        """Test print_curl functionality."""
        mongo_api = MongoAPI(
            api_url=mongo_config["api_url"],
            api_key=mongo_config["api_key"],
            database=mongo_config["database"],
            data_source=mongo_config["data_source"],
            collection=mongo_config["collection"],
            print_curl=True
        )

        mock_response = Mock()
        mock_response.text = '{"document": {"_id": "123"}}'
        mock_request.return_value = mock_response

        mongo_api.find_document({"_id": "123"})

        assert mock_print_curl.called

    @patch('requests.request')
    def test_headers_configuration(self, mock_request, mongo_api):
        """Test that correct headers are sent with requests."""
        mock_response = Mock()
        mock_response.text = '{"documents": []}'
        mock_request.return_value = mock_response

        mongo_api.find_documents()

        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert headers["Content-Type"] == "application/json"
        assert headers["api-key"] == "test_api_key_12345"
        assert headers["Access-Control-Request-Headers"] == "*"

    @patch('requests.request')
    def test_find_documents_without_query(self, mock_request, mongo_api):
        """Test finding documents without query filter."""
        mock_response = Mock()
        mock_response.text = '{"documents": [{"_id": "1"}, {"_id": "2"}]}'
        mock_request.return_value = mock_response

        result = mongo_api.find_documents()

        assert len(result) == 2
        assert mock_request.called

    @patch('requests.request')
    def test_delete_documents_without_query(self, mock_request, mongo_api):
        """Test deleting all documents (without query)."""
        mock_response = Mock()
        mock_response.text = '{"deletedCount": 10}'
        mock_request.return_value = mock_response

        mongo_api.delete_documents()

        assert mock_request.called
        call_args = mock_request.call_args
        assert "deleteMany" in call_args[0][1]

    @patch('requests.request')
    def test_payload_structure(self, mock_request, mongo_api):
        """Test that payload structure is correct."""
        mock_response = Mock()
        mock_response.text = '{"insertedId": "123"}'
        mock_request.return_value = mock_response

        doc = {"name": "John"}
        mongo_api.insert_document(doc)

        call_args = mock_request.call_args
        payload = call_args[1]["data"]
        import json
        parsed_payload = json.loads(payload)

        assert parsed_payload["collection"] == "test_collection"
        assert parsed_payload["database"] == "test_db"
        assert parsed_payload["dataSource"] == "Cluster0"
        assert parsed_payload["document"] == doc
