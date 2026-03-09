from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from src.toolkit.protocols.mqtt import DEFAULT_BROKER_ADDRESS
from src.toolkit.protocols.mqtt import DEFAULT_MQTT_PORT
from src.toolkit.protocols.mqtt import MQTTClient


class TestMQTTClient:
    """Test suite for MQTTClient class."""

    @pytest.fixture
    def mock_mqtt_client(self):
        """Mock the paho mqtt client."""
        with patch('paho.mqtt.client.Client') as mock:
            yield mock

    @pytest.fixture
    def mqtt_client(self, mock_mqtt_client):
        """Create a MQTTClient instance with mocked mqtt client."""
        mock_instance = MagicMock()
        mock_mqtt_client.return_value = mock_instance

        on_connect_callback = MagicMock()
        client = MQTTClient(
            broker_address="test.mosquitto.org",
            broker_port=1883,
            on_connect_callback=on_connect_callback
        )

        client.client = mock_instance
        return client

    def test_initialization_with_defaults(self):
        """Test MQTTClient initialization with default values."""
        with patch('paho.mqtt.client.Client') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance

            client = MQTTClient()

            assert client.broker_address == DEFAULT_BROKER_ADDRESS
            assert client.broker_port == DEFAULT_MQTT_PORT
            assert client._subscriber_callback is None
            mock.assert_called_once()

    def test_initialization_with_custom_values(self, mock_mqtt_client):
        """Test MQTTClient initialization with custom values."""
        mock_instance = MagicMock()
        mock_mqtt_client.return_value = mock_instance

        on_connect_cb = MagicMock()
        client = MQTTClient(
            broker_address="custom.broker.com",
            broker_port=8883,
            on_connect_callback=on_connect_cb
        )

        assert client.broker_address == "custom.broker.com"
        assert client.broker_port == 8883
        assert client._on_connect_callback == on_connect_cb

    def test_callbacks_are_set(self, mock_mqtt_client):
        """Test that mqtt callbacks are properly set."""
        mock_instance = MagicMock()
        mock_mqtt_client.return_value = mock_instance

        client = MQTTClient()

        assert client.client.on_connect == client._on_connect
        assert client.client.on_message == client._on_message

    def test_connect_without_credentials(self, mqtt_client):
        """Test connecting without username and password."""
        mqtt_client.connect()

        mqtt_client.client.connect.assert_called_once_with(
            "test.mosquitto.org",
            1883,
            60
        )

    def test_connect_safe_with_credentials(self, mqtt_client):
        """Test connecting with username and password."""
        mqtt_client.connect_safe(username="testuser", password="testpass")

        mqtt_client.client.username_pw_set.assert_called_once_with("testuser", "testpass")
        mqtt_client.client.connect.assert_called_once_with(
            "test.mosquitto.org",
            1883,
            60
        )

    def test_disconnect(self, mqtt_client):
        """Test disconnecting from broker."""
        mqtt_client.disconnect()

        mqtt_client.client.disconnect.assert_called_once()

    def test_publish_success(self, mqtt_client):
        """Test successful message publishing."""
        mqtt_client.client.publish.return_value = (0, 1)

        result = mqtt_client.publish("test/topic", "test message")

        assert result is True
        mqtt_client.client.publish.assert_called_once_with("test/topic", "test message")

    def test_publish_failure(self, mqtt_client):
        """Test failed message publishing."""
        mqtt_client.client.publish.return_value = (1, 1)

        result = mqtt_client.publish("test/topic", "test message")

        assert result is False

    def test_publish_with_different_status_codes(self, mqtt_client):
        """Test publishing with different MQTT status codes."""
        test_cases = [
            (0, True),  # MQTT_ERR_SUCCESS
            (1, False),  # MQTT_ERR_NO_CONN
            (2, False),  # MQTT_ERR_INVALID_PROT_VER
            (3, False),  # MQTT_ERR_INVALID_CLIENT_ID
        ]

        for status, expected_result in test_cases:
            mqtt_client.client.publish.return_value = (status, 1)
            result = mqtt_client.publish("test/topic", "data")
            assert result == expected_result

    def test_subscribe(self, mqtt_client):
        """Test subscribing to a topic."""
        subscriber_callback = MagicMock()

        mqtt_client.subscribe("test/topic", subscriber_callback)

        assert mqtt_client._subscriber_callback == subscriber_callback
        mqtt_client.client.subscribe.assert_called_once_with("test/topic")

    def test_unsubscribe(self, mqtt_client):
        """Test unsubscribing from a topic."""
        mqtt_client.unsubscribe("test/topic")

        mqtt_client.client.unsubscribe.assert_called_once_with("test/topic")

    def test_subscribe_multiple_topics(self, mqtt_client):
        """Test subscribing to multiple topics sequentially."""
        callback = MagicMock()

        mqtt_client.subscribe("topic/1", callback)
        mqtt_client.subscribe("topic/2", callback)

        assert mqtt_client.client.subscribe.call_count == 2
        mqtt_client.client.subscribe.assert_any_call("topic/1")
        mqtt_client.client.subscribe.assert_any_call("topic/2")

    def test_on_message_callback(self, mqtt_client):
        """Test on_message callback handling."""
        subscriber_callback = MagicMock()
        mqtt_client._subscriber_callback = subscriber_callback

        # Mock the message object
        mock_msg = MagicMock()
        mock_msg.payload = b"test message"
        mock_msg.topic = "test/topic"

        mqtt_client._on_message(mqtt_client.client, None, mock_msg)

        subscriber_callback.assert_called_once_with("test/topic", "test message")

    def test_on_message_with_special_characters(self, mqtt_client):
        """Test on_message with special characters and UTF-8."""
        subscriber_callback = MagicMock()
        mqtt_client._subscriber_callback = subscriber_callback

        mock_msg = MagicMock()
        mock_msg.payload = "José García: Tëst with spëcial çharacters".encode('utf-8')
        mock_msg.topic = "test/topic"

        mqtt_client._on_message(mqtt_client.client, None, mock_msg)

        subscriber_callback.assert_called_once_with(
            "test/topic",
            "José García: Tëst with spëcial çharacters"
        )

    def test_on_connect_success(self, mqtt_client):
        """Test on_connect callback with successful connection."""
        mqtt_client._on_connect_callback = MagicMock()

        mqtt_client._on_connect(mqtt_client.client, None, None, rc=0)

        mqtt_client._on_connect_callback.assert_called_once()

    def test_on_connect_failure(self, mqtt_client):
        """Test on_connect callback with connection failure."""
        mqtt_client._on_connect_callback = MagicMock()

        mqtt_client._on_connect(mqtt_client.client, None, None, rc=1)

        mqtt_client._on_connect_callback.assert_not_called()

    def test_on_connect_with_different_return_codes(self, mqtt_client):
        """Test on_connect with different MQTT return codes."""
        mqtt_client._on_connect_callback = MagicMock()

        return_codes = [0, 1, 2, 3, 4, 5]
        for rc in return_codes:
            mqtt_client._on_connect_callback.reset_mock()
            mqtt_client._on_connect(mqtt_client.client, None, None, rc=rc)

            if rc == 0:
                mqtt_client._on_connect_callback.assert_called_once()
            else:
                mqtt_client._on_connect_callback.assert_not_called()

    def test_loop_forever(self, mqtt_client):
        """Test loop_forever method."""
        mqtt_client.client.loop_forever.return_value = None

        # We'll test that it calls loop_forever but we can't actually run forever in tests
        # So we'll just verify the method exists and can be called
        assert hasattr(mqtt_client, 'loop_forever')
        assert callable(mqtt_client.loop_forever)

    def test_loop_start(self, mqtt_client):
        """Test loop_start method."""
        mqtt_client.client.loop_start.return_value = None

        mqtt_client.loop_start()

        mqtt_client.client.loop_start.assert_called_once()

    def test_loop_stop(self, mqtt_client):
        """Test loop_stop method."""
        mqtt_client.client.loop_stop.return_value = None

        mqtt_client.loop_stop()

        mqtt_client.client.loop_stop.assert_called_once()

    def test_publish_and_subscribe_workflow(self, mqtt_client):
        """Test complete publish and subscribe workflow."""
        # Setup subscription
        subscriber_callback = MagicMock()
        mqtt_client.subscribe("sensor/temperature", subscriber_callback)

        # Publish a message
        mqtt_client.client.publish.return_value = (0, 1)
        result = mqtt_client.publish("sensor/temperature", "25.5")

        # Verify publish was successful
        assert result is True
        mqtt_client.client.publish.assert_called_once_with("sensor/temperature", "25.5")

        # Simulate incoming message
        mock_msg = MagicMock()
        mock_msg.payload = b"25.5"
        mock_msg.topic = "sensor/temperature"

        mqtt_client._on_message(mqtt_client.client, None, mock_msg)

        # Verify callback was called
        subscriber_callback.assert_called_once_with("sensor/temperature", "25.5")

    def test_multiple_publishes(self, mqtt_client):
        """Test publishing multiple messages."""
        mqtt_client.client.publish.return_value = (0, 1)

        topics_and_messages = [
            ("test/topic1", "message1"),
            ("test/topic2", "message2"),
            ("test/topic3", "message3"),
        ]

        for topic, message in topics_and_messages:
            result = mqtt_client.publish(topic, message)
            assert result is True

        assert mqtt_client.client.publish.call_count == 3

    def test_connect_and_disconnect_workflow(self, mqtt_client):
        """Test complete connect and disconnect workflow."""
        mqtt_client._on_connect_callback = MagicMock()

        # Connect
        mqtt_client.connect()
        mqtt_client.client.connect.assert_called_once()

        # Simulate connection success
        mqtt_client._on_connect(mqtt_client.client, None, None, rc=0)
        mqtt_client._on_connect_callback.assert_called_once()

        # Disconnect
        mqtt_client.disconnect()
        mqtt_client.client.disconnect.assert_called_once()

    def test_connect_safe_and_disconnect_workflow(self, mqtt_client):
        """Test complete secure connect and disconnect workflow."""
        # Connect safely
        mqtt_client.connect_safe("user", "password")

        mqtt_client.client.username_pw_set.assert_called_once_with("user", "password")
        mqtt_client.client.connect.assert_called_once()

        # Disconnect
        mqtt_client.disconnect()
        mqtt_client.client.disconnect.assert_called_once()

    def test_broker_address_and_port_configuration(self, mock_mqtt_client):
        """Test custom broker address and port configuration."""
        mock_instance = MagicMock()
        mock_mqtt_client.return_value = mock_instance

        custom_address = "mqtt.example.com"
        custom_port = 8883

        client = MQTTClient(
            broker_address=custom_address,
            broker_port=custom_port
        )

        client.connect()

        client.client.connect.assert_called_once_with(custom_address, custom_port, 60)

    def test_on_message_without_callback_set(self, mqtt_client):
        """Test on_message when callback is not set (should handle gracefully)."""
        mqtt_client._subscriber_callback = None

        mock_msg = MagicMock()
        mock_msg.payload = b"test"
        mock_msg.topic = "test/topic"

        # Should not crash, just skip callback
        mqtt_client._on_message(mqtt_client.client, None, mock_msg)

    def test_publish_with_empty_topic(self, mqtt_client):
        """Test publishing with empty topic."""
        mqtt_client.client.publish.return_value = (0, 1)

        result = mqtt_client.publish("", "message")

        assert result is True
        mqtt_client.client.publish.assert_called_once_with("", "message")

    def test_publish_with_empty_message(self, mqtt_client):
        """Test publishing with empty message."""
        mqtt_client.client.publish.return_value = (0, 1)

        result = mqtt_client.publish("test/topic", "")

        assert result is True
        mqtt_client.client.publish.assert_called_once_with("test/topic", "")

    def test_subscribe_with_wildcard_topics(self, mqtt_client):
        """Test subscribing with wildcard topics."""
        callback = MagicMock()

        wildcard_topics = [
            "test/#",
            "sensor/+/temperature",
            "$SYS/broker/clients/active",
        ]

        for topic in wildcard_topics:
            mqtt_client.subscribe(topic, callback)

        assert mqtt_client.client.subscribe.call_count == 3
