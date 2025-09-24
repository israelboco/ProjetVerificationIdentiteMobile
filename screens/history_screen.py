import flet as ft
from datetime import datetime
import json

class HistoryScreen:
    def __init__(self, app):
        self.app = app
        self.history_data = self._load_history_data()  # Charger depuis le stockage
        self._filtered_data = self.history_data.copy()
        self._current_filter = "all"
        self._sort_order = "newest"
        self.dialog = None
        self._search_query = ""

    def build(self):
        # Configuration de la barre d'application moderne
        self.app.page.appbar = ft.AppBar(
            title=ft.Row([
                ft.Icon(ft.Icons.HISTORY, color=ft.Colors.WHITE, size=28),
                ft.Text("Historique des Vérifications", 
                       size=20, 
                       weight=ft.FontWeight.BOLD),
            ]),
            bgcolor=ft.Colors.BLUE_700,
            center_title=False,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.SEARCH,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Rechercher",
                    on_click=self._show_search_dialog
                ),
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    icon_color=ft.Colors.WHITE,
                    items=[
                        ft.PopupMenuItem(
                            text="Exporter l'historique",
                            icon=ft.Icons.DATA_EXPLORATION,
                            on_click=self._export_history
                        ),
                        ft.PopupMenuItem(),  # Séparateur
                        ft.PopupMenuItem(
                            text="Statistiques",
                            icon=ft.Icons.ANALYTICS,
                            on_click=self._show_stats
                        ),
                    ]
                )
            ]
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # En-tête avec statistiques
                    self._build_header_stats(),
                    
                    # Barre de filtres et tri
                    self._build_filter_bar(),
                    
                    # Liste des vérifications ou message vide
                    self._build_history_content(),
                    
                    # Pied de page
                    self._build_footer()
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=0
            ),
            padding=20,
            expand=True
        )

    def _build_header_stats(self):
        """Construit l'en-tête avec les statistiques"""
        total = len(self.history_data)
        successful = len([h for h in self.history_data if h.get('success', False)])
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.ANALYTICS, color=ft.Colors.BLUE_600, size=28),
                            ft.Text("RÉSUMÉ DE L'HISTORIQUE", 
                                   size=16, 
                                   weight=ft.FontWeight.BOLD)
                        ]),
                        
                        ft.Container(height=15),
                        
                        ft.ResponsiveRow([
                            # Total des vérifications
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"{total}", 
                                           size=24, 
                                           weight=ft.FontWeight.BOLD,
                                           color=ft.Colors.BLUE_700),
                                    ft.Text("Vérifications totales", 
                                           size=12, 
                                           color=ft.Colors.GREY_600)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                col={"sm": 4},
                                padding=10
                            ),
                            
                            # Vérifications réussies
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"{successful}", 
                                           size=24, 
                                           weight=ft.FontWeight.BOLD,
                                           color=ft.Colors.GREEN_600),
                                    ft.Text("Réussies", 
                                           size=12, 
                                           color=ft.Colors.GREY_600)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                col={"sm": 4},
                                padding=10
                            ),
                            
                            # Taux de réussite
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"{success_rate:.1f}%", 
                                           size=24, 
                                           weight=ft.FontWeight.BOLD,
                                           color=ft.Colors.ORANGE_600),
                                    ft.Text("Taux de réussite", 
                                           size=12, 
                                           color=ft.Colors.GREY_600)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                col={"sm": 4},
                                padding=10
                            ),
                        ])
                    ]),
                    padding=20
                ),
                elevation=4
            ),
            margin=ft.margin.only(bottom=20)
        )

    def _build_filter_bar(self):
        """Construit la barre de filtres et tri"""
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.ResponsiveRow([
                        # Filtre par statut
                        ft.Container(
                            content=ft.Dropdown(
                                label="Filtrer par statut",
                                options=[
                                    ft.dropdown.Option("all", "Toutes"),
                                    ft.dropdown.Option("success", "✅ Réussies"),
                                    ft.dropdown.Option("failed", "❌ Échecs"),
                                ],
                                value=self._current_filter,
                                on_change=self._apply_filter,
                                width=150
                            ),
                            col={"sm": 6},
                            padding=5
                        ),
                        
                        # Tri
                        ft.Container(
                            content=ft.Dropdown(
                                label="Trier par",
                                options=[
                                    ft.dropdown.Option("newest", "Plus récent"),
                                    ft.dropdown.Option("oldest", "Plus ancien"),
                                    ft.dropdown.Option("score", "Score décroissant"),
                                ],
                                value=self._sort_order,
                                on_change=self._apply_sort,
                                width=150
                            ),
                            col={"sm": 6},
                            padding=5
                        ),
                    ]),
                    padding=15
                ),
                elevation=2
            ),
            margin=ft.margin.only(bottom=15)
        )

    def _build_history_content(self):
        """Construit le contenu principal de l'historique"""
        if not self._filtered_data:
            return self._build_empty_state()
        
        return ft.Column(
            controls=[
                ft.Text(
                    f"{len(self._filtered_data)} vérification(s) trouvée(s)",
                    size=14,
                    color=ft.Colors.GREY_600,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(height=10),
                *self._build_history_cards()
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True
        )

    def _build_empty_state(self):
        """Construit l'état vide de l'historique"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF, size=80, color=ft.Colors.GREY_300),
                ft.Text("Aucune vérification enregistrée", 
                       size=20, 
                       weight=ft.FontWeight.BOLD,
                       color=ft.Colors.GREY_500),
                ft.Text("Les vérifications que vous effectuerez apparaîtront ici.",
                       size=14,
                       color=ft.Colors.GREY_400,
                       text_align=ft.TextAlign.CENTER),
                ft.Container(height=20),
                ft.FilledButton(
                    "🔍 Effectuer une vérification",
                    icon=ft.Icons.SEARCH,
                    on_click=lambda e: self.app.navigate_to("home"),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_600,
                        padding=15
                    )
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
            alignment=ft.alignment.center
        )

    def _build_history_cards(self):
        """Construit les cartes d'historique"""
        cards = []
        for item in self._filtered_data:
            cards.append(self._build_history_card(item))
            cards.append(ft.Container(height=10))  # Espacement entre les cartes
        
        return cards

    def _build_history_card(self, item):
        """Construit une carte d'historique individuelle"""
        is_success = item.get('success', False)
        score = item.get('score', 0) * 100
        date = self._format_date(item.get('date', ''))
        document_type = item.get('document_type', 'Document inconnu')
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # En-tête de la carte
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.CHECK_CIRCLE if is_success else ft.Icons.ERROR,
                                color=ft.Colors.GREEN if is_success else ft.Colors.RED,
                                size=24
                            ),
                            padding=8,
                            bgcolor=ft.Colors.GREEN_50 if is_success else ft.Colors.RED_50,
                            border_radius=8
                        ),
                        ft.Column([
                            ft.Text(
                                "✅ Vérification réussie" if is_success else "❌ Vérification échouée",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700 if is_success else ft.Colors.RED_700
                            ),
                            ft.Text(document_type, 
                                   size=12, 
                                   color=ft.Colors.GREY_600)
                        ], expand=True, spacing=2),
                        ft.Container(
                            content=ft.Text(f"{score:.1f}%",
                                          size=14,
                                          weight=ft.FontWeight.BOLD,
                                          color=self._get_score_color(score)),
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=8
                        )
                    ], alignment=ft.MainAxisAlignment.START),
                    
                    ft.Container(height=10),
                    
                    # Détails de la vérification
                    ft.ResponsiveRow([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("DATE", size=10, color=ft.Colors.GREY_500),
                                ft.Text(date, size=12, weight=ft.FontWeight.W_500)
                            ]),
                            col={"sm": 6},
                            padding=5
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("DURÉE", size=10, color=ft.Colors.GREY_500),
                                ft.Text(item.get('duration', 'N/A'), size=12, weight=ft.FontWeight.W_500)
                            ]),
                            col={"sm": 6},
                            padding=5
                        )
                    ]),
                    
                    ft.Container(height=10),
                    
                    # Actions
                    ft.Row([
                        ft.FilledTonalButton(
                            "📋 Détails",
                            icon=ft.Icons.VISIBILITY,
                            on_click=lambda e, item=item: self._show_details(item),
                            style=ft.ButtonStyle(padding=10)
                        ),
                        ft.OutlinedButton(
                            "🔄 Refaire",
                            icon=ft.Icons.REPLAY,
                            on_click=lambda e, item=item: self._replay_verification(item),
                            style=ft.ButtonStyle(padding=10)
                        ),
                        ft.Container(expand=True),  # Espaceur
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.GREY_500,
                            tooltip="Supprimer",
                            on_click=lambda e, item=item: self._delete_item(item)
                        )
                    ])
                ]),
                padding=15
            ),
            elevation=3,
            margin=ft.margin.symmetric(horizontal=5)
        )

    def _build_footer(self):
        """Construit le pied de page avec les actions globales"""
        if not self.history_data:
            return ft.Container()
        
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.ResponsiveRow([
                        ft.Container(
                            content=ft.FilledButton(
                                "🗑️ Tout effacer",
                                icon=ft.Icons.DELETE_FOREVER,
                                on_click=self._show_clear_confirmation,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_600,
                                    padding=15
                                ),
                                expand=True
                            ),
                            col={"sm": 6},
                            padding=5
                        ),
                        ft.Container(
                            content=ft.FilledTonalButton(
                                "📊 Rapport complet",
                                icon=ft.Icons.SUMMARIZE,
                                on_click=self._generate_report,
                                expand=True
                            ),
                            col={"sm": 6},
                            padding=5
                        ),
                    ]),
                    padding=15
                )
            ),
            margin=ft.margin.only(top=20)
        )

    def _apply_filter(self, e):
        """Applique le filtre sélectionné"""
        self._current_filter = e.control.value
        self._filtered_data = self._filter_history()
        self._apply_current_sort()
        self.app.page.update()

    def _apply_sort(self, e):
        """Applique le tri sélectionné"""
        self._sort_order = e.control.value
        self._apply_current_sort()
        self.app.page.update()

    def _filter_history(self):
        """Filtre l'historique selon le critère sélectionné"""
        if self._current_filter == "all":
            return self.history_data.copy()
        elif self._current_filter == "success":
            return [h for h in self.history_data if h.get('success', False)]
        else:  # failed
            return [h for h in self.history_data if not h.get('success', False)]

    def _apply_current_sort(self):
        """Applique le tri actuel aux données filtrées"""
        if self._sort_order == "newest":
            self._filtered_data.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        elif self._sort_order == "oldest":
            self._filtered_data.sort(key=lambda x: x.get('timestamp', 0))
        elif self._sort_order == "score":
            self._filtered_data.sort(key=lambda x: x.get('score', 0), reverse=True)

    def _format_date(self, date_str):
        """Formate la date pour l'affichage"""
        try:
            if 'T' in date_str:  # Format ISO
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%d/%m/%Y à %H:%M')
        except:
            return date_str

    def _get_score_color(self, score):
        """Retourne la couleur en fonction du score"""
        if score >= 80:
            return ft.Colors.GREEN_600
        elif score >= 60:
            return ft.Colors.ORANGE_600
        else:
            return ft.Colors.RED_600

    def _show_details(self, item):
        """Affiche les détails d'une vérification"""
        details_content = self._build_details_content(item)
        
        self.dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_600),
                ft.Text("Détails de la vérification", weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=details_content,
                width=400,
                height=300
            ),
            actions=[
                ft.TextButton("Fermer", on_click=self._close_dialog),
                ft.TextButton("Exporter", on_click=lambda e: self._export_single(item))
            ]
        )
        self.app.page.dialog = self.dialog
        self.dialog.open = True
        self.app.page.update()

    def _build_details_content(self, item):
        """Construit le contenu détaillé d'une vérification"""
        return ft.Column(
            controls=[
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Champ", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Valeur", weight=ft.FontWeight.BOLD))
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Statut")),
                            ft.DataCell(ft.Text(
                                "✅ Réussie" if item.get('success') else "❌ Échouée",
                                color=ft.Colors.GREEN if item.get('success') else ft.Colors.RED
                            ))
                        ]),
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Score")),
                            ft.DataCell(ft.Text(f"{item.get('score', 0)*100:.1f}%"))
                        ]),
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Date")),
                            ft.DataCell(ft.Text(item.get('date', 'N/A')))
                        ]),
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Type de document")),
                            ft.DataCell(ft.Text(item.get('document_type', 'Inconnu')))
                        ]),
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Durée")),
                            ft.DataCell(ft.Text(item.get('duration', 'N/A')))
                        ]),
                    ]
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )

    def _replay_verification(self, item):
        """Relance une vérification à partir de l'historique"""
        show_snack_bar = ft.SnackBar(
                ft.Text("🔍 Préparation de la re-vérification..."),
                open=True
            )
        self.app.page.open(show_snack_bar)
        self.app.page.update()
        # Navigation vers l'écran de scan avec pré-remplissage si possible
        self.app.navigate_to("home")

    def _delete_item(self, item):
        """Supprime un élément de l'historique"""
        def confirm_delete(e):
            self.history_data.remove(item)
            self._filtered_data.remove(item)
            self._save_history_data()
            self.dialog.open = False
            self.app.page.update()
            show_snack_bar = ft.SnackBar(ft.Text("✅ Élément supprimé"), open=True)
            self.app.page.open(show_snack_bar)
            self.app.page.update()

        self.dialog = ft.AlertDialog(
            title=ft.Text("Confirmation de suppression"),
            content=ft.Text("Êtes-vous sûr de vouloir supprimer cette vérification ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(self.dialog, 'open', False)),
                ft.TextButton("Supprimer", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED))
            ]
        )
        self.app.page.open(self.dialog)
        self.dialog.open = True
        self.app.page.update()

    def _show_clear_confirmation(self, e):
        """Affiche la confirmation pour effacer tout l'historique"""
        def confirm_clear(e):
            self.history_data.clear()
            self._filtered_data.clear()
            self._save_history_data()
            self.dialog.open = False
            self.app.page.update()
            show_snack_bar = ft.SnackBar(ft.Text("🗑️ Historique effacé"), open=True)
            self.app.page.open(show_snack_bar)
            self.app.page.update()

        self.dialog = ft.AlertDialog(
            title=ft.Text("Confirmation"),
            content=ft.Text("Êtes-vous sûr de vouloir effacer tout l'historique ? Cette action est irréversible."),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(self.app.page.dialog, 'open', False)),
                ft.TextButton("Tout effacer", on_click=confirm_clear, style=ft.ButtonStyle(color=ft.Colors.RED))
            ]
        )
        self.dialog.open = True
        self.app.page.open(self.dialog)
        self.app.page.update()

    def _generate_report(self, e):
        """Génère un rapport complet"""
        show_snack_bar = ft.SnackBar(ft.Text("📊 Génération du rapport en cours..."), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _export_history(self, e):
        """Exporte l'historique"""
        show_snack_bar = ft.SnackBar(ft.Text("📤 Export de l'historique..."), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _export_single(self, item):
        """Exporte un élément individuel"""
        show_snack_bar = ft.SnackBar(ft.Text("📤 Export de l'élément..."), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()
        self._close_dialog()

    def _show_stats(self, e):
        """Affiche les statistiques détaillées"""
        show_snack_bar = ft.SnackBar(ft.Text("📈 Ouverture des statistiques..."), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _show_search_dialog(self, e):
        """Affiche la boîte de dialogue de recherche"""
        show_snack_bar = ft.SnackBar(ft.Text("🔍 Fonction de recherche à implémenter"), open=True)
        self.app.page.open(show_snack_bar)
        self.app.page.update()

    def _close_dialog(self):
        """Ferme le dialogue actuel"""
        if self.dialog:
            self.dialog.open = False
            self.app.page.update()

    def _load_history_data(self):
        """Charge les données d'historique depuis le stockage"""
        # En production, charger depuis une base de données
        # Pour l'exemple, on retourne des données de démo
        return [
            {
                'success': True,
                'score': 0.92,
                'date': '2024-01-15 14:30:00',
                'timestamp': 1705325400,
                'document_type': 'CNI Biométrique',
                'duration': '2.3s'
            },
            {
                'success': False,
                'score': 0.45,
                'date': '2024-01-14 10:15:00',
                'timestamp': 1705234500,
                'document_type': 'Passeport',
                'duration': '1.8s'
            }
        ]

    def _save_history_data(self):
        """Sauvegarde les données d'historique"""
        # En production, sauvegarder dans une base de données
        pass

    def add_verification_result(self, result_data):
        """Ajoute un nouveau résultat à l'historique"""
        new_entry = {
            'success': result_data.get('data', {}).get('verdict') == 'IDENTITY_CONFIRMED',
            'score': result_data.get('data', {}).get('confidence_score', 0),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'timestamp': datetime.now().timestamp(),
            'document_type': result_data.get('data', {}).get('ocr_extraction', {}).get('document_type', 'Inconnu'),
            'duration': 'N/A'  # À calculer lors de la vérification
        }
        
        self.history_data.insert(0, new_entry)  # Ajouter au début
        self._filtered_data = self._filter_history()
        self._apply_current_sort()
        self._save_history_data()