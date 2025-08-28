# pdf_processor.py

import spacy
from unstructured.partition.pdf import partition_pdf
import logging
import tempfile
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf_to_chunks(pdf_path: str, spacy_model: spacy.language.Language) -> list[str]:
    """
    Extrait le texte d'un PDF, le nettoie et le segmente en phrases.

    Args:
        pdf_path: Chemin vers le fichier PDF.
        spacy_model: Modèle spaCy chargé.

    Returns:
        Une liste de chaînes de caractères (chunks).
    """
    logger.info(f"Traitement du fichier PDF : {pdf_path}")
    try:
        temp_dir = "/home/nomdecode/tmp/"
        os.makedirs(temp_dir, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_dir) as tmpdir:
            elements = partition_pdf(
                filename=pdf_path,
                strategy="fast",  # méthode plus légère qui évite LaTeX/MiKTeX
                languages=['fra'],
                extract_images_in_pdf=False,
                tempdir=tmpdir
            )
        raw_text = "\n".join([str(el) for el in elements])

        # Nettoyage simple du texte
        cleaned_text = " ".join(raw_text.split())

        doc = spacy_model(cleaned_text)
        chunks = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

        logger.info(f"PDF {pdf_path} a été segmenté en {len(chunks)} chunks.")
        return chunks
    except Exception as e:
        logger.error(f"Erreur lors du traitement du PDF {pdf_path}: {e}")
        return []
