import flet as ft
from modules.api_client import APIClient
from datetime import datetime
import random

class HomeScreen:
    def __init__(self, app):
        self.app = app
        self.api_client = APIClient()
        self.show_dialog = None
        # Statistiques fictives pour l'exemple
        self._stats = {
            'total_verifications': 42,
            'success_rate': 89,
            'last_verification': '2024-01-15 14:30'
        }

    def build(self):
        # Configuration de la barre d'application moderne
        self.app.page.appbar = ft.AppBar(
            title=ft.Row([
                ft.Icon(ft.Icons.FINGERPRINT, color=ft.Colors.WHITE, size=28),
                ft.Text("ANIP Vérification", 
                       size=22, 
                       weight=ft.FontWeight.BOLD),
            ]),
            bgcolor=ft.Colors.BLUE_700,
            center_title=False,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.NOTIFICATIONS,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Notifications",
                    on_click=self._show_notifications
                ),
                ft.IconButton(
                    icon=ft.Icons.HELP_OUTLINE,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Aide",
                    on_click=self._show_help
                ),
            ]
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header avec statistiques
                    self._build_hero_header(),
                    
                    # Indicateur d'état de scan
                    self._build_scan_status(),
                    
                    # Cartes d'actions principales
                    self._build_action_grid(),
                    
                    # Section statistiques rapides
                    self._build_quick_stats(),
                    
                    # Guide rapide
                    self._build_quick_guide(),
                    
                    # Pied de page
                    self._build_footer()
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=0
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[ft.Colors.BLUE_50, ft.Colors.WHITE]
            ),
            padding=20,
            expand=True
        )

    def _build_hero_header(self):
        """Construit l'en-tête principal avec bienvenue"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.VERIFIED_USER,
                            size=40,
                            color=ft.Colors.BLUE_600
                        ),
                        padding=15,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=20,
                        shadow=ft.BoxShadow(
                            blur_radius=10,
                            color=ft.Colors.BLUE_100
                        )
                    ),
                    ft.Column([
                        ft.Text("Bienvenue", 
                               size=24, 
                               weight=ft.FontWeight.BOLD,
                               color=ft.Colors.BLUE_900),
                        ft.Text("Système de Vérification d'Identité",
                               size=16,
                               color=ft.Colors.BLUE_700,
                               weight=ft.FontWeight.W_600,
                               text_align=ft.TextAlign.CENTER)
                    ], spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True)
                ], alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
                
                ft.Container(height=15),
                
                ft.Text(
                    "Vérifiez votre identité en 3 étapes simples et sécurisées",
                    size=14,
                    color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.CENTER
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=30,
            margin=ft.margin.only(bottom=20)
        )

    def _build_scan_status(self):
        """Affiche l'état actuel des scans"""
        document_ready = hasattr(self.app, 'scanned_document_data') and self.app.scanned_document_data
        selfie_ready = hasattr(self.app, 'scanned_selfie_data') and self.app.scanned_selfie_data
        
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("PROGRESSION DE LA VÉRIFICATION", 
                               size=14, 
                               weight=ft.FontWeight.BOLD,
                               color=ft.Colors.GREY_700),
                        
                        ft.Container(height=15),
                        
                        ft.ResponsiveRow([
                            # Étape Document
                            ft.Container(
                                content=self._build_step_indicator(
                                    "📄 Document",
                                    "Scanner votre pièce d'identité",
                                    document_ready,
                                    1
                                ),
                                col={"sm": 6},
                                padding=5
                            ),
                            
                            # Étape Selfie
                            ft.Container(
                                content=self._build_step_indicator(
                                    "🤳 Selfie",
                                    "Prendre une photo de votre visage",
                                    selfie_ready,
                                    2
                                ),
                                col={"sm": 6},
                                padding=5
                            ),
                        ]),
                        
                        ft.Container(height=10),
                        
                        # Indicateur de complétion
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Complétion: ", size=12),
                                    ft.Text(f"{50 if document_ready else 0}{50 if selfie_ready else 0}%", 
                                           size=12, 
                                           weight=ft.FontWeight.BOLD,
                                           color=ft.Colors.BLUE_600)
                                ]),
                                ft.Container(
                                    content=ft.Container(
                                        bgcolor=ft.Colors.BLUE_500,
                                        width=f"{(50 if document_ready else 0) + (50 if selfie_ready else 0)}%",
                                        height=6,
                                        border_radius=3
                                    ),
                                    bgcolor=ft.Colors.GREY_300,
                                    height=6,
                                    border_radius=3
                                )
                            ]),
                            padding=10,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8
                        )
                    ]),
                    padding=20
                ),
                elevation=4,
                margin=5
            ),
            margin=ft.margin.only(bottom=20)
        )

    def _build_step_indicator(self, title, description, completed, step_number):
        """Construit un indicateur d'étape"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(str(step_number),
                                 color=ft.Colors.WHITE if completed else ft.Colors.BLUE_600,
                                 weight=ft.FontWeight.BOLD),
                    width=30,
                    height=30,
                    bgcolor=ft.Colors.BLUE_600 if completed else ft.Colors.BLUE_100,
                    border_radius=15,
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text(title, 
                           size=14, 
                           weight=ft.FontWeight.BOLD,
                           color=ft.Colors.BLUE_800 if completed else ft.Colors.GREY_700),
                    ft.Text(description, 
                           size=12, 
                           color=ft.Colors.GREY_600)
                ], spacing=2, expand=True)
            ], spacing=15),
            padding=15,
            bgcolor=ft.Colors.WHITE if completed else ft.Colors.GREY_50,
            border=ft.border.all(2, ft.Colors.BLUE_300 if completed else ft.Colors.GREY_300),
            border_radius=12
        )

    def _build_action_grid(self):
        """Construit la grille des actions principales"""
        return ft.Container(
            content=ft.ResponsiveRow([
                # Scanner Document
                ft.Container(
                    content=self._build_action_card(
                        "📄 Scanner Document",
                        "Numérisez votre CNI, passeport ou carte d'identité",
                        "scan_document",
                        ft.Colors.BLUE_500,
                        ft.Icons.BADGE
                    ),
                    col={"sm": 6},
                    padding=10
                ),
                
                # Prendre Selfie
                ft.Container(
                    content=self._build_action_card(
                        "🤳 Prendre Selfie",
                        "Capturez une photo de votre visage pour comparaison",
                        "take_selfie",
                        ft.Colors.GREEN_500,
                        ft.Icons.CAMERA_ALT
                    ),
                    col={"sm": 6},
                    padding=10
                ),
                
                # Vérifier Identité
                ft.Container(
                    content=self._build_action_card(
                        "✅ Vérifier Identité",
                        "Lancez l'analyse complète de vérification",
                        "verify_identity",
                        ft.Colors.ORANGE_500,
                        ft.Icons.VERIFIED,
                        is_primary=True
                    ),
                    col={"sm": 6},
                    padding=10
                ),
                
                # Historique
                ft.Container(
                    content=self._build_action_card(
                        "📊 Historique",
                        "Consultez vos vérifications précédentes",
                        "view_history",
                        ft.Colors.PURPLE_500,
                        ft.Icons.HISTORY
                    ),
                    col={"sm": 6},
                    padding=10
                ),
            ]),
            margin=ft.margin.only(bottom=20)
        )

    def _build_action_card(self, title, description, action, color, icon, is_primary=False):
        """Construit une carte d'action moderne"""
        document_ready = hasattr(self.app, 'scanned_document_data') and self.app.scanned_document_data
        selfie_ready = hasattr(self.app, 'scanned_selfie_data') and self.app.scanned_selfie_data
        
        # Vérifier si l'action est disponible
        if action == "verify_identity" and not (document_ready and selfie_ready):
            is_disabled = True
            disabled_reason = "Document et selfie requis"
        else:
            is_disabled = False
            disabled_reason = ""
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # En-tête avec icône
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=24),
                            padding=12,
                            bgcolor=color,
                            border_radius=12
                        ),
                        ft.Column([
                            ft.Text(title, 
                                   size=16, 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.Colors.GREY_800),
                            ft.Text(description, 
                                   size=12, 
                                   color=ft.Colors.GREY_600)
                        ], expand=True, spacing=2)
                    ], spacing=15),
                    
                    ft.Container(height=10),
                    
                    # Bouton d'action
                    ft.Container(
                        content=ft.FilledButton(
                            "Commencer →",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self._handle_action(action),
                            disabled=is_disabled,
                            style=ft.ButtonStyle(
                                bgcolor=color if not is_disabled else ft.Colors.GREY_400,
                                color=ft.Colors.WHITE,
                                padding=15,
                                elevation=8 if is_primary else 2
                            ),
                            expand=True
                        ),
                        padding=ft.padding.only(top=10)
                    ),
                    
                    # Message d'information si désactivé
                    ft.Container(
                        content=ft.Text(
                            disabled_reason,
                            size=10,
                            color=ft.Colors.ORANGE_600,
                            text_align=ft.TextAlign.CENTER
                        ),
                        visible=is_disabled,
                        padding=ft.padding.only(top=5)
                    )
                ]),
                padding=20,
                on_click=lambda e: self._handle_action(action) if not is_disabled else None,
                border=ft.border.all(2, color if not is_disabled else ft.Colors.GREY_300),
                border_radius=15
            ),
            elevation=8 if is_primary else 4,
            margin=5
        )

    def _build_quick_stats(self):
        """Construit la section des statistiques rapides"""
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.ANALYTICS, color=ft.Colors.BLUE_600),
                            ft.Text("STATISTIQUES RAPIDES", 
                                   size=14, 
                                   weight=ft.FontWeight.BOLD)
                        ]),
                        
                        ft.Container(height=15),
                        
                        ft.ResponsiveRow([
                            self._build_stat_card("Vérifications totales", 
                                                f"{self._stats['total_verifications']}", 
                                                ft.Icons.SECURITY),
                            self._build_stat_card("Taux de réussite", 
                                                f"{self._stats['success_rate']}%", 
                                                ft.Icons.TRENDING_UP),
                            self._build_stat_card("Dernière vérification", 
                                                "Aujourd'hui", 
                                                ft.Icons.SCHEDULE),
                        ])
                    ]),
                    padding=20
                )
            ),
            margin=ft.margin.only(bottom=20)
        )

    def _build_stat_card(self, title, value, icon):
        """Construit une carte de statistique"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=20, color=ft.Colors.BLUE_500),
                    ft.Text(value, 
                           size=18, 
                           weight=ft.FontWeight.BOLD,
                           color=ft.Colors.BLUE_700)
                ], spacing=10),
                ft.Text(title, 
                       size=12, 
                       color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            col={"sm": 4},
            margin=5
        )

    def _build_quick_guide(self):
        """Construit le guide rapide d'utilisation"""
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.MAP_OUTLINED, color=ft.Colors.BLUE_600),
                            ft.Text("GUIDE RAPIDE", 
                                   size=14, 
                                   weight=ft.FontWeight.BOLD)
                        ]),
                        
                        ft.Container(height=15),
                        
                        ft.Column([
                            self._build_guide_step(1, "Scanner votre document", "Assurez-vous que le document est bien visible et éclairé"),
                            self._build_guide_step(2, "Prendre un selfie", "Regardez droit devant la caméra dans un endroit bien éclairé"),
                            self._build_guide_step(3, "Lancer la vérification", "Le système compare automatiquement les informations"),
                        ], spacing=10)
                    ]),
                    padding=20
                )
            ),
            margin=ft.margin.only(bottom=20)
        )

    def _build_guide_step(self, number, title, description):
        """Construit une étape du guide"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(str(number),
                                 color=ft.Colors.WHITE,
                                 weight=ft.FontWeight.BOLD),
                    width=25,
                    height=25,
                    bgcolor=ft.Colors.BLUE_500,
                    border_radius=20,
                    alignment=ft.alignment.center
                ),
                ft.Column([
                    ft.Text(title, 
                           size=14, 
                           weight=ft.FontWeight.BOLD,
                           color=ft.Colors.GREY_800),
                    ft.Text(description, 
                           size=12, 
                           color=ft.Colors.GREY_600)
                ], spacing=2, expand=True)
            ], spacing=15),
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=8
        )

    def _build_footer(self):
        """Construit le pied de page"""
        return ft.Container(
            content=ft.Column([
                ft.Divider(),
                ft.Text("🔒 ANIP Bénin - Vérification d'Identité Sécurisée",
                       size=12,
                       color=ft.Colors.GREY_600,
                       text_align=ft.TextAlign.CENTER),
                ft.Text("Système certifié - Données cryptées",
                       size=10,
                       color=ft.Colors.GREY_500,
                       text_align=ft.TextAlign.CENTER),
                ft.Text(f"© 2024 ANIP Bénin • Version 1.0.0",
                       size=9,
                       color=ft.Colors.GREY_400,
                       text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20
        )

    def _handle_action(self, action: str):
        """Gère les actions des boutons"""
        if action == "scan_document":
            self.app.navigate_to("scan", scan_type="document")
        elif action == "take_selfie":
            self.app.navigate_to("scan", scan_type="selfie")
        elif action == "verify_identity":
            self._verify_identity()
        elif action == "view_history":
            self.app.navigate_to("history")

    def _verify_identity(self):
        """Lance la vérification d'identité"""
        document_data, selfie_data = self.app.get_scanned_data()
        
        if not document_data or not selfie_data:
            self._show_snackbar(
                "❌ Veuillez d'abord scanner un document et prendre un selfie",
                ft.Colors.RED
            )
            return
        
        # Afficher un overlay de chargement
        self._show_loading_overlay("🔍 Vérification en cours...")
        
        # Appel API en arrière-plan
        def verify_thread():
            try:
                result = self.api_client.verify_identity(document_data, selfie_data)
                # self.app.page.run_task(lambda: self._handle_verification_result(result))
                self._handle_verification_result(result)
            except Exception as e:
                # self.app.page.run_task(lambda: self._handle_verification_error(str(e)))
                self._handle_verification_error(str(e))
        
        import threading
        threading.Thread(target=verify_thread, daemon=True).start()

    def _handle_verification_result(self, result):
        """Gère le résultat de la vérification"""
        self._hide_loading_overlay()
        
        if result:
            self.app.navigate_to("result", result_data=result)
            self._stats['total_verifications'] += 1
            self._stats['last_verification'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            self._show_snackbar(
                "❌ Erreur lors de la vérification. Veuillez réessayer.",
                ft.Colors.RED
            )

    def _handle_verification_error(self, error_message):
        """Gère les erreurs de vérification"""
        self._hide_loading_overlay()
        self._show_snackbar(f"❌ Erreur: {error_message}", ft.Colors.RED)

    def _show_loading_overlay(self, message: str):
        """Affiche un overlay de chargement"""
        self.app.page.overlay.append(
            ft.Container(
                content=ft.Column([
                    ft.ProgressRing(width=50, height=50, stroke_width=6),
                    ft.Container(height=20),
                    ft.Text(message, size=16, color=ft.Colors.WHITE)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLACK54,
                expand=True
            )
        )
        self.app.page.update()

    def _hide_loading_overlay(self):
        """Cache l'overlay de chargement"""
        if self.app.page.overlay:
            self.app.page.overlay.pop()
        self.app.page.update()

    def _show_snackbar(self, message: str, color: ft.Colors = ft.Colors.BLUE_600):
        """Affiche un snackbar stylisé"""
        show_snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO, color=ft.Colors.WHITE),
                    ft.Text(message, color=ft.Colors.WHITE)
                ]),
                bgcolor=color,
                open=True
            )
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _show_notifications(self, e):
        """Affiche les notifications"""
        self._show_snackbar("🔔 Aucune nouvelle notification", ft.Colors.BLUE_600)

    def _show_help(self, e):
        """Affiche l'aide"""
        self.show_dialog = ft.AlertDialog(
                title=ft.Text("💡 Aide & Support"),
                content=ft.Text("Pour toute assistance, contactez le support ANIP au 1234."),
                actions=[ft.TextButton("Fermer", on_click=lambda e: self._close_dialog())]
            )
        self.app.page.open(self.show_dialog)
        self.show_dialog.open = True
        self.app.page.update()

    def _close_dialog(self):
        """Ferme le dialogue"""
        self.show_dialog.open = False
        self.app.page.update()