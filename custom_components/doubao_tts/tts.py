"""Doubao TTS implementation."""
from __future__ import annotations
import json
import uuid
import struct
import websockets
from homeassistant.components.tts import Provider, TtsAudioType

WS_URL = "wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream"

class DoubaoTTSProvider(Provider):
    def __init__(self, app_id: str, access_key: str, resource_id: str):
        self._app_id = app_id
        self._access_key = access_key
        self._resource_id = resource_id

    @property
    def name(self):
        return "Doubao TTS"

    @property
    def default_language(self):
        return "zh"

    @property
    def supported_languages(self):
        return ["zh"]

    @property
    def supported_options(self):
        return ["speaker", "speed", "volume"]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict
    ) -> TtsAudioType:
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

        return ("mp3", audio)

async def async_setup_entry(hass, entry, async_add_entities):
    app_id = entry.data["app_id"]
    access_key = entry.data["access_key"]
    resource_id = entry.data["resource_id"]

    async_add_entities([
        DoubaoTTSProvider(app_id, access_key, resource_id)
    ], True)