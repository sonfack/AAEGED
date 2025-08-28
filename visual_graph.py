from rdflib import Graph
from pyvis.network import Network

# Charger ton graphe
g = Graph()
g.parse("output/knowledge_graph.ttl", format="turtle")

# Créer le réseau interactif
net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", notebook=False)

for s, p, o in g:
    net.add_node(str(s), str(s))
    net.add_node(str(o), str(o))
    net.add_edge(str(s), str(o), title=str(p))

# Sauvegarder en HTML
net.write_html("graph.html")
print("Graphique généré → Ouvre 'graph.html' dans ton navigateur.")
