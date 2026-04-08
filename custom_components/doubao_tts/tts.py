"""Doubao TTS."""
from __future__ import annotations

import json
import uuid
import struct
import logging
import websockets
from homeassistant.components.tts import (
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
WS_URL = "wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Doubao TTS entity from config entry."""
    entity = DoubaoTTSEntity(hass, config_entry)
    async_add_entities([entity])


class DoubaoTTSEntity(TextToSpeechEntity):
    """Doubao TTS Entity."""

    _attr_name = "Doubao TTS"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize TTS entity."""
        self.hass = hass
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}-tts"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "Doubao TTS Service",
            "manufacturer": "Doubao",
            "model": "Cloud TTS",
            "entry_type": DeviceEntryType.SERVICE,
        }
        # 从配置中读取密钥
        self._app_id = config_entry.data["app_id"]
        self._access_key = config_entry.data["access_key"]
        self._resource_id = config_entry.data["resource_id"]

    @property
    def default_language(self) -> str:
        return "zh"

    @property
    def supported_languages(self) -> list[str]:
        return ["zh"]

    @property
    def supported_options(self) -> list[str]:
        return ["speaker", "speed", "volume"]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """获取 TTS 音频。"""
        speaker = options.get("speaker", "zh_female_shuangkuaisisi_moon_bigtts")
        speed = int(options.get("speed", 0))
        volume = int(options.get("volume", 0))

        payload = {
            "user": {"uid": "homeassistant"},
            "namespace": "BidirectionalTTS",
            "req_params": {
                "text": message,
                "speaker": speaker,
                "model": "seed-tts-2.0-standard",
                "audio_params": {
                    "format": "mp3",
                    "sample_rate": 24000,
                    "speech_rate": speed,
                    "loudness_rate": volume
                },
                "additions": {"disable_markdown_filter": True}
            }
        }

        headers = {
            "X-Api-App-Id": self._app_id,
            "X-Api-Access-Key": self._access_key,
            "X-Api-Resource-Id": self._resource_id,
            "X-Api-Request-Id": str(uuid.uuid4()),
        }

        audio = b""
        try:
            async with websockets.connect(WS_URL, extra_headers=headers) as ws:
                header = bytes([0x11, 0x10, 0x10, 0x00])
                payload_bytes = json.dumps(payload).encode("utf-8")
                frame = header + struct.pack(">I", len(payload_bytes)) + payload_bytes
                await ws.send(frame)

                while True:
                    msg = await ws.recv()
                    if not isinstance(msg, bytes):
                        continue
                    payload_len = struct.unpack(">I", msg[4:8])[0]
                    data = json.loads(msg[8:8+payload_len])
                    if data.get("event") == 352:
                        audio += bytes(data["data"])
                    if data.get("event") == 152:
                        break
        except Exception as e:
            _LOGGER.error("Doubao TTS error: %s", e)
            return None, None

        return ("mp3", audio)