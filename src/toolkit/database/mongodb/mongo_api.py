"""
    DOC ref: https://www.mongodb.com/docs/atlas/app-services/data-api/examples/
"""

import json
from typing import Any

import curl
import requests


def print_curl(response):
    curl.parse(response)


class MongoAPI:
    def __init__(
            self,
            api_url: str,
            api_key: str,
            database: str,
            data_source: str,
            collection: str,
            print_curl: bool = False
    ) -> None:
        self._api_url = api_url
        self.print_curl = print_curl
        self._headers = {
            'Content-Type': 'application/json',
            'Access-Control-Request-Headers': '*',
            'api-key': api_key
        }
        self._base_payload: dict[str, Any] = {
            "collection": collection,
            "database": database,
            "dataSource": data_source
        }

    # ------------------------------------------------------------------------------------------------------------------
    # Implementations
    # ------------------------------------------------------------------------------------------------------------------

    def insert_document(self, document: dict):
        """Insert a single document into the collection."""
        _payload = self._base_payload.copy()
        _payload["document"] = document
        self._run_api(payload=json.dumps(_payload), action="insertOne")

    def insert_documents(self, documents: list[dict]):
        """Insert multiple documents into the collection."""
        _payload = self._base_payload.copy()
        _payload["documents"] = documents
        self._run_api(payload=json.dumps(_payload), action="insertMany")

    def delete_documents(self, query: dict = None):
        """Delete documents matching the query from the collection."""
        _payload = self._base_payload.copy()
        if query is not None:
            _payload["filter"] = query
        self._run_api(payload=json.dumps(_payload), action="deleteMany")

    def find_document(self, query: dict) -> dict:
        """Find a single document matching the query."""
        _payload = self._base_payload.copy()
        _payload["filter"] = query
        return self._run_get_document(payload=json.dumps(_payload), action="findOne")

    def find_documents(self, query: dict = None, sort: dict = None, limit: int = None) -> list[dict]:
        """Find documents matching the query, with optional sort and limit."""
        _payload = self._base_payload.copy()
        if query is not None:
            _payload["filter"] = query
        if sort is not None:
            _payload["sort"] = sort
        if limit is not None:
            _payload["limit"] = limit
        return self._run_get_documents(payload=json.dumps(_payload), action="find")

    def aggregate(self, pipeline: list[dict]) -> list[dict]:
        """Perform an aggregation pipeline on the collection."""
        _payload = self._base_payload.copy()
        _payload["pipeline"] = pipeline
        return self._run_get_documents(payload=json.dumps(_payload), action="aggregate")

    # ------------------------------------------------------------------------------------------------------------------
    # Extra Methods
    # ------------------------------------------------------------------------------------------------------------------

    def _run_api(self, payload: str, action: str) -> dict:
        url = self._api_url + action
        response = requests.request("POST", url, headers=self._headers, data=payload)
        if self.print_curl:
            print_curl(response)
        return json.loads(response.text)

    def _run_get_document(self, payload: str, action: str) -> dict:
        data = self._run_api(payload, action)
        return data["document"]

    def _run_get_documents(self, payload: str, action: str) -> list[dict]:
        data = self._run_api(payload, action)
        return data["documents"]
