import requests
import base64
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = 300  # Timeout en secondes

    def verify_identity(self, document_image: bytes, selfie_image: bytes) -> Optional[Dict]:
        """Envoie les images à l'API de vérification"""
        try:
            files = {
                'document': ('document.jpg', document_image, 'image/jpeg'),
                'selfie': ('selfie.jpg', selfie_image, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{self.base_url}/verify",
                files=files,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur connexion API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return None

    def extract_ocr(self, document_image: bytes) -> Optional[Dict]:
        """Extraction OCR seule"""
        try:
            files = {
                'document': ('document.jpg', document_image, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{self.base_url}/ocr/extract",
                files=files,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur OCR API: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur connexion OCR API: {e}")
            return None

    def health_check(self) -> bool:
        """Vérifie si l'API est disponible"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False