"""网关发现工具类."""

from dataclasses import dataclass
import socket

from .common_utils import json_to_bean


@dataclass
class GatewayInfo:
    """网关信息."""

    ip: str = None
    link_enabled: bool = None
    link_remain_ms: int = None
    mac: str = None
    model: str = None
    name: str = None
    reset_id: str = None
    version: str = None


@dataclass
class DiscoveryResponse:
    """发现响应."""

    data: GatewayInfo = None
    op: int = None


class GatewayDiscovery:
    """网关发现."""

    LISTEN_IP = "0.0.0.0"
    BROADCAST_IP = "255.255.255.255"
    PORT = 9001

    def __init__(self) -> None:
        """初始化网关发现类."""
        self._recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._recv_sock.settimeout(30)
        self._recv_sock.bind((self.LISTEN_IP, self.PORT))

        self.hostname = socket.gethostname()
        # self.local_ip = socket.gethostbyname(self.hostname)
        self.local_ip = socket.gethostbyname(self.hostname)
        self._send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._send_sock.bind((self.local_ip, 0))

    def discovery(self, timeout: int) -> DiscoveryResponse:
        """发现网关."""
        self._send_sock.sendto(b'{"op":101}', (self.BROADCAST_IP, self.PORT))
        try:
            self._recv_sock.settimeout(timeout)
            buf, addr = self._recv_sock.recvfrom(1024)
            if addr[0] == self.local_ip:
                buf, addr = self._recv_sock.recvfrom(1024)
                return json_to_bean(buf.decode(), DiscoveryResponse)
        except TimeoutError:
            return None
        finally:
            self._send_sock.close()
            self._recv_sock.close()
