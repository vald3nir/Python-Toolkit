"""
MQTT Client wrapper using paho-mqtt library.
Provides convenient methods for publishing and subscribing to MQTT topics.
"""

import logging
from typing import Callable
from typing import Optional

import paho.mqtt.client as mqtt

DEFAULT_BROKER_ADDRESS = "broker.hivemq.com"
DEFAULT_MQTT_PORT = 1883

# Configure logging
logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client wrapper for publishing and subscribing to topics."""

    def __init__(
            self,
            broker_address: str = DEFAULT_BROKER_ADDRESS,
            broker_port: int = DEFAULT_MQTT_PORT,
            on_connect_callback: Optional[Callable] = None
    ) -> None:
        """
        Initialize MQTT client.

        Args:
            broker_address: MQTT broker address (default: broker.hivemq.com)
            broker_port: MQTT broker port (default: 1883)
            on_connect_callback: Callback function when client connects
        """
        self.broker_address = broker_address
        self.broker_port = broker_port
        self._subscriber_callback: Optional[Callable] = None
        self._on_connect_callback = on_connect_callback

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    # ------------------------------------------------------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to MQTT broker without authentication.

        Raises:
            Exception: If connection fails
        """
        logger.info(f"Connecting to {self.broker_address}:{self.broker_port}...")
        self.client.connect(self.broker_address, self.broker_port, 60)

    def connect_safe(self, username: str, password: str) -> None:
        """
        Connect to MQTT broker with authentication.

        Args:
            username: MQTT broker username
            password: MQTT broker password

        Raises:
            Exception: If connection fails
        """
        logger.info(f"Connecting safely to {self.broker_address}:{self.broker_port}...")
        self.client.username_pw_set(username, password)
        self.client.connect(self.broker_address, self.broker_port, 60)

    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        logger.info(f"Disconnecting from {self.broker_address}:{self.broker_port}...")
        self.client.disconnect()

    # ------------------------------------------------------------------------------------------------------------------
    # Internal Callbacks
    # ------------------------------------------------------------------------------------------------------------------

    def _on_message(self, current_client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        """
        Internal callback for MQTT message reception.

        Args:
            current_client: MQTT client instance
            userdata: User data
            msg: MQTT message object
        """
        try:
            if isinstance(msg.payload, bytes):
                response = msg.payload.decode('utf-8')
            else:
                response = str(msg.payload)
            logger.debug(f"Message received on {msg.topic}: {response}")
            if self._subscriber_callback:
                self._subscriber_callback(msg.topic, response)
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _on_connect(self, current_client: mqtt.Client, userdata: object, flags: object, rc: int) -> None:
        """
        Internal callback for MQTT connection.

        Args:
            current_client: MQTT client instance
            userdata: User data
            flags: Connection flags
            rc: Connection return code
        """
        if rc == 0:
            logger.info("MQTT client connected successfully")
            if self._on_connect_callback:
                self._on_connect_callback()
        else:
            logger.error(f"Failed to connect, return code: {rc}")

    # ------------------------------------------------------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------------------------------------------------------

    def publish(self, topic: str, data: str) -> bool:
        """
        Publish message to MQTT topic.

        Args:
            topic: MQTT topic to publish to
            data: Message data to publish

        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            result = self.client.publish(topic, data)
            status = result[0]
            if status == 0:
                logger.debug(f"Message published to {topic}")
                return True
            else:
                logger.error(f"Failed to send message to topic {topic}")
                return False
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False

    # ------------------------------------------------------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------------------------------------------------------

    def subscribe(self, topic: str, subscriber_callback: Callable) -> None:
        """
        Subscribe to MQTT topic.

        Args:
            topic: MQTT topic to subscribe to
            subscriber_callback: Callback function when message is received
                                Format: callback(topic: str, message: str)

        Example:
            def on_message(topic: str, message: str):
                print(f"Received: {message} on {topic}")

            client.subscribe("test/topic", on_message)
        """
        logger.info(f"Subscribing to topic: {topic}")
        self._subscriber_callback = subscriber_callback
        self.client.subscribe(topic)

    def unsubscribe(self, topic: str) -> None:
        """
        Unsubscribe from MQTT topic.

        Args:
            topic: MQTT topic to unsubscribe from
        """
        logger.info(f"Unsubscribing from topic: {topic}")
        self.client.unsubscribe(topic)

    # ------------------------------------------------------------------------------------------------------------------
    # Event Loop
    # ------------------------------------------------------------------------------------------------------------------

    def loop_forever(self) -> None:
        """
        Start the MQTT client loop (blocking).

        This method blocks until disconnect is called.
        Handles all network communication.
        """
        try:
            logger.info("Starting MQTT client loop (forever)...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected")
            self.disconnect()

    def loop_start(self) -> None:
        """
        Start the MQTT client loop in a background thread (non-blocking).

        Call loop_stop() to stop the background thread.
        """
        try:
            logger.info("Starting MQTT client loop (background)...")
            self.client.loop_start()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected")
            self.disconnect()

    def loop_stop(self) -> None:
        """Stop the MQTT client background loop."""
        try:
            logger.info("Stopping MQTT client loop...")
            self.client.loop_stop()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected")
            self.disconnect()
