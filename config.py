# config.py

import os
from huggingface_hub import HfFolder

# --- Chemins ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ONTOLOGY_PATH = os.path.join(BASE_DIR, "ontology", "baeo_application.ttl")
PDF_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# --- Modèles ---
# Modèle de langue pour le traitement de texte (spaCy)
SPACY_MODEL = "fr_core_news_lg"

# Modèle Hugging Face pour l'extraction de triplets
# Assurez-vous d'avoir un token Hugging Face configuré.
# Vous pouvez vous connecter via le terminal : `huggingface-cli login`
# ou définir la variable d'environnement HUGGING_FACE_HUB_TOKEN.
HF_TOKEN = HfFolder.get_token()
HF_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1" # Exemple, choisissez un modèle adapté

# --- Paramètres LLM ---
LLM_TEMPERATURE = 0.1
LLM_MAX_NEW_TOKENS = 1024
LLM_TIMEOUT = 320 # en secondes

# --- Graphe de Connaissances ---
NAMESPACE = "http://www.enit.fr/2022/03/baeo#"