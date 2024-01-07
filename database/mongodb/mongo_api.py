'''
    DOC ref: https://www.mongodb.com/docs/atlas/app-services/data-api/examples/
'''

import json

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
        super().__init__()
        self._api_url = api_url
        self.print_curl = print_curl
        self._headers = {
            'Content-Type': 'application/json',
            'Access-Control-Request-Headers': '*',
            'api-key': api_key
        }
        self._base_payload = {
            "collection": collection,
            "database": database,
            "dataSource": data_source
        }

    def _run_post_request(self, payload: str, action: str) -> str:
        try:
            url = self._api_url + action
            response = requests.request("POST", url, headers=self._headers, data=payload)
            return response.text
        except Exception as e:
            return str(e)

    def _run_get_request(self, payload: str, action: str) -> dict:
        try:
            url = self._api_url + action
            response = requests.request("POST", url, headers=self._headers, data=payload)
            data = json.loads(response.text)
            if self.print_curl:
                print_curl(response)
            if "documents" in data:
                return data["documents"]
            if "document" in data:
                return data["document"]
        except Exception as e:
            print(e)

    def insert_one(self, document: dict) -> str:
        _payload = self._base_payload
        _payload["document"] = document
        return self._run_post_request(payload=json.dumps(_payload), action="insertOne")

    def insert_many(self, documents: list[dict]) -> str:
        _payload = self._base_payload
        _payload["documents"] = documents
        return self._run_post_request(payload=json.dumps(_payload), action="insertMany")

    def delete_many(self, query: dict = None) -> str:
        _payload = self._base_payload
        if query is not None:
            _payload["filter"] = query
        return self._run_post_request(payload=json.dumps(_payload), action="deleteMany")

    def find_one(self, query: dict):
        _payload = self._base_payload
        _payload["filter"] = query
        return self._run_get_request(payload=json.dumps(_payload), action="findOne")

    def find_many(self, query: dict = None, sort: dict = None, limit: int = None):
        _payload = self._base_payload
        if query is not None:
            _payload["filter"] = query
        if sort is not None:
            _payload["sort"] = sort
        if limit is not None:
            _payload["limit"] = limit
        return self._run_get_request(payload=json.dumps(_payload), action="find")

    def aggregate(self, pipeline: [dict]):
        _payload = self._base_payload
        _payload["pipeline"] = pipeline
        return self._run_get_request(payload=json.dumps(_payload), action="aggregate")
