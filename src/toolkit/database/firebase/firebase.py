"""
Firebase Realtime Database wrapper.
To get firebase certificate: https://firebase.google.com/docs/admin/setup?hl=pt-br
"""

from typing import Any
from typing import Optional

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


class Firebase:
    """Firebase Realtime Database client."""

    def __init__(self, firebase_config: dict, firebase_certificate: dict) -> None:
        """
        Initialize Firebase connection.

        Args:
            firebase_config: Firebase configuration dictionary
            firebase_certificate: Firebase service account certificate dictionary
        """
        cred: Any = credentials.Certificate(firebase_certificate)  # type: ignore
        firebase_admin.initialize_app(cred, firebase_config)
        self._db = db

    def insert_or_update(self, path: str, data: Any) -> None:
        """
        Insert or update data at specified path.

        Args:
            path: Database path where data will be stored
            data: Data to be inserted or updated
        """
        ref = self._db.reference(path)
        ref.set(data)

    def load(self, path: str) -> Optional[Any]:
        """
        Load data from specified path.

        Args:
            path: Database path to retrieve data from

        Returns:
            Data from the specified path or None if path doesn't exist
        """
        ref = self._db.reference(path)
        return ref.get()

    def clear(self, path: str) -> None:
        """
        Clear (delete) data at specified path.

        Args:
            path: Database path to clear
        """
        self.insert_or_update(path, {})
