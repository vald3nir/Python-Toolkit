"""IP address and network operations."""

import logging
import socket

logger = logging.getLogger(__name__)


def get_local_ip() -> str:
    """
    Get the local IP address of the machine.

    Uses UDP connection to determine which IP address is used to connect
    to external networks. No actual connection is made.

    Returns:
        Local IP address as string

    Raises:
        Returns error message as string if operation fails

    Example:
        >>> ip = get_local_ip()
        >>> print(ip)
        '192.168.1.100'
    """
    try:
        # Create a temporary socket to discover the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Tries to connect to an external address (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            # Gets the local IP address used for the connection
            local_ip = s.getsockname()[0]
            logger.info(f"Local IP address: {local_ip}")
            return local_ip
        finally:
            s.close()
    except Exception as e:
        error_msg = f"Error getting local IP: {e}"
        logger.error(error_msg)
        return error_msg
