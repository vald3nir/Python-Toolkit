import pytest
from unittest.mock import Mock, patch, MagicMock
from src.toolkit.database.firebase.firebase import Firebase


class TestFirebase:
    """Test suite for Firebase class."""

    @pytest.fixture
    def mock_firebase_config(self):
        """Mock Firebase configuration."""
        return {
            "apiKey": "test_api_key",
            "authDomain": "test_project.firebaseapp.com",
            "databaseURL": "https://test_project.firebaseio.com",
            "projectId": "test_project",
            "storageBucket": "test_project.appspot.com",
            "messagingSenderId": "123456789",
            "appId": "1:123456789:web:abcdefg"
        }

    @pytest.fixture
    def mock_firebase_certificate(self):
        """Mock Firebase certificate."""
        return {
            "type": "service_account",
            "project_id": "test_project",
            "private_key_id": "key_id",
            "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygT0xw==\n-----END RSA PRIVATE KEY-----\n",
            "client_email": "firebase-adminsdk@test_project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40test_project.iam.gserviceaccount.com"
        }

    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    @patch('src.toolkit.database.firebase.firebase.db')
    def test_firebase_initialization(self, mock_db, mock_cert, mock_init, mock_firebase_config, mock_firebase_certificate):
        """Test Firebase initialization."""
        mock_cert.return_value = Mock()

        firebase = Firebase(mock_firebase_config, mock_firebase_certificate)

        assert firebase is not None
        mock_cert.assert_called_once_with(mock_firebase_certificate)
        mock_init.assert_called_once()

    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    @patch('src.toolkit.database.firebase.firebase.db')
    def test_insert_or_update(self, mock_db, mock_cert, mock_init, mock_firebase_config, mock_firebase_certificate):
        """Test insert or update data."""
        mock_cert.return_value = Mock()
        mock_ref = MagicMock()
        mock_db.reference.return_value = mock_ref

        firebase = Firebase(mock_firebase_config, mock_firebase_certificate)
        data = {"name": "test", "value": 123}

        firebase.insert_or_update("/users/user1", data)

        mock_db.reference.assert_called_with("/users/user1")
        mock_ref.set.assert_called_once_with(data)

    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    @patch('src.toolkit.database.firebase.firebase.db')
    def test_load(self, mock_db, mock_cert, mock_init, mock_firebase_config, mock_firebase_certificate):
        """Test loading data from Firebase."""
        mock_cert.return_value = Mock()
        mock_ref = MagicMock()
        expected_data = {"name": "test", "value": 123}
        mock_ref.get.return_value = expected_data
        mock_db.reference.return_value = mock_ref

        firebase = Firebase(mock_firebase_config, mock_firebase_certificate)
        result = firebase.load("/users/user1")

        assert result == expected_data
        mock_db.reference.assert_called_with("/users/user1")
        mock_ref.get.assert_called_once()

    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    @patch('src.toolkit.database.firebase.firebase.db')
    def test_clear(self, mock_db, mock_cert, mock_init, mock_firebase_config, mock_firebase_certificate):
        """Test clearing data from a path."""
        mock_cert.return_value = Mock()
        mock_ref = MagicMock()
        mock_db.reference.return_value = mock_ref

        firebase = Firebase(mock_firebase_config, mock_firebase_certificate)
        firebase.clear("/users/user1")

        mock_db.reference.assert_called_with("/users/user1")
        mock_ref.set.assert_called_once_with({})

    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    @patch('src.toolkit.database.firebase.firebase.db')
    def test_insert_multiple_types(self, mock_db, mock_cert, mock_init, mock_firebase_config, mock_firebase_certificate):
        """Test inserting different data types."""
        mock_cert.return_value = Mock()
        mock_ref = MagicMock()
        mock_db.reference.return_value = mock_ref

        firebase = Firebase(mock_firebase_config, mock_firebase_certificate)

        # Test with string
        firebase.insert_or_update("/data/string", "test_string")
        mock_ref.set.assert_called_with("test_string")

        # Test with list
        firebase.insert_or_update("/data/list", [1, 2, 3])
        mock_ref.set.assert_called_with([1, 2, 3])

        # Test with dict
        firebase.insert_or_update("/data/dict", {"key": "value"})
        mock_ref.set.assert_called_with({"key": "value"})

    @patch('firebase_admin.initialize_app')
    @patch('firebase_admin.credentials.Certificate')
    @patch('src.toolkit.database.firebase.firebase.db')
    def test_load_empty_path(self, mock_db, mock_cert, mock_init, mock_firebase_config, mock_firebase_certificate):
        """Test loading from an empty path returns None."""
        mock_cert.return_value = Mock()
        mock_ref = MagicMock()
        mock_ref.get.return_value = None
        mock_db.reference.return_value = mock_ref

        firebase = Firebase(mock_firebase_config, mock_firebase_certificate)
        result = firebase.load("/nonexistent/path")

        assert result is None
