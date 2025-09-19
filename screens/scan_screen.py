import flet as ft
import base64
from io import BytesIO
from PIL import Image
import cv2
import numpy as np

class ScanScreen:
    def __init__(self, app):
        self.app = app
        self.scan_type = "document"  # "document" or "selfie"
        self.captured_image = None

    def set_scan_type(self, scan_type: str):
        self.scan_type = scan_type
        self.captured_image = None

    def build(self):
        return ft.Column(
            controls=[
                # Header
                ft.AppBar(
                    title=ft.Text(
                        "Scanner Document" if self.scan_type == "document" else "Prendre Selfie",
                        weight=ft.FontWeight.BOLD
                    ),
                    leading=ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda e: self.app.navigate_to("home")
                    )
                ),
                
                # Zone de preview
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Positionnez votre document dans le cadre" if self.scan_type == "document" 
                            else "Centrez votre visage dans le cadre",
                            text_align=ft.TextAlign.CENTER
                        ),
                        self._build_image_preview(),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
                
                # Contrôles
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "📷 Prendre Photo",
                            icon=ft.icons.CAMERA,
                            on_click=self._take_photo,
                            expand=True
                        ),
                        ft.ElevatedButton(
                            "📁 Importer",
                            icon=ft.icons.FILE_UPLOAD,
                            on_click=self._pick_file,
                            expand=True
                        )
                    ],
                    spacing=20),
                    padding=20
                ),
                
                # Actions
                ft.Container(
                    content=ft.Row([
                        ft.FilledButton(
                            "✅ Utiliser cette image",
                            on_click=self._use_image,
                            disabled=self.captured_image is None
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                )
            ]
        )

    def _build_image_preview(self):
        if self.captured_image:
            # Afficher l'image capturée
            return ft.Image(
                src_base64=self.captured_image,
                width=300,
                height=400,
                fit=ft.ImageFit.CONTAIN,
                border_radius=10
            )
        else:
            # Afficher un placeholder
            return ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.icons.DOCUMENT_SCANNER if self.scan_type == "document" else ft.icons.CAMERA,
                        size=64,
                        color=ft.colors.GREY_400
                    ),
                    ft.Text(
                        "Aucune image capturée",
                        color=ft.colors.GREY_500
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=300,
                height=400,
                border=ft.border.all(2, ft.colors.GREY_300),
                border_radius=10,
                alignment=ft.alignment.center
            )

    def _take_photo(self, e):
        # Simuler la prise de photo (dans une vraie app, utiliser la caméra)
        self.app.page.snack_bar = ft.SnackBar(
            ft.Text("Fonctionnalité caméra à implémenter"),
            open=True
        )
        self.app.page.update()
        
        # Pour la démo, utiliser une image de test
        self._simulate_camera_capture()

    def _pick_file(self, e):
        # Simuler la sélection de fichier
        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                # Lire le fichier et le convertir en base64
                file_path = e.files[0].path
                with open(file_path, "rb") as f:
                    image_data = f.read()
                    self._process_image_data(image_data)
        
        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.app.page.overlay.append(file_picker)
        self.app.page.update()
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png"])

    def _simulate_camera_capture(self):
        # Utiliser une image de test selon le type de scan
        test_image_path = "assets/images/test_document.jpg" if self.scan_type == "document" else "assets/images/test_selfie.jpg"
        
        try:
            with open(test_image_path, "rb") as f:
                image_data = f.read()
                self._process_image_data(image_data)
        except FileNotFoundError:
            # Créer une image de test programmatiquement
            self._create_test_image()

    def _create_test_image(self):
        # Créer une image de test simple
        from PIL import Image, ImageDraw
        width, height = 300, 400
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        if self.scan_type == "document":
            draw.rectangle([50, 50, 250, 200], outline='black', width=2)
            draw.text((100, 220), "DOCUMENT TEST", fill='black')
        else:
            draw.ellipse([100, 100, 200, 200], outline='black', width=2)
            draw.text((120, 220), "SELFIE TEST", fill='black')
        
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        self._process_image_data(buffered.getvalue())

    def _process_image_data(self, image_data: bytes):
        # Prétraiter l'image si nécessaire
        processed_image = self._preprocess_image(image_data)
        
        # Convertir en base64 pour l'affichage
        self.captured_image = base64.b64encode(processed_image).decode('utf-8')
        self.app.page.update()

    def _preprocess_image(self, image_data: bytes) -> bytes:
        """Prétraite l'image pour améliorer la qualité"""
        try:
            image = Image.open(BytesIO(image_data))
            
            # Redimensionner si trop grande
            max_size = (800, 1000)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir en JPEG pour réduire la taille
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            
            return buffered.getvalue()
            
        except Exception as e:
            print(f"Erreur prétraitement image: {e}")
            return image_data

    def _use_image(self, e):
        if self.captured_image:
            # Décoder l'image base64
            image_data = base64.b64decode(self.captured_image)
            
            # Stocker dans l'application
            if self.scan_type == "document":
                self.app.scanned_document_data = image_data
            else:
                self.app.scanned_selfie_data = image_data
            
            self.app.page.snack_bar = ft.SnackBar(
                ft.Text("Image enregistrée avec succès"),
                open=True
            )
            self.app.navigate_to("home")