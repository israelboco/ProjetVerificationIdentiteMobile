import flet as ft
import base64
from datetime import datetime
import math

class ResultScreen:
    def __init__(self, app):
        self.app = app
        self._result_data = None
        self._confidence_score = 0
        self._verdict = None
        self.dialog = None

    def build(self):
        if not self.app.verification_result:
            return self._build_no_result_view()
        
        self._result_data = self.app.verification_result.get('data', {})
        self._confidence_score = self._result_data.get('confidence_score', 0)
        self._verdict = self._result_data.get('verdict', 'UNKNOWN')
        
        # Configuration de la barre d'application
        self.app.page.appbar = ft.AppBar(
            title=ft.Text("📊 Résultats de Vérification", 
                         weight=ft.FontWeight.BOLD,
                         size=22),
            bgcolor=ft.Colors.BLUE_700,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: self._return_to_home()
            ),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.SHARE,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Partager les résultats",
                    on_click=self._share_results
                ),
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    icon_color=ft.Colors.WHITE,
                    items=[
                        ft.PopupMenuItem(
                            text="Exporter PDF",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=self._export_pdf
                        ),
                        ft.PopupMenuItem(
                            text="Réimprimer",
                            icon=ft.Icons.PRINT,
                            on_click=self._reprint_result
                        ),
                    ]
                )
            ]
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # En-tête avec résultat principal
                    self._build_result_header(),
                    
                    # Jauge de confiance
                    self._build_confidence_gauge(),
                    
                    # Sections détaillées
                    self._build_detailed_sections(),
                    
                    # Actions principales
                    self._build_action_buttons(),
                    
                    # Pied de page
                    self._build_footer()
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=0
            ),
            padding=20,
            expand=True
        )

    def _build_no_result_view(self):
        """Vue quand aucun résultat n'est disponible"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.ORANGE),
                    ft.Text("Aucun résultat disponible", 
                           size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Veuillez effectuer une vérification d'identité d'abord",
                           size=16, color=ft.Colors.GREY_600,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=30),
                    ft.FilledButton(
                        "🔄 Nouvelle Vérification",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e: self._return_to_home(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            padding=20
                        )
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            padding=40,
            expand=True
        )

    def _build_result_header(self):
        """Construit l'en-tête du résultat"""
        is_verified = self._verdict == 'IDENTITY_CONFIRMED'
        icon_color = ft.Colors.GREEN if is_verified else ft.Colors.RED
        bg_color = ft.Colors.GREEN_50 if is_verified else ft.Colors.RED_50
        border_color = ft.Colors.GREEN_200 if is_verified else ft.Colors.RED_200
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.VERIFIED if is_verified else ft.Icons.WARNING,
                            size=40,
                            color=icon_color
                        ),
                        padding=15,
                        bgcolor=bg_color,
                        border_radius=50
                    ),
                    ft.Column([
                        ft.Text(
                            "✅ Identité Confirmée" if is_verified else "❌ Vérification Échouée",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=icon_color
                        ),
                        ft.Text(
                            f"Vérification effectuée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                            size=14,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=5)
                ], alignment=ft.MainAxisAlignment.CENTER),
                
                ft.Container(height=10),
                
                ft.Text(
                    "L'identité a été vérifiée avec succès" if is_verified 
                    else "La vérification d'identité a échoué",
                    size=16,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.GREY_700
                )
            ]),
            padding=25,
            bgcolor=bg_color,
            border=ft.border.all(2, border_color),
            border_radius=15,
            margin=ft.margin.only(bottom=20)
        )

    def _build_confidence_gauge(self):
        """Construit la jauge de confiance circulaire"""
        score_percent = self._confidence_score * 100
        color = self._get_score_color(score_percent)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("NIVEAU DE CONFIANCE", 
                       size=14, 
                       weight=ft.FontWeight.BOLD,
                       color=ft.Colors.GREY_600),
                
                ft.Stack([
                    # Cercle de fond
                    ft.Container(
                        width=120,
                        height=120,
                        border=ft.border.all(8, ft.Colors.GREY_200),
                        border_radius=60
                    ),
                    
                    # Cercle de progression
                    ft.Container(
                        width=120,
                        height=120,
                        gradient=ft.SweepGradient(
                            center=ft.alignment.center,
                            colors=[color, ft.Colors.GREY_200],
                            stops=[self._confidence_score, self._confidence_score + 0.01]
                        ),
                        border=ft.border.all(8, ft.Colors.TRANSPARENT),
                        border_radius=60
                    ),
                    
                    # Texte central
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"{score_percent:.0f}%", 
                                   size=24, 
                                   weight=ft.FontWeight.BOLD,
                                   color=color),
                            ft.Text("Score", 
                                   size=12, 
                                   color=ft.Colors.GREY_600)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        alignment=ft.alignment.center,
                        width=120,
                        height=120
                    )
                ]),
                
                ft.Container(height=10),
                
                ft.Text(
                    self._get_score_message(score_percent),
                    size=14,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.GREY_700
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            alignment=ft.alignment.center
        )

    def _build_detailed_sections(self):
        """Construit les sections détaillées des résultats"""
        return ft.Column([
            self._build_ocr_section(),
            self._build_face_recognition_section(),
            self._build_age_estimation_section(),
            self._build_technical_details_section()
        ], spacing=15)

    def _build_ocr_section(self):
        """Section OCR améliorée"""
        ocr_data = self._result_data.get('ocr_extraction', {})
        structured_data = ocr_data.get('structured_data', {})
        document_type = ocr_data.get('document_type', 'Non détecté')
        
        # Créer des cartes pour chaque champ important
        field_cards = []
        important_fields = ['nom', 'prenoms', 'npi', 'date_naissance', 'lieu_naissance']
        
        for field in important_fields:
            value = structured_data.get(field)
            if value:
                field_cards.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(field.upper(), 
                                   size=12, 
                                   color=ft.Colors.GREY_600,
                                   weight=ft.FontWeight.BOLD),
                            ft.Text(value, 
                                   size=14, 
                                   weight=ft.FontWeight.W500)
                        ]),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=10,
                        expand=True
                    )
                )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.DOCUMENT_SCANNER, color=ft.Colors.BLUE_600),
                        ft.Text("📄 INFORMATIONS DU DOCUMENT", 
                               size=16, 
                               weight=ft.FontWeight.BOLD)
                    ]),
                    
                    ft.Container(height=10),
                    
                    # Type de document
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Type de document:", 
                                   size=14, 
                                   color=ft.Colors.GREY_600),
                            ft.Text(document_type, 
                                   size=14, 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.Colors.BLUE_600)
                        ]),
                        padding=ft.padding.symmetric(vertical=5)
                    ),
                    
                    # Champs importants
                    ft.ResponsiveRow(
                        controls=field_cards,
                        spacing=10
                    ),
                    
                    # Bouton voir plus
                    ft.TextButton(
                        "Voir tous les détails OCR",
                        icon=ft.Icons.EXPAND_MORE,
                        on_click=self._show_full_ocr_details
                    )
                ]),
                padding=20
            ),
            elevation=3,
            margin=5
        )

    def _build_face_recognition_section(self):
        """Section reconnaissance faciale améliorée"""
        face_data = self._result_data.get('face_verification', {})
        is_verified = face_data.get('verified', False)
        distance = face_data.get('distance', 0)
        threshold = face_data.get('threshold', 0.4)
        
        # Calcul du pourcentage de similarité
        similarity_percent = max(0, min(100, (1 - (distance / threshold)) * 100)) if threshold > 0 else 0
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.FACE, 
                               color=ft.Colors.GREEN if is_verified else ft.Colors.RED),
                        ft.Text("👤 RECONNAISSANCE FACIALE", 
                               size=16, 
                               weight=ft.FontWeight.BOLD)
                    ]),
                    
                    ft.Container(height=15),
                    
                    # Barre de similarité
                    ft.Column([
                        ft.Row([
                            ft.Text("Similarité faciale:", size=14),
                            ft.Text(f"{similarity_percent:.1f}%", 
                                   size=14, 
                                   weight=ft.FontWeight.BOLD,
                                   color=self._get_score_color(similarity_percent))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        
                        ft.Container(
                            content=ft.Container(
                                bgcolor=self._get_score_color(similarity_percent),
                                border_radius=10,
                                height=8
                            ),
                            bgcolor=ft.Colors.GREY_200,
                            border_radius=10,
                            height=8,
                            width=300
                        ),
                        
                        ft.Row([
                            ft.Text("0%", size=12, color=ft.Colors.GREY_500),
                            ft.Text("Seuil", size=12, color=ft.Colors.GREY_500),
                            ft.Text("100%", size=12, color=ft.Colors.GREY_500)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]),
                    
                    ft.Container(height=10),
                    
                    # Détails techniques
                    ft.ResponsiveRow([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("DISTANCE", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{distance:.3f}", size=14, weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            col={"sm": 6}
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("SEUIL", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{threshold:.3f}", size=14, weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            col={"sm": 6}
                        )
                    ], spacing=10)
                ]),
                padding=20
            ),
            elevation=3,
            margin=5
        )

    def _build_age_estimation_section(self):
        """Section estimation d'âge améliorée"""
        age_data = self._result_data.get('age_estimation', {})
        estimated_age = age_data.get('estimated_age', 0)
        confidence = age_data.get('confidence', 0) * 100
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CAKE, color=ft.Colors.ORANGE),
                        ft.Text("📅 ESTIMATION D'ÂGE", 
                               size=16, 
                               weight=ft.FontWeight.BOLD)
                    ]),
                    
                    ft.Container(height=15),
                    
                    ft.ResponsiveRow([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("ÂGE ESTIMÉ", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{estimated_age} ans", 
                                       size=20, 
                                       weight=ft.FontWeight.BOLD,
                                       color=ft.Colors.ORANGE_600)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            bgcolor=ft.Colors.ORANGE_50,
                            border_radius=10,
                            col={"sm": 6}
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("CONFIANCE", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"{confidence:.1f}%", 
                                       size=20, 
                                       weight=ft.FontWeight.BOLD,
                                       color=ft.Colors.GREEN_600)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=15,
                            bgcolor=ft.Colors.GREEN_50,
                            border_radius=10,
                            col={"sm": 6}
                        )
                    ], spacing=10),
                    
                    ft.Container(height=10),
                    
                    ft.Text(
                        self._get_age_interpretation(estimated_age),
                        size=14,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY_700
                    )
                ]),
                padding=20
            ),
            elevation=3,
            margin=5
        )

    def _build_technical_details_section(self):
        """Section détails techniques"""
        return ft.ExpansionTile(
            title=ft.Text("🔧 Détails Techniques", 
                         weight=ft.FontWeight.BOLD),
            subtitle=ft.Text("Informations techniques avancées"),
            controls=[
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Paramètre", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Valeur", weight=ft.FontWeight.BOLD))
                    ],
                    rows=[
                        self._create_tech_row("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        self._create_tech_row("Version API", "1.0.0"),
                        self._create_tech_row("Modèle Face", self._result_data.get('face_verification', {}).get('model', 'N/A')),
                        self._create_tech_row("Backend Face", self._result_data.get('face_verification', {}).get('backend', 'N/A')),
                        self._create_tech_row("Modèle Âge", self._result_data.get('age_estimation', {}).get('model', 'N/A')),
                    ]
                )
            ]
        )

    def _build_action_buttons(self):
        """Boutons d'action améliorés"""
        return ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    content=ft.FilledButton(
                        "🔄 Nouvelle Vérification",
                        icon=ft.Icons.REFRESH,
                        on_click=self._return_to_home,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            padding=20
                        ),
                        expand=True
                    ),
                    col={"sm": 6},
                    padding=5
                ),
                ft.Container(
                    content=ft.FilledTonalButton(
                        "💾 Sauvegarder",
                        icon=ft.Icons.SAVE,
                        on_click=self._save_result,
                        style=ft.ButtonStyle(
                            padding=20
                        ),
                        expand=True
                    ),
                    col={"sm": 6},
                    padding=5
                ),
                ft.Container(
                    content=ft.OutlinedButton(
                        "📊 Voir l'Historique",
                        icon=ft.Icons.HISTORY,
                        on_click=self._view_history,
                        expand=True
                    ),
                    col={"sm": 12},
                    padding=5,
                    margin=ft.margin.only(top=10)
                )
            ]),
            padding=20,
            margin=ft.margin.only(top=20)
        )

    def _build_footer(self):
        """Pied de page"""
        return ft.Container(
            content=ft.Column([
                ft.Divider(),
                ft.Text("ANIP Bénin - Système de Vérification d'Identité",
                       size=12,
                       color=ft.Colors.GREY_500,
                       text_align=ft.TextAlign.CENTER),
                ft.Text("Résultat généré automatiquement",
                       size=10,
                       color=ft.Colors.GREY_400,
                       text_align=ft.TextAlign.CENTER)
            ]),
            padding=20
        )

    # Méthodes utilitaires
    def _get_score_color(self, score):
        """Retourne la couleur en fonction du score"""
        if score >= 80:
            return ft.Colors.GREEN_600
        elif score >= 60:
            return ft.Colors.ORANGE_600
        else:
            return ft.Colors.RED_600

    def _get_score_message(self, score):
        """Retourne un message en fonction du score"""
        if score >= 90:
            return "Excellente confiance"
        elif score >= 75:
            return "Bonne confiance"
        elif score >= 60:
            return "Confiance modérée"
        else:
            return "Confiance faible"

    def _get_age_interpretation(self, age):
        """Interprétation de l'âge estimé"""
        if age < 18:
            return "Âge mineur détecté"
        elif 18 <= age <= 25:
            return "Jeune adulte"
        elif 26 <= age <= 60:
            return "Adulte"
        else:
            return "Personne âgée"

    def _create_tech_row(self, param, value):
        """Crée une ligne pour le tableau technique"""
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(param)),
            ft.DataCell(ft.Text(value, color=ft.Colors.BLUE_600))
        ])

    # Gestion des événements
    def _return_to_home(self, e=None):
        """Retour à l'accueil"""
        self.app.scanned_document_data = None
        self.app.scanned_selfie_data = None
        self.app.verification_result = None
        self.app.navigate_to("home")

    def _save_result(self, e):
        """Sauvegarde le résultat"""
        result_entry = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'success': self._verdict == 'IDENTITY_CONFIRMED',
            'score': self._confidence_score,
            'document_type': self._result_data.get('ocr_extraction', {}).get('document_type', 'Inconnu')
        }
        
        # Ajouter à l'historique
        if not hasattr(self.app.history_screen, 'history_data'):
            self.app.history_screen.history_data = []
        self.app.history_screen.history_data.append(result_entry)
        
        # Nettoyer les données temporaires
        self.app.scanned_document_data = None
        self.app.scanned_selfie_data = None
        
        # Notification
        show_snack_bar = ft.SnackBar(
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                    ft.Text("Résultat sauvegardé dans l'historique")
                ]),
                open=True
            )
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _share_results(self, e):
        """Partage les résultats"""
        show_snack_bar = ft.SnackBar(ft.Text("Fonctionnalité de partage à implémenter"), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _export_pdf(self, e):
        """Exporte en PDF"""
        show_snack_bar = ft.SnackBar(ft.Text("Export PDF à implémenter"), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _reprint_result(self, e):
        """Réimprime le résultat"""
        show_snack_bar = ft.SnackBar(ft.Text("Réimpression à implémenter"), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _view_history(self, e):
        """Voir l'historique"""
        self.app.navigate_to("history")

    def _show_full_ocr_details(self, e):
        """Affiche tous les détails OCR"""
        ocr_data = self._result_data.get('ocr_extraction', {})
        structured_data = ocr_data.get('structured_data', {})
        
        # Créer un dialogue avec tous les détails
        content = ft.Column([
            ft.Text("Détails complets OCR", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            *[ft.Row([
                ft.Text(f"{key}:", weight=ft.FontWeight.BOLD, width=150),
                ft.Text(str(value) if value else "Non détecté")
            ]) for key, value in structured_data.items()]
        ], scroll=ft.ScrollMode.AUTO)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text("Détails OCR Complets"),
            content=content,
            actions=[ft.TextButton("Fermer", on_click=lambda e: self._close_dialog())]
        )
        self.app.page.open(self.dialog)
        self.app.page.dialog.open = True
        self.app.page.update()

    def _close_dialog(self):
        """Ferme le dialogue"""
        self.dialog.open = False
        self.app.page.update()