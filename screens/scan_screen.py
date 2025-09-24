import flet as ft
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import threading
import logging
import time

from modules.api_client import APIClient

class ScanScreen:
    def __init__(self, app):
        self.app = app
        self.scan_type = "document"  # "document" or "selfie"
        self.captured_image = None
        self.api_client = APIClient()
        
        # Gestion de la prévisualisation
        self._preview_running = False
        self._preview_thread = None
        self._preview_frame_bytes = None
        self._preview_image_base64 = None
        self._preview_lock = threading.Lock()
        self._preview_opened_by_user = False
        
        # Configuration caméra
        self.use_native_camera = False
        self.camera_index = 0  # 0 = arrière par défaut, 1 = avant
        self.available_cameras = {0: "📷 Caméra arrière", 1: "🤳 Caméra avant"}
        self.image_widget = None
        
        # Contrôles UI
        self._image_preview_container = ft.Container(
            width=350,
            height=450,
            border=ft.border.all(3, ft.Colors.BLUE_300),
            border_radius=15,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.GREY_100
        )
        self._take_photo_button = None
        self._use_button = None
        self._camera_selector = None
        
        # Données d'image
        self._last_captured_bytes = None

    def set_scan_type(self, scan_type: str):
        """Définit le type de scan (document ou selfie)"""
        self.scan_type = scan_type
        self.captured_image = None
        self._last_captured_bytes = None
        self._reset_preview_state()

    def build(self):
        """Construit l'interface utilisateur de l'écran de scan"""
        # Configuration de la barre d'application
        self.app.page.appbar = ft.AppBar(
            title=ft.Text(
                "📄 Scanner Document" if self.scan_type == "document" else "🤳 Prendre Selfie",
                weight=ft.FontWeight.BOLD,
                size=20
            ),
            bgcolor=ft.Colors.BLUE_700,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=self._on_back
            ),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.HELP_OUTLINE,
                    icon_color=ft.Colors.WHITE,
                    on_click=self._show_help
                )
            ]
        )

        # Initialisation des contrôles
        self._initialize_controls()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Instructions
                    self._build_instructions(),
                    
                    # Zone de prévisualisation
                    self._build_preview_section(),
                    
                    # Sélecteur de caméra
                    self._build_camera_selector(),
                    
                    # Contrôles de capture
                    self._build_controls_section(),
                    
                    # Actions principales
                    self._build_actions_section(),
                    
                    # Indicateur de statut
                    self._build_status_indicator()
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
            expand=True
        )

    def _initialize_controls(self):
        """Initialise les contrôles interactifs"""
        # Bouton de capture photo
        self._take_photo_button = ft.ElevatedButton(
            "📷 Ouvrir caméra",
            icon=ft.Icons.CAMERA,
            on_click=self._take_photo,
            expand=True,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600
            )
        )
        
        # Bouton d'utilisation d'image
        self._use_button = ft.FilledButton(
            "✅ Utiliser cette image",
            on_click=self._use_image,
            disabled=True,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600
            )
        )
        
        # Sélecteur de caméra
        self._camera_selector = ft.Dropdown(
            label="Choisir la caméra",
            options=[
                ft.dropdown.Option(str(idx), text=label) 
                for idx, label in self.available_cameras.items()
            ],
            value=str(self.camera_index),
            on_change=self._on_camera_change,
            expand=True,
            visible=len(self.available_cameras) > 1
        )

    def _build_instructions(self):
        """Construit la section d'instructions"""
        instructions = {
            "document": "📋 Positionnez votre document dans le cadre\n• Assurez-vous que le document est bien éclairé\n• Maintenez le document stable\n• Vérifiez que tout le texte est visible",
            "selfie": "👤 Centrez votre visage dans le cadre\n• Regardez droit devant la caméra\n• Assurez-vous d'avoir un bon éclairage\n• Enlevez les lunettes de soleil si nécessaire"
        }
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    instructions[self.scan_type],
                    size=14,
                    color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.CENTER
                )
            ]),
            padding=10,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10
        )

    def _build_preview_section(self):
        """Construit la section de prévisualisation"""
        self._image_preview_container = ft.Container(
            width=350,
            height=450,
            border=ft.border.all(3, ft.Colors.BLUE_300),
            border_radius=15,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.GREY_100
        )
        
        # Initialiser avec le placeholder
        self._set_preview_placeholder()
        
        return self._image_preview_container

    def _build_camera_selector(self):
        """Construit le sélecteur de caméra"""
        return ft.Container(
            content=self._camera_selector,
            padding=ft.padding.symmetric(horizontal=20),
            visible=len(self.available_cameras) > 1
        )

    def _build_controls_section(self):
        """Construit la section des contrôles"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self._take_photo_button,
                    ft.ElevatedButton(
                        "📁 Importer fichier",
                        icon=ft.Icons.FILE_UPLOAD,
                        on_click=self._pick_file,
                        expand=True,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_600,
                            bgcolor=ft.Colors.WHITE
                        )
                    )
                ], spacing=15),
                
                ft.Row([
                    ft.ElevatedButton(
                        "🔄 Réinitialiser",
                        icon=ft.Icons.REFRESH,
                        on_click=self._reset_capture,
                        expand=True
                    ),
                    ft.ElevatedButton(
                        "💡 Aide capture",
                        icon=ft.Icons.LIGHTBULB,
                        on_click=self._show_capture_tips,
                        expand=True
                    )
                ], spacing=15)
            ], spacing=10),
            padding=10
        )

    def _build_actions_section(self):
        """Construit la section des actions principales"""
        return ft.Container(
            content=ft.Row([
                self._use_button,
                ft.OutlinedButton(
                    "📊 Vérifier maintenant",
                    icon=ft.Icons.VERIFIED,
                    on_click=self._verify_immediately,
                    disabled=True
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            padding=10
        )

    def _build_status_indicator(self):
        """Construit l'indicateur de statut"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.CIRCLE,
                    color=ft.Colors.RED if not self.captured_image else ft.Colors.GREEN,
                    size=12
                ),
                ft.Text(
                    "Prêt à capturer" if not self.captured_image else "Image capturée",
                    size=12,
                    color=ft.Colors.GREY_600
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=5
        )

    def _set_preview_placeholder(self):
        """Affiche le placeholder dans le conteneur de prévisualisation"""
        icon = ft.Icons.DOCUMENT_SCANNER if self.scan_type == "document" else ft.Icons.FACE
        text = "Document" if self.scan_type == "document" else "Selfie"
        
        self._image_preview_container.content = ft.Column(
            [
                ft.Icon(icon, size=80, color=ft.Colors.BLUE_300),
                ft.Text(f"Aucun {text} capturé", size=16, color=ft.Colors.GREY_500),
                ft.Text("Cliquez sur 'Ouvrir caméra' pour commencer", 
                       size=12, color=ft.Colors.GREY_400)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

    def _update_preview_with_image(self, base64_str: str):
        """Met à jour la prévisualisation avec une image base64"""
        try:
            if self.image_widget is None:
                self.image_widget = ft.Image(
                    src_base64=base64_str,
                    width=340,
                    height=440,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=10
                )
                
                self._image_preview_container.content = ft.Stack([
                    self.image_widget,
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20),
                            ft.Text("Image capturée", color=ft.Colors.GREEN, size=12)
                        ]),
                        top=10,
                        right=10,
                        bgcolor=ft.Colors.WHITE,
                        padding=5,
                        border_radius=5
                    )
                ])
            else:
                self.image_widget.src_base64 = base64_str
            
            self.app.page.update()
        except Exception as e:
            logging.error(f"Erreur mise à jour prévisualisation: {e}")

    def _on_camera_change(self, e: ft.ControlEvent):
        """Gère le changement de caméra"""
        try:
            new_index = int(e.control.value)
            if new_index != self.camera_index:
                self.camera_index = new_index
                logging.info(f"Caméra changée: {self.available_cameras.get(new_index, new_index)}")

                # Redémarrer la prévisualisation si active
                if self._preview_running:
                    self.stop_camera_preview()
                    time.sleep(0.5)  # Pause courte
                    self.start_camera_preview()
                    
        except Exception as ex:
            logging.error(f"Erreur changement caméra: {ex}")
            self._show_snackbar("❌ Erreur changement caméra")

    def _on_back(self, e):
        """Gère le retour à l'écran précédent"""
        try:
            self.stop_camera_preview()
        except Exception:
            pass
        self.app.navigate_to("home")

    def _take_photo(self, e):
        """Gère la capture de photo"""
        self._show_snackbar("📷 Préparation de la capture...")
        
        # Premier clic : ouvrir la prévisualisation
        if not self._preview_running:
            try:
                self.start_camera_preview()
                self._preview_opened_by_user = True
                self._take_photo_button.text = "📸 Capturer maintenant"
                self.app.page.update()
                return
            except Exception as ex:
                logging.error(f"Erreur démarrage caméra: {ex}")
                self._show_snackbar("❌ Impossible d'ouvrir la caméra")
                return

        # Deuxième clic : capturer l'image
        try:
            with self._preview_lock:
                frame_bytes = self._preview_frame_bytes

            if frame_bytes:
                processed_image = self._preprocess_image(frame_bytes)
                self.captured_image = base64.b64encode(processed_image).decode('utf-8')
                self._last_captured_bytes = processed_image
                
                # Mettre à jour l'interface
                self._update_preview_with_image(self.captured_image)
                self._use_button.disabled = False
                
                # Arrêter la prévisualisation si ouverte par l'utilisateur
                if self._preview_opened_by_user:
                    self.stop_camera_preview()
                    self._preview_opened_by_user = False
                    self._take_photo_button.text = "📷 Ouvrir caméra"
                
                self._show_snackbar("✅ Photo capturée avec succès!")
                
                # Envoyer à l'API en arrière-plan
                # self._send_to_api_background(processed_image)
                
            else:
                self._show_snackbar("❌ Aucune image disponible")
                
        except Exception as ex:
            logging.error(f"Erreur capture photo: {ex}")
            self._show_snackbar("❌ Erreur lors de la capture")

    def start_camera_preview(self):
        """Démarre la prévisualisation caméra"""
        if self._preview_running:
            return
            
        if self.use_native_camera:
            return self._start_native_camera()

        self._preview_running = True

        def preview_loop():
            cap = None
            try:
                cap = cv2.VideoCapture(self.camera_index)
                if not cap.isOpened():
                    raise RuntimeError("Caméra non disponible")

                while self._preview_running:
                    ret, frame = cap.read()
                    if not ret:
                        continue

                    # Traitement de l'image
                    frame = self._enhance_frame(frame)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Conversion en JPEG
                    pil_image = Image.fromarray(frame_rgb)
                    buffer = BytesIO()
                    pil_image.save(buffer, format="JPEG", quality=70)
                    jpeg_data = buffer.getvalue()

                    # Mise à jour des données de prévisualisation
                    with self._preview_lock:
                        self._preview_frame_bytes = jpeg_data
                        self._preview_image_base64 = base64.b64encode(jpeg_data).decode('utf-8')

                    # Mise à jour de l'interface
                    self._update_ui_preview()
                    
                    time.sleep(0.033)  # ~30 FPS

            except Exception as e:
                logging.error(f"Erreur prévisualisation: {e}")
                self._preview_running = False
            finally:
                if cap:
                    cap.release()

        self._preview_thread = threading.Thread(target=preview_loop, daemon=True)
        self._preview_thread.start()

    def _enhance_frame(self, frame):
        """Améliore la qualité de l'image"""
        try:
            # Ajustement de la luminosité et contraste
            alpha = 1.2  # Contraste
            beta = 10    # Luminosité
            frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
            
            # Réduction du bruit
            frame = cv2.medianBlur(frame, 3)
            
            return frame
        except:
            return frame

    def _update_ui_preview(self):
        """Met à jour la prévisualisation dans l'interface"""
        try:
            if self._preview_image_base64:
                self._update_preview_with_image(self._preview_image_base64)
                # self.app.page.run_task(
                #     lambda: self._update_preview_with_image(self._preview_image_base64)
                # )
        except Exception as e:
            logging.error(f"Erreur mise à jour UI: {e}")

    def stop_camera_preview(self):
        """Arrête la prévisualisation caméra"""
        self._preview_running = False
        self.image_widget = None
        if self.use_native_camera:
            self._stop_native_camera()

    def _start_native_camera(self):
        """Démarre la caméra native (Android)"""
        try:
            self.app.page.invoke_method(
                "start_camera",
                {"camera_index": self.camera_index}
            )
            logging.info(f"Caméra native démarrée (index={self.camera_index})")
        except Exception as e:
            logging.error(f"Erreur caméra native: {e}")

    def _stop_native_camera(self):
        """Arrête la caméra native"""
        try:
            self.app.page.invoke_method("stop_camera", {})
            logging.info("Caméra native arrêtée")
        except Exception as e:
            logging.error(f"Erreur arrêt caméra native: {e}")

    def _pick_file(self, e):
        """Gère la sélection de fichier"""
        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                try:
                    file_path = e.files[0].path
                    with open(file_path, "rb") as f:
                        image_data = f.read()
                    
                    self.stop_camera_preview()
                    self._process_image_data(image_data)
                    self._show_snackbar("✅ Fichier importé avec succès")
                    
                except Exception as ex:
                    logging.error(f"Erreur import fichier: {ex}")
                    self._show_snackbar("❌ Erreur lors de l'import")

        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.app.page.overlay.append(file_picker)
        file_picker.pick_files(
            allow_multiple=False, 
            allowed_extensions=["jpg", "jpeg", "png", "bmp", "webp"]
        )

    def _process_image_data(self, image_data: bytes):
        """Traite les données d'image"""
        try:
            processed_image = self._preprocess_image(image_data)
            self._last_captured_bytes = processed_image
            self.captured_image = base64.b64encode(processed_image).decode('utf-8')
            
            self._update_preview_with_image(self.captured_image)
            self._use_button.disabled = False
            
            # Envoyer à l'API
            # self._send_to_api_background(processed_image)
            
            self.app.page.update()
        except Exception as e:
            logging.error(f"Erreur traitement image: {e}")

    def _preprocess_image(self, image_data: bytes) -> bytes:
        """Prétraite l'image pour améliorer la qualité"""
        try:
            image = Image.open(BytesIO(image_data))
            
            # Redimensionnement intelligent
            max_size = (1200, 1600)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Conversion en JPEG
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=85, optimize=True)
            
            return buffer.getvalue()
            
        except Exception as e:
            logging.error(f"Erreur prétraitement: {e}")
            return image_data

    def _use_image(self, e):
        """Utilise l'image capturée"""
        if not self.captured_image or not self._last_captured_bytes:
            self._show_snackbar("❌ Aucune image à utiliser")
            return

        try:
            # Stocker l'image dans l'application
            if self.scan_type == "document":
                self.app.scanned_document_data = self._last_captured_bytes
                self._show_snackbar("✅ Document enregistré")
            else:
                self.app.scanned_selfie_data = self._last_captured_bytes
                self._show_snackbar("✅ Selfie enregistré")

            # Vérifier si on peut lancer la vérification
            if (hasattr(self.app, 'scanned_document_data') and 
                hasattr(self.app, 'scanned_selfie_data') and
                self.app.scanned_document_data and self.app.scanned_selfie_data):
                
                self._launch_verification()
            else:
                # Retour à l'accueil
                self._reset_capture()
                self.app.navigate_to("home")

        except Exception as ex:
            logging.error(f"Erreur utilisation image: {ex}")
            self._show_snackbar("❌ Erreur lors de l'utilisation")

    def _launch_verification(self):
        """Lance la vérification d'identité"""
        self._show_snackbar("🔍 Vérification en cours...")
        
        def verify_thread():
            try:
                document_data = self.app.scanned_document_data
                selfie_data = self.app.scanned_selfie_data
                
                if not document_data or not selfie_data:
                    self._show_snackbar("❌ Données manquantes")
                    return

                result = self.api_client.verify_identity(document_data, selfie_data)
                
                if result:
                    self.app.page.run_task(
                        lambda: self.app.navigate_to("result", result_data=result)
                    )
                else:
                    self._show_snackbar("❌ Échec de la vérification")
                    
            except Exception as ex:
                logging.error(f"Erreur vérification: {ex}")
                self._show_snackbar("❌ Erreur lors de la vérification")

        threading.Thread(target=verify_thread, daemon=True).start()

    def _verify_immediately(self, e):
        """Lance la vérification immédiate"""
        if self.captured_image and self._last_captured_bytes:
            self._use_image(e)
        else:
            self._show_snackbar("❌ Aucune image capturée")

    def _reset_capture(self, e=None):
        """Réinitialise la capture"""
        self.captured_image = None
        self._last_captured_bytes = None
        self._reset_preview_state()
        self._show_snackbar("🔄 Capture réinitialisée")

    def _reset_preview_state(self):
        """Réinitialise l'état de prévisualisation"""
        self._set_preview_placeholder()
        if self._use_button:
            self._use_button.disabled = True
        if self._take_photo_button:
            self._take_photo_button.text = "📷 Ouvrir caméra"
        self.app.page.update()

    def _send_to_api_background(self, image_bytes: bytes):
        """Envoie l'image à l'API en arrière-plan"""
        def api_thread():
            try:
                if self.scan_type == "document":
                    result = self.api_client.extract_ocr(image_bytes)
                    if result:
                        self.app.ocr_result = result
                        logging.info("OCR réussi")
                else:
                    logging.info("Selfie prêt pour vérification")
                    
            except Exception as e:
                logging.error(f"Erreur API: {e}")

        threading.Thread(target=api_thread, daemon=True).start()

    def _show_snackbar(self, message: str):
        """Affiche un message snackbar"""
        try:
            show_snack_bar = ft.SnackBar(ft.Text(message), open=True)
            self.app.page.open(show_snack_bar)
            self.app.page.update()
        except:
            pass

    def _show_help(self, e):
        """Affiche l'aide"""
        self._show_snackbar("ℹ️ Aide: Capturez un document puis un selfie")

    def _show_capture_tips(self, e):
        """Affiche les conseils de capture"""
        tips = {
            "document": "• Bon éclairage\n• Document à plat\n• Texte visible\n• Pas de reflets",
            "selfie": "• Visage centré\n• Bon éclairage\n• Expression neutre\n• Fond simple"
        }
        self._show_snackbar(f"💡 Conseils: {tips[self.scan_type]}")

    def push_native_frame(self, frame_bytes: bytes):
        """Reçoit les frames de la caméra native (Android)"""
        if not self._preview_running:
            return
            
        try:
            with self._preview_lock:
                self._preview_frame_bytes = frame_bytes
                self._preview_image_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            
            self._update_ui_preview()
        except Exception as e:
            logging.error(f"Erreur frame native: {e}")