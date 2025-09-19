#!/bin/bash

# Création du dossier racine
# mkdir -p mobile

# Fichiers racine
touch mobile/main.py
touch mobile/requirements.txt

# Sous-dossier assets
mkdir -p mobile/assets/images
mkdir -p mobile/assets/styles

# Sous-dossier modules
mkdir -p mobile/modules
touch mobile/modules/__init__.py
touch mobile/modules/api_client.py
touch mobile/modules/camera_module.py
touch mobile/modules/document_scanner.py
touch mobile/modules/utils.py

# Sous-dossier screens
mkdir -p mobile/screens
touch mobile/screens/__init__.py
touch mobile/screens/home_screen.py
touch mobile/screens/scan_screen.py
touch mobile/screens/result_screen.py
touch mobile/screens/history_screen.py

echo "✅ Structure du projet mobile créée avec succès."
