# knowledge_graph.py

import re
import logging
from rdflib import Graph, URIRef
from rdflib.util import from_n3
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeGraph:
    def __init__(self, namespace: str):
        self.graph = Graph()
        self.namespace = namespace
        self.graph.bind("baeo", URIRef(namespace))
    
    def _sanitize_uri_part(self, part: str) -> str:
        """Nettoie une partie d'URI pour la rendre valide."""
        # Supprime les chevrons et les points finaux
        part = part.strip('<>. ')
        # Remplace les espaces et autres caractères invalides
        # quote() s'assure que l'URI est valide
        return quote(part.replace(' ', '_'))

    def add_triplets(self, triplets: list[str]):
        """
        Ajoute une liste de triplets (au format N-Triples) au graphe, en les validant.
        """
        triple_pattern = re.compile(r'^<([^>]+)>\s+<([^>]+)>\s+<([^>]+)>\s*\.$')
        
        for t_str in triplets:
            match = triple_pattern.match(t_str)
            if not match:
                logger.warning(f"Triplet ignoré (format invalide) : {t_str}")
                continue
            
            s, p, o = match.groups()
            
            try:
                # from_n3 est une manière robuste de parser les composants
                subject = from_n3(f"<{s}>")
                predicate = from_n3(f"<{p}>")
                obj = from_n3(f"<{o}>")
                
                self.graph.add((subject, predicate, obj))
            except Exception as e:
                logger.error(f"Impossible d'ajouter le triplet '{t_str}': {e}")

    def save_graph(self, output_path: str, file_format: str):
        """
        Sérialise et sauvegarde le graphe dans un format spécifié.

        Args:
            output_path: Chemin du fichier de sortie.
            file_format: Le format de sérialisation ('turtle', 'json-ld', 'xml').
        """
        if not self.graph:
            logger.warning("Le graphe est vide, aucun fichier ne sera sauvegardé.")
            return

        try:
            # 'xml' correspond au format RDF/XML, souvent utilisé pour OWL.
            self.graph.serialize(destination=output_path, format=file_format)
            logger.info(f"Graphe sauvegardé avec succès dans {output_path} (format: {file_format})")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du graphe en {file_format}: {e}")

    def get_total_triplets(self) -> int:
        """Retourne le nombre total de triplets dans le graphe."""
        return len(self.graph)