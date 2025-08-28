# main.py

import os
import spacy
import logging
from tqdm import tqdm

import config
# MODIFICATION : Importer la nouvelle classe OntologyHandler
from ontology_parser import OntologyHandler
from pdf_processor import process_pdf_to_chunks
from llm_client import extract_triplets_with_llm
from knowledge_graph import KnowledgeGraph

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Pipeline principale pour construire le graphe de connaissances."""
    logger.info("--- Démarrage de la pipeline ---")

    # --- ÉTAPE 1 : Charger l'ontologie via le nouveau handler ---
    logger.info("Étape 1: Initialisation du gestionnaire d'ontologie...")
    try:
        ontology_handler = OntologyHandler(config.ONTOLOGY_PATH)
    except Exception as e:
        logger.error(f"Impossible d'initialiser l'ontologie. Arrêt. Erreur: {e}")
        return
    
    # --- ÉTAPE 2 : Initialisation des modèles et du graphe ---
    logger.info("Étape 2: Initialisation des modèles...")
    # ... (le reste de cette étape ne change pas) ...
    try:
        nlp = spacy.load(config.SPACY_MODEL)
    except OSError:
        logger.error(f"Modèle spaCy '{config.SPACY_MODEL}' non trouvé.")
        return
        
    kg = KnowledgeGraph(namespace=config.NAMESPACE)

    # --- ÉTAPE 3 : Traitement des PDF ---
    # ... (cette étape ne change pas jusqu'à la boucle d'extraction) ...
    pdf_files = [f for f in os.listdir(config.PDF_DIR) if f.lower().endswith('.pdf')]
    if not pdf_files:
        logger.warning(f"Aucun fichier PDF trouvé dans '{config.PDF_DIR}'.")
        return

    logger.info(f"Étape 3: Traitement de {len(pdf_files)} fichier(s) PDF...")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(config.PDF_DIR, pdf_file)
        chunks = process_pdf_to_chunks(pdf_path, nlp)
        
        if not chunks:
            continue
            
        all_triplets = []
        # --- MODIFICATION : Utiliser les listes de noms depuis le handler ---
        for chunk in tqdm(chunks, desc=f"Extraction de triplets de {pdf_file}"):
            triplets = extract_triplets_with_llm(
                chunk, 
                ontology_handler.class_names, 
                ontology_handler.property_names
            )
            all_triplets.extend(triplets)
        
        if all_triplets:
            logger.info(f"Ajout de {len(all_triplets)} triplets de {pdf_file} au graphe.")
            kg.add_triplets(all_triplets)

    # --- ÉTAPE 4 : Sauvegarde du graphe ---
    logger.info(f"--- Pipeline terminée. Total de {kg.get_total_triplets()} triplets. ---")
    # ... (le reste ne change pas) ...
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    kg.save_graph(os.path.join(config.OUTPUT_DIR, "knowledge_graph.ttl"), "turtle")
    kg.save_graph(os.path.join(config.OUTPUT_DIR, "knowledge_graph.jsonld"), "json-ld")
    kg.save_graph(os.path.join(config.OUTPUT_DIR, "knowledge_graph.owl"), "xml")

if __name__ == "__main__":
    main()