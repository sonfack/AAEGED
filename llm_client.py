# llm_client.py

import re
import logging
import traceback
import time
from huggingface_hub import InferenceClient
# Notez que HF_MODEL_ID est toujours importé depuis config
from config import HF_MODEL_ID, HF_TOKEN, LLM_TEMPERATURE, LLM_MAX_NEW_TOKENS, LLM_TIMEOUT, NAMESPACE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialiser le client avec l'URL directe
client = InferenceClient(model=HF_MODEL_ID, token=HF_TOKEN, timeout=LLM_TIMEOUT)

# Test the chat_completion API to ensure the model is accessible
try:
    test_response = client.chat_completion(
        messages=[{"role": "user", "content": "Test prompt"}],
        max_tokens=50
    )
    logger.info(f"Test de l'API chat_completion réussi : {test_response.choices[0].message.content[:50]}...")
except Exception as e:
    logger.error(f"Échec du test de l'API chat_completion : {str(e)}")
    raise


def build_prompt(chunk: str, class_names: list[str], property_names: list[str]) -> str:
    return f"""
    ### INSTRUCTION :
    Tu es un expert en représentation de connaissances. À partir du texte ci-dessous, tu dois extraire des triplets RDF au format **N-Triples**.

    Voici les règles à respecter :
    1. Utilise **uniquement** les classes et propriétés définies dans l’ontologie ci-dessous.
    2. Tous les identifiants d'entités doivent être au format URI : `<{NAMESPACE}NomDeLEntite>`.
    3. **NomDeLEntite** doit être généré à partir de mots-clés du texte, sans espaces, ni articles, ni ponctuation. Utilise des noms clairs et courts.
    - Exemple : "l'accident de l'avion" → `<{NAMESPACE}AccidentAvion>`
    4. Ne retourne **que** les triplets RDF, un par ligne, sans texte supplémentaire ni commentaire.
    5. Le format **N-Triples** impose des URI entre chevrons (`< >`) et des littéraux entre guillemets (`" "`).

    ### ONTOLOGIE DISPONIBLE :
    - Classes :
    {', '.join(class_names)}

    - Propriétés :
    {', '.join(property_names)}

    ### TEXTE À ANALYSER :
    \"\"\"{chunk}\"\"\"

    ### TRIPLETS RDF ATTENDUS (format N-Triples) :
    """

def extract_triplets_with_llm(chunk: str, class_names: list[str], property_names: list[str]) -> list[str]:
    """Extrait des triplets en utilisant l'API chat_completion avec une logique de retry."""
    prompt = build_prompt(chunk, class_names, property_names)
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # L'utilisation de chat_completion est une bonne amélioration !
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=LLM_MAX_NEW_TOKENS,
                temperature=LLM_TEMPERATURE,
            )
            response_text = response.choices[0].message.content

            triple_pattern = re.compile(r'^<[^>]+>\s+<[^>]+>\s+<[^>]+>\s*\.$')
            triplets = [
                line.strip() for line in response_text.splitlines()
                if triple_pattern.match(line.strip())
            ]
            return triplets

        except Exception as e:
            logger.warning(f"Tentative {attempt + 1}/{max_retries} a échoué. Erreur : {e}")
            if attempt + 1 < max_retries:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Échec de l'extraction pour le chunk après {max_retries} tentatives.")
                logger.error(traceback.format_exc())
                return []
    return []