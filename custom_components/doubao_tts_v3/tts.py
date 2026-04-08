import json
import uuid
import struct
import websockets
from homeassistant.components.tts import Provider, TtsAudioType

from .const import (
    WS_URL,
    DEFAULT_SPEAKER,
    DEFAULT_FORMAT,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_SPEECH_RATE,
    DEFAULT_LOUDNESS_RATE
)

class DoubaoTTSV3Provider(Provider):
    def __init__(self, hass, app_id, access_key, resource_id):
        self.hass = hass
        self.app_id = app_id
        self.access_key = access_key
        self.resource_id = resource_id
        self.name = "豆包TTS V3"

    @property
    def default_language(self):
        return "zh"

    @property
    def supported_languages(self):
        return ["zh"]

    @property
    def supported_options(self):
        return ["speaker", "speed", "volume", "format"]

    def _build_frame(self, payload: dict) -> bytes:
        header = bytes([0x11, 0x10, 0x10, 0x00])
        payload_bytes = json.dumps(payload).encode("utf-8")
        length = struct.pack(">I", len(payload_bytes))
        return header + length + payload_bytes

    async def async_get_tts_audio(self, message, language, options):
        speaker = options.get("speaker", DEFAULT_SPEAKER)
        fmt = options.get("format", DEFAULT_FORMAT)
        sample_rate = options.get("sample_rate", DEFAULT_SAMPLE_RATE)
        speed = options.get("speed", DEFAULT_SPEECH_RATE)
        volume = options.get("volume", DEFAULT_LOUDNESS_RATE)

        payload = {
            "user": {"uid": "homeassistant"},
            "namespace": "BidirectionalTTS",
            "req_params": {
                "text": message,
                "speaker": speaker,
                "model": "seed-tts-2.0-standard",
                "audio_params": {
                    "format": fmt,
                    "sample_rate": sample_rate,
                    "speech_rate": speed,
                    "loudness_rate": volume
                },
                "additions": {"disable_markdown_filter": True}
            }
        }

        headers = {
            "X-Api-App-Id": self.app_id,
            "X-Api-Access-Key": self.access_key,
            "X-Api-Resource-Id": self.resource_id,
            "X-Api-Request-Id": str(uuid.uuid4()),
        }

        audio = b""
        async with websockets.connect(WS_URL, extra_headers=headers, timeout=20) as ws:
            await ws.send(self._build_frame(payload))

            while True:
                msg = await ws.recv()
                if not isinstance(msg, bytes):
                    continue

                payload_len = struct.unpack(">I", msg[4:8])[0]
                payload_raw = msg[8:8+payload_len]
                data = json.loads(payload_raw)

                if data.get("event") == 352:
                    audio += bytes(data["data"])
                if data.get("event") == 152:
                    break

        return (fmt, audio)

async def async_setup_entry(hass, entry, async_add_entities):
    app_id = entry.data["app_id"]
    access_key = entry.data["access_key"]
    resource_id = entry.data["resource_id"]

    provider = DoubaoTTSV3Provider(hass, app_id, access_key, resource_id)
    async_add_entities([provider])