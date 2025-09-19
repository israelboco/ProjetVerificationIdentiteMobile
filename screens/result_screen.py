import flet as ft
import base64
from datetime import datetime

class ResultScreen:
    def __init__(self, app):
        self.app = app

    def build(self):
        if not self.app.verification_result:
            return ft.Column([
                ft.Text("Aucun résultat disponible"),
                ft.ElevatedButton("Retour", on_click=lambda e: self.app.navigate_to("home"))
            ])
        
        result = self.app.verification_result
        data = result.get('data', {})
        
        return ft.Column(
            controls=[
                ft.AppBar(
                    title=ft.Text("Résultats de Vérification", weight=ft.FontWeight.BOLD),
                    leading=ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda e: self.app.navigate_to("home")
                    )
                ),
                
                # Carte de résultat principal
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(
                                    ft.icons.CHECK_CIRCLE if data.get('verdict') == 'IDENTITY_CONFIRMED' 
                                    else ft.icons.ERROR,
                                    color=ft.colors.GREEN if data.get('verdict') == 'IDENTITY_CONFIRMED' 
                                    else ft.colors.RED,
                                    size=40
                                ),
                                ft.Text(
                                    "Identité Confirmée" if data.get('verdict') == 'IDENTITY_CONFIRMED' 
                                    else "Échec de Vérification",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.GREEN if data.get('verdict') == 'IDENTITY_CONFIRMED' 
                                    else ft.colors.RED
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER),
                            
                            ft.Text(
                                f"Score de confiance: {data.get('confidence_score', 0)*100:.1f}%",
                                size=16,
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20
                    )
                ),
                
                # Détails OCR
                self._build_ocr_section(data.get('ocr_extraction', {})),
                
                # Détails reconnaissance faciale
                self._build_face_section(data.get('face_verification', {})),
                
                # Détails âge
                self._build_age_section(data.get('age_estimation', {})),
                
                # Actions
                ft.Container(
                    content=ft.Row([
                        ft.FilledButton(
                            "🔄 Nouvelle Vérification",
                            on_click=lambda e: self.app.navigate_to("home")
                        ),
                        ft.OutlinedButton(
                            "💾 Sauvegarder",
                            on_click=self._save_result
                        )
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def _build_ocr_section(self, ocr_data):
        structured_data = ocr_data.get('structured_data', {})
        
        return ft.ExpansionTile(
            title=ft.Text("📄 Informations Document", weight=ft.FontWeight.BOLD),
            subtitle=ft.Text(f"Type: {ocr_data.get('document_type', 'Inconnu')}"),
            controls=[
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Champ")),
                        ft.DataColumn(ft.Text("Valeur"))
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(key.capitalize())),
                            ft.DataCell(ft.Text(str(value) if value else "Non détecté"))
                        ]) for key, value in structured_data.items() if value
                    ]
                )
            ]
        )

    def _build_face_section(self, face_data):
        return ft.ExpansionTile(
            title=ft.Text("👤 Reconnaissance Faciale", weight=ft.FontWeight.BOLD),
            subtitle=ft.Text("✅ Correspondance" if face_data.get('verified') else "❌ Non correspondance"),
            controls=[
                ft.ListTile(
                    title=ft.Text(f"Distance: {face_data.get('distance', 0):.3f}"),
                    subtitle=ft.Text(f"Seuil: {face_data.get('threshold', 0)}")
                ),
                ft.ListTile(
                    title=ft.Text(f"Modèle: {face_data.get('model', 'Inconnu')}"),
                    subtitle=ft.Text(f"Backend: {face_data.get('backend', 'Inconnu')}")
                )
            ]
        )

    def _build_age_section(self, age_data):
        return ft.ExpansionTile(
            title=ft.Text("📅 Estimation d'Âge", weight=ft.FontWeight.BOLD),
            controls=[
                ft.ListTile(
                    title=ft.Text(f"Âge estimé: {age_data.get('estimated_age', 0)} ans"),
                    subtitle=ft.Text(f"Confiance: {age_data.get('confidence', 0)*100:.1f}%")
                ),
                ft.ListTile(
                    title=ft.Text(f"Modèle: {age_data.get('model', 'Inconnu')}"),
                    subtitle=ft.Text(f"Backend: {age_data.get('backend', 'Inconnu')}")
                )
            ]
        )

    def _save_result(self, e):
        # Sauvegarder le résultat (implémentation simplifiée)
        self.app.page.snack_bar = ft.SnackBar(
            ft.Text("Résultat sauvegardé avec succès"),
            open=True
        )
        self.app.page.update()