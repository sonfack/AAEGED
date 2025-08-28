# ontology_parser.py

import logging
from typing import List, Dict, Tuple
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

# Initialisation du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OntologyHandler:
    """Gestionnaire automatique de l'ontologie BAEO."""
    
    def __init__(self, ontology_path: str):
        """
        Initialise le gestionnaire, charge l'ontologie et extrait
        automatiquement les classes et propriétés.
        """
        self.ontology_graph = Graph()
        try:
            self.ontology_graph.parse(ontology_path, format="turtle")
        except Exception as e:
            logger.error(f"Impossible de parser l'ontologie à l'adresse : {ontology_path}. Erreur : {e}")
            raise
            
        self.BAEO = Namespace("http://www.enit.fr/2022/03/baeo#")
        
        # Extraction automatique
        self.classes = self._extract_classes()
        self.properties = self._extract_properties()
        
        # Prépare des listes de noms simples pour les prompts
        self.class_names = sorted([cls['label'] or cls['uri'].split('#')[-1] for cls in self.classes if 'uri' in cls])
        self.property_names = sorted([prop['label'] or prop['uri'].split('#')[-1] for prop in self.properties if 'uri' in prop])
        
        logger.info(f"Ontologie chargée: {len(self.class_names)} classes et {len(self.property_names)} propriétés extraites.")
    
    def _extract_classes(self) -> List[Dict[str, str]]:
        """Extraire automatiquement les classes de l'ontologie avec leurs labels."""
        query_str = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?cls ?label WHERE {
            ?cls a owl:Class .
            FILTER(isIRI(?cls))
            OPTIONAL { ?cls rdfs:label ?label . FILTER(lang(?label) = "" || langMatches(lang(?label), "fr")) }
        }
        """
        results = self.ontology_graph.query(query_str)
        return [{'uri': str(row.cls), 'label': str(row.label) if row.label else ""} for row in results]
    
    def _extract_properties(self) -> List[Dict[str, str]]:
        """Extraire automatiquement les propriétés avec domaine, range et labels."""
        query_str = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?prop ?domain ?range ?label WHERE {
            {?prop a owl:ObjectProperty} UNION {?prop a owl:DatatypeProperty}
            FILTER(isIRI(?prop))
            OPTIONAL { ?prop rdfs:domain ?domain }
            OPTIONAL { ?prop rdfs:range ?range }
            OPTIONAL { ?prop rdfs:label ?label . FILTER(lang(?label) = "" || langMatches(lang(?label), "fr")) }
        }
        """
        results = self.ontology_graph.query(query_str)
        return [{
            'uri': str(row.prop),
            'domain': str(row.domain) if row.domain else None,
            'range': str(row.range) if row.range else None,
            'label': str(row.label) if row.label else ""
        } for row in results]