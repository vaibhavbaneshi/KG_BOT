import networkx as nx
import matplotlib.pyplot as plt

def visualize_graph(graph_data):
    G = nx.Graph()
    G.add_nodes_from(graph_data["nodes"])
    G.add_edges_from([(u, v, {"label": d}) for u, v, d in graph_data["edges"]])

    # Layout
    pos = nx.spring_layout(G, k=0.8, iterations=50)

    # Highlight center node (assuming first node is main entity)
    main_node = graph_data["nodes"][0]

    # Node colors and sizes
    node_colors = ["orange" if n == main_node else "skyblue" for n in G.nodes()]
    node_sizes = [3000 if n == main_node else 1800 for n in G.nodes()]

    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9)
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=9, font_family="sans-serif")

    # Edge labels (show only unique types)
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True) if d["label"] != "RELATED"}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.axis("off")
    plt.show()