"""Mqtt client utils."""

import asyncio
from collections.abc import Callable
import logging

import paho.mqtt.client as mqtt

from .models import Device, DeviceUpdatePayload, LightUpdatePayload, Resource
from .utils import json_to_bean

_LOGGER = logging.getLogger(__name__)


ALL_TOPICS = [
    "res/device/add",  # 添加设备
    "res/device/remove",  # 删除设备
    "res/device/update",  # 更新设备
    "res/light/update",  # 灯具更新
]


class MqttServiceForGateway:
    """Gateway mqtt service."""

    _mqtt: mqtt.Client
    _ip: str

    def __init__(self, ip_address: str) -> None:
        """Init mqtt client."""
        self._mqtt = mqtt.Client()
        self._ip = ip_address
        self._on_device_add: (
            Callable[
                [
                    list[Device],
                ]
            ]
            | None
        ) = None
        self._on_device_remove: (
            Callable[
                [
                    list[Resource],
                ]
            ]
            | None
        ) = None
        self._on_device_update: (
            Callable[
                [
                    list[DeviceUpdatePayload],
                ]
            ]
            | None
        ) = None
        self._on_light_update: (
            Callable[
                [
                    list[LightUpdatePayload],
                ]
            ]
            | None
        ) = None
        self.loop = asyncio.get_event_loop()

    def connect(self) -> None:
        """Gateway connect ."""
        self._mqtt.on_connect = self.on_connect
        self._mqtt.on_message = self.on_message
        self._mqtt.on_disconnect = self.on_disconnect
        self._mqtt.connect_async(self._ip, 1883)
        self._mqtt.loop_start()

    def disconnect(self) -> None:
        """Gateway disconnect ."""
        self._mqtt.disconnect()
        self._mqtt.loop_stop()

    def init_subscribe(self) -> None:
        """Init subscribe topic."""

    def on_connect(self, _, __, ___, ____, _____=None) -> None:
        """Mqtt connected callback."""
        # 订阅指令主题
        for topic in ALL_TOPICS:
            self._mqtt.subscribe(topic, qos=1)

    def on_message(self, _, __, msg):
        """Receive mqtt message."""
        topic = msg.topic
        payload = msg.payload.decode()
        _LOGGER.info("Received command: %s from %s", payload, msg.topic)
        if topic == "res/device/add":
            if self.on_device_add:
                data = json_to_bean(payload, list[Device])
                asyncio.run_coroutine_threadsafe(self.on_device_add(data), self.loop)
        if topic == "res/device/remove":
            if self.on_device_remove:
                data = json_to_bean(payload, list[Resource])
                asyncio.run_coroutine_threadsafe(self.on_device_remove(data), self.loop)
        if topic == "res/device/update":
            if self.on_device_update:
                data = json_to_bean(payload, list[DeviceUpdatePayload])
                asyncio.run_coroutine_threadsafe(self.on_device_update(data), self.loop)
        if topic == "res/light/update":
            if self.on_light_update:
                data = json_to_bean(payload, list[LightUpdatePayload])
                asyncio.run_coroutine_threadsafe(self.on_light_update(data), self.loop)

    @property
    def on_device_add(self):
        """Device add envent."""
        return self._on_device_add

    @on_device_add.setter
    def on_device_add(self, func: Callable | None) -> None:
        self._on_device_add = func

    @property
    def on_device_remove(self):
        """Device add envent."""
        return self._on_device_remove

    @on_device_remove.setter
    def on_device_remove(self, func: Callable | None) -> None:
        self._on_device_remove = func

    @property
    def on_device_update(self):
        """Device add envent."""
        return self._on_device_update

    @on_device_update.setter
    def on_device_update(self, func: Callable | None) -> None:
        self._on_device_update = func
        return self._on_device_update

    @property
    def on_light_update(self):
        """Device add envent."""
        return self._on_light_update

    @on_light_update.setter
    def on_light_update(self, func: Callable | None) -> None:
        self._on_light_update = func

    def on_disconnect(self, _, __, ___):
        """Mqtt disconnect."""
