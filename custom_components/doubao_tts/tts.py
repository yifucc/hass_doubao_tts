"""Doubao TTS."""
from __future__ import annotations

import json
import uuid
import logging
import websockets
from typing import Any
from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType
from .protocols import full_client_request, receive_message, MsgType, EventType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
WS_URL = "wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream"

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    entity = DoubaoTTSEntity(hass, config_entry)
    async_add_entities([entity])


class DoubaoTTSEntity(TextToSpeechEntity):
    _attr_name = "Doubao TTS"

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self.hass = hass
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}-tts"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": "Doubao TTS",
            "manufacturer": "Doubao",
            "model": "TTS",
            "entry_type": DeviceEntryType.SERVICE,
        }

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

        speaker = options.get("speaker", "zh_female_qingxinnvsheng_uranus_bigtts")

        headers = {
            "X-Api-App-Key": self._app_id,
            "X-Api-Access-Key": self._access_key,
            "X-Api-Resource-Id": self._resource_id,
            "X-Api-Connect-Id": str(uuid.uuid4()),
        }

        _LOGGER.info(f"Connecting to {WS_URL} with headers: {headers}")
        websocket = await websockets.connect(
            WS_URL, additional_headers=headers, max_size=10 * 1024 * 1024
        )
        _LOGGER.info(
            f"Connected to WebSocket server, Logid: {websocket.response.headers['x-tt-logid']}",
        )

        try:
            # Prepare request payload
            request = {
                "user": {
                    "uid": str(uuid.uuid4()),
                },
                "req_params": {
                    "speaker": speaker,
                    "audio_params": {
                        "format": "mp3",
                        "sample_rate": 24000,
                        "enable_timestamp": True,
                    },
                    "text": message,
                    "additions": json.dumps(
                        {
                            "disable_markdown_filter": False,
                        }
                    ),
                },
            }

            # Send request
            await full_client_request(websocket, json.dumps(request).encode())

            # Receive audio data
            audio = bytearray()
            while True:
                msg = await receive_message(websocket)

                if msg.type == MsgType.FullServerResponse:
                    if msg.event == EventType.SessionFinished:
                        break
                elif msg.type == MsgType.AudioOnlyServer:
                    audio.extend(msg.payload)
                else:
                    raise RuntimeError(f"TTS conversion failed: {msg}")

            # Check if we received any audio data
            if not audio:
                raise RuntimeError("No audio data received")

        finally:
            await websocket.close()

        return "mp3", audio
