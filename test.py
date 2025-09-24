from flet_camera import Camera
import flet as ft
import asyncio  
import logging
from modules.api_client import APIClient
from modules.ui_utils import install_call_from_async
from screens.home_screen import HomeScreen
from screens.scan_screen import ScanScreen
from screens.result_screen import ResultScreen
from screens.history_screen import HistoryScreen
from typing import Optional, Dict
import os
import sys
import threading   
import time
import json
import base64
import datetime
import tempfile
import platform
import traceback
import webbrowser
import uuid
import requests
from io import BytesIO
from PIL import Image
from functools import partial
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCameraApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Test Camera"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20

        self.camera: Optional[Camera] = None
        self.captured_image: Optional[bytes] = None
        self.image_display: Optional[ft.Image] = None

        self.init_ui()

    def init_ui(self):
        self.camera = Camera(
            on_frame_captured=self.on_frame_captured,
            width=400,
            height=300,
            fit=ft.ImageFit.COVER,
            border_radius=10,
            border_color=ft.colors.BLUE,
            border_width=2,
        )

        capture_button = ft.ElevatedButton(
            text="Capture Image",
            on_click=self.capture_image
        )

        self.image_display = ft.Image(
            src="",
            width=400,
            height=300,
            fit=ft.ImageFit.CONTAIN,
            border_radius=10,
            border_color=ft.colors.GREEN,
            border_width=2,
        )

        self.page.add(
            self.camera,
            capture_button,
            self.image_display
        )

    def on_frame_captured(self, frame: bytes):
        # Callback when a frame is captured from the camera
        pass

    def capture_image(self, e):
        if self.camera:
            self.captured_image = self.camera.capture()
            if self.captured_image:
                image_data_url = "data:image/jpeg;base64," + base64.b64encode(self.captured_image).decode('utf-8')
                self.image_display.src = image_data_url
                self.image_display.update()
                logger.info("Image captured and displayed.")
            else:
                logger.error("Failed to capture image.")
        else:
            logger.error("Camera is not initialized.")