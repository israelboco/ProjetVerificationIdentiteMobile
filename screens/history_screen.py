import flet as ft
from datetime import datetime

class HistoryScreen:
    def __init__(self, app):
        self.app = app
        self.history_data = []  # En production, charger depuis une base de données

    def build(self):
        return ft.Column(
            controls=[
                ft.AppBar(
                    title=ft.Text("Historique des Vérifications", weight=ft.FontWeight.BOLD),
                    leading=ft.IconButton(
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda e: self.app.navigate_to("home")
                    )
                ),
                
                ft.Container(
                    content=ft.Text(
                        "Aucune vérification enregistrée" if not self.history_data 
                        else f"{len(self.history_data)} vérification(s) trouvée(s)",
                        text_align=ft.TextAlign.CENTER
                    ),
                    padding=20
                ),
                
                # Liste des vérifications
                *self._build_history_list(),
                
                # Actions
                ft.Container(
                    content=ft.Row([
                        ft.FilledButton(
                            "🗑️ Effacer l'historique",
                            on_click=self._clear_history,
                            disabled=not self.history_data
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                )
            ]
        )

    def _build_history_list(self):
        if not self.history_data:
            return []
        
        return [
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(
                                ft.icons.CHECK_CIRCLE if item['success'] else ft.icons.ERROR,
                                color=ft.colors.GREEN if item['success'] else ft.colors.RED
                            ),
                            title=ft.Text(
                                "Vérification réussie" if item['success'] else "Échec de vérification",
                                weight=ft.FontWeight.BOLD
                            ),
                            subtitle=ft.Text(
                                f"{item['date']} - Score: {item['score']*100:.1f}%"
                            ),
                        ),
                        ft.Row([
                            ft.TextButton(
                                "Détails",
                                on_click=lambda e, item=item: self._show_details(item)
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ]),
                    padding=10
                )
            ) for item in self.history_data
        ]

    def _clear_history(self, e):
        self.history_data = []
        self.app.page.snack_bar = ft.SnackBar(
            ft.Text("Historique effacé"),
            open=True
        )
        self.app.page.update()

    def _show_details(self, item):
        # Afficher les détails d'une vérification
        self.app.page.dialog = ft.AlertDialog(
            title=ft.Text("Détails de la vérification"),
            content=ft.Text(f"Date: {item['date']}\nScore: {item['score']*100:.1f}%"),
            actions=[ft.TextButton("Fermer", on_click=lambda e: self._close_dialog())]
        )
        self.app.page.dialog.open = True
        self.app.page.update()

    def _close_dialog(self):
        self.app.page.dialog.open = False
        self.app.page.update()