from __future__ import annotations

from typing import Final

DOMAIN: Final = "doubao_tts"
WS_URL: Final = "wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream"

CONF_APP_ID: Final = "app_id"
CONF_ACCESS_KEY: Final = "access_key"
CONF_VOICE: Final = "voice"
CONF_SPEED: Final = "speed"
CONF_VOLUME: Final = "volume"
CONF_RESOURCE_ID: Final = "resource_id"
CONF_SAMPLE_RATE: Final = "sample_rate"
CONF_EMOTION: Final = "emotion"
CONF_CONTEXT_TEXTS: Final = "context_texts"

SPEED_MIN: Final = -50
SPEED_MAX: Final = 100
SPEED_STEP: Final = 1

VOLUME_MIN: Final = -50
VOLUME_MAX: Final = 100
VOLUME_STEP: Final = 1

DEFAULT_TITLE: Final = "Doubao TTS"
DEFAULT_LANGUAGE: Final = "zh-CN"
DEFAULT_VOICE: Final = "zh_female_vv_uranus_bigtts"
DEFAULT_SAMPLE_RATE: Final = 24000
DEFAULT_SPEED: Final = 0
DEFAULT_VOLUME: Final = 0
