import flet as ft
from screens.home_screen import HomeScreen
from screens.scan_screen import ScanScreen
from screens.result_screen import ResultScreen
from screens.history_screen import HistoryScreen
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IdentityVerificationApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Vérification d'Identité ANIP"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        
        # États de l'application
        self.scanned_document_data = None
        self.scanned_selfie_data = None
        self.verification_result = None
        
        # Initialisation des écrans
        self.home_screen = HomeScreen(self)
        self.scan_screen = ScanScreen(self)
        self.result_screen = ResultScreen(self)
        self.history_screen = HistoryScreen(self)
        
        # Navigation
        self.current_screen = "home"
        self.update_display()

    def navigate_to(self, screen_name: str, **kwargs):
        """Navigation entre les écrans"""
        self.current_screen = screen_name
        
        if screen_name == "scan" and kwargs.get("scan_type"):
            self.scan_screen.set_scan_type(kwargs["scan_type"])
        elif screen_name == "result" and kwargs.get("result_data"):
            self.verification_result = kwargs["result_data"]
        
        self.update_display()

    def update_display(self):
        """Met à jour l'affichage en fonction de l'écran courant"""
        self.page.clean()
        
        if self.current_screen == "home":
            self.page.add(self.home_screen.build())
        elif self.current_screen == "scan":
            self.page.add(self.scan_screen.build())
        elif self.current_screen == "result":
            self.page.add(self.result_screen.build())
        elif self.current_screen == "history":
            self.page.add(self.history_screen.build())

    def set_scanned_data(self, document_data: bytes, selfie_data: bytes):
        """Stocke les données scannées"""
        self.scanned_document_data = document_data
        self.scanned_selfie_data = selfie_data

    def get_scanned_data(self):
        """Récupère les données scannées"""
        return self.scanned_document_data, self.scanned_selfie_data

def main(page: ft.Page):
    app = IdentityVerificationApp(page)
    # install safe call_from_async helper so code can schedule UI updates from threads
    try:
        from modules.ui_utils import install_call_from_async
        install_call_from_async(page)
    except Exception:
        pass
    page.update()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)