from __future__ import annotations

import json
import uuid
import logging
import websockets
import ssl
from typing import Any
from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.components.tts import ATTR_VOICE, Voice
from .protocols import full_client_request, receive_message, MsgType, EventType
from .const import DOMAIN, WS_URL, DEFAULT_VOICE, DEFAULT_SAMPLE_RATE, DEFAULT_SPEED, DEFAULT_VOLUME, DEFAULT_LANGUAGE
from .voice_const import SUPPORTED_VOICES

_LOGGER = logging.getLogger(__name__)

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
            "model": "Cloud TTS",
            "entry_type": DeviceEntryType.SERVICE,
        }

        self._app_id = config_entry.data["app_id"]
        self._access_key = config_entry.data["access_key"]
        self._resource_id = config_entry.data["resource_id"]

    @property
    def default_language(self) -> str:
        return DEFAULT_LANGUAGE

    @property
    def supported_languages(self) -> list[str]:
        return list({lang for voice in SUPPORTED_VOICES.values() for lang in voice["languages"]})

    @property
    def supported_options(self) -> list[str]:
        return [ATTR_VOICE, "speaker", "speed", "volume", "resource_id", "sample_rate", "emotion", "context_texts"]
    
    @callback
    def async_get_supported_voices(self, language: str) -> list[Voice]:
        return list({Voice(voice_id, voice_info["name"]) for voice_id, voice_info in SUPPORTED_VOICES.items()})

    async def async_get_tts_audio(
            self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:

        voice = options.get(ATTR_VOICE) or options.get("speaker", DEFAULT_VOICE)
        resource_id = options.get("resource_id")
        if not resource_id:
            voice_conf = SUPPORTED_VOICES.get(voice)
            if voice_conf:
                resource_id = voice_conf.get("resource_id")
        sample_rate = options.get("sample_rate", DEFAULT_SAMPLE_RATE)
        emotion = options.get("emotion", "")
        context_texts = options.get("context_texts", "")
        speed = options.get("speed", DEFAULT_SPEED)
        volume = options.get("volume", DEFAULT_VOLUME)

        headers = {
            "X-Api-App-Key": self._app_id,
            "X-Api-Access-Key": self._access_key,
            "X-Api-Resource-Id": resource_id,
            "X-Api-Connect-Id": str(uuid.uuid4()),
        }
        _LOGGER.info(f"Connecting to {WS_URL} with headers: {headers}")
        ssl_context = await self.hass.async_add_executor_job(
            lambda: ssl.create_default_context()
        )
        websocket = await websockets.connect(
            WS_URL,
            additional_headers=headers,
            max_size=10 * 1024 * 1024,
            ssl=ssl_context,
        )
        try:
            request = {
                "user": {"uid": str(uuid.uuid4())},
                "req_params": {
                    "speaker": voice,
                    "audio_params": {
                        "format": "mp3",
                        "sample_rate": int(sample_rate),
                        "speech_rate": int(speed),
                        "loudness_rate": int(volume),
                        "enable_timestamp": True,
                        **({"emotion": emotion.strip()} if emotion and emotion.strip() else {})
                    },
                    "text": message,
                    "additions": json.dumps({
                            "disable_markdown_filter": False,
                            **({"context_texts": context_texts.strip()} if context_texts and context_texts.strip() else {})
                        }
                    ),
                },
            }

            payload = json.dumps(request).encode()
            await full_client_request(websocket, payload)
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
            if not audio:
                raise RuntimeError("No audio data received")
        finally:
            await websocket.close()

        return "mp3", bytes(audio)
