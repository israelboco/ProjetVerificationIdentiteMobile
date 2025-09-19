import flet as ft
from modules.api_client import APIClient

class HomeScreen:
    def __init__(self, app):
        self.app = app
        self.api_client = APIClient()

    def build(self):
        return ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Image(
                            src="assets/images/logo_anip.png",
                            width=120,
                            height=120,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Text(
                            "Vérification d'Identité ANIP",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            "Système intelligent de vérification d'identité",
                            size=16,
                            color=ft.colors.GREY_600,
                            text_align=ft.TextAlign.CENTER
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
                
                # Cards d'actions
                ft.Container(
                    content=ft.Column([
                        self._build_action_card(
                            "📄 Scanner Document",
                            "Scannez votre CNI, CIP ou passeport",
                            "scan_document"
                        ),
                        self._build_action_card(
                            "📸 Prendre Selfie",
                            "Prenez une photo de votre visage",
                            "take_selfie"
                        ),
                        self._build_action_card(
                            "✅ Vérifier Identité",
                            "Lancez la vérification complète",
                            "verify_identity"
                        ),
                        self._build_action_card(
                            "📊 Historique",
                            "Consultez vos vérifications",
                            "view_history"
                        )
                    ],
                    spacing=20),
                    padding=ft.padding.symmetric(horizontal=20)
                ),
                
                # Footer
                ft.Container(
                    content=ft.Text(
                        "© 2024 ANIP Bénin - Sécurisez votre identité",
                        size=12,
                        color=ft.colors.GREY_400,
                        text_align=ft.TextAlign.CENTER
                    ),
                    padding=20
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    def _build_action_card(self, title: str, description: str, action: str):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.DOCUMENT_SCANNER if "document" in action else 
                                      ft.icons.CAMERA_ALT if "selfie" in action else
                                      ft.icons.VERIFIED if "verify" in action else
                                      ft.icons.HISTORY),
                        title=ft.Text(title, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(description),
                    ),
                    ft.Row([
                        ft.TextButton(
                            "Commencer →",
                            on_click=lambda e: self._handle_action(action)
                        )
                    ], alignment=ft.MainAxisAlignment.END)
                ]),
                padding=10,
                on_click=lambda e: self._handle_action(action)
            ),
            elevation=2,
            margin=5
        )

    def _handle_action(self, action: str):
        if action == "scan_document":
            self.app.navigate_to("scan", scan_type="document")
        elif action == "take_selfie":
            self.app.navigate_to("scan", scan_type="selfie")
        elif action == "verify_identity":
            self._verify_identity()
        elif action == "view_history":
            self.app.navigate_to("history")

    def _verify_identity(self):
        document_data, selfie_data = self.app.get_scanned_data()
        
        if not document_data or not selfie_data:
            self.app.page.snack_bar = ft.SnackBar(
                ft.Text("Veuillez d'abord scanner un document et prendre un selfie"),
                open=True
            )
            self.app.page.update()
            return
        
        # Afficher un indicateur de chargement
        self.app.page.snack_bar = ft.SnackBar(
            ft.Row([
                ft.ProgressRing(width=20, height=20),
                ft.Text("Vérification en cours...")
            ]),
            open=True
        )
        self.app.page.update()
        
        # Appel API
        result = self.api_client.verify_identity(document_data, selfie_data)
        
        if result:
            self.app.navigate_to("result", result_data=result)
        else:
            self.app.page.snack_bar = ft.SnackBar(
                ft.Text("Erreur lors de la vérification"),
                open=True
            )
            self.app.page.update()