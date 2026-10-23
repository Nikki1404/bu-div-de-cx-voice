import os

APP_NAME = os.getenv("APP_NAME", "Speech AI API")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_BASE_PATH = os.getenv("APP_BASE_PATH", "/apps/voice-biometric").strip()
if APP_BASE_PATH:
	APP_BASE_PATH = "/" + APP_BASE_PATH.strip("/")
if APP_BASE_PATH == "/":
	APP_BASE_PATH = ""