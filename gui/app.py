# app.py (versión corregida)
from flask import Flask, render_template, request
import networkx as nx
import pickle
import matplotlib

# ========= IMPORTANT: use non-GUI backend BEFORE importing pyplot =========
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

# =====================================================
# CARGAR GRAFO
# =====================================================
with open("grafo.pkl", "rb") as f:
    G = pickle.load(f)

# Asegurarnos de que nodos tienen 'x' y 'y' (OSMnx suele usar estas etiquetas)
# Construimos pos para NetworkX basado en x,y
pos = {n: (data.get("x"), data.get("y")) for n, data in G.nodes(data=True)}

POIS = [
    "POI_UFM",
    "POI_Cayala",
    "POI_ParqueLasAmericas",
    "POI_PlazaDecimaZ14",
    "POI_FridaysZ10",
    "POI_MercadoLaVilla",
    "POI_MyHouse",
    "POI_TheSecretGardenZ9",
    "POI_PraderaZ10",
    "POI_MetroBowlZ15"
]

# =====================================================
# FUNCIONES DE RUTA
# =====================================================
def shortest_path_AB(G, A, B):
    return nx.shortest_path(G, A, B, weight="length")

def shortest_path_A_via_C_B(G, A, C, B):
    AC = nx.shortest_path(G, A, C, weight="length")
    CB = nx.shortest_path(G, C, B, weight="length")
    return AC + CB[1:]

def shortest_path_avoiding_C(G, A, B, C):
    G2 = G.copy()
    # proteger si C no existe
    if C not in G2:
        raise KeyError(f"El nodo a evitar ({C}) no existe en el grafo.")
    for u, v, data in G2.in_edges(C, data=True):
        data["length"] = float("inf")
    for u, v, data in G2.out_edges(C, data=True):
        data["length"] = float("inf")
    return nx.shortest_path(G2, A, B, weight="length")

def apply_traffic_weights(G, hour):
    G2 = G.copy()
    peak = (7 <= hour <= 9) or (16 <= hour <= 19)

    if not peak:
        # aseguramos que existe la llave traffic_weight para evitar KeyError
        for u, v, data in G2.edges(data=True):
            data["traffic_weight"] = data.get("length", 1.0)
        return G2

    degrees = dict(G2.degree())
    dmin, dmax = min(degrees.values()), max(degrees.values())

    # evitar división por cero si dmax == dmin
    denom = dmax - dmin if dmax != dmin else 1.0

    for u, v, data in G2.edges(data=True):
        base = data.get("length", data.get("distance", 1.0))
        du = degrees.get(u, 1)
        factor = 1 + 3*(1 - (du - dmin)/denom)
        data["traffic_weight"] = base * factor

    return G2

# =====================================================
# GRAFICAR
# =====================================================
def draw_graph_with_path(G_local, path, filename="ruta.png"):
    # Ensure static directory exists: <project>/Djikstra/gui/static
    static_dir = os.path.join(app.root_path, "static")
    os.makedirs(static_dir, exist_ok=True)

    outfile = os.path.join(static_dir, filename)

    plt.figure(figsize=(10, 7))
    nx.draw_networkx_edges(G_local, pos, edge_color="lightgray", width=0.5)
    nx.draw_networkx_nodes(G_local, pos, node_size=10, node_color="black", alpha=0.6)

    if path:
        edges = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(G_local, pos, nodelist=path, node_size=60, node_color="red")
        nx.draw_networkx_edges(G_local, pos, edgelist=edges, edge_color="red", width=2.5)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()

# =====================================================
# FLASK APP
# =====================================================
app = Flask(__name__, static_folder="static")

@app.route("/", methods=["GET", "POST"])
def index():
    image_path = None
    error_msg = None

    if request.method == "POST":
        A = request.form.get("A")
        B = request.form.get("B")
        C = request.form.get("C") or None
        hour = request.form.get("hour")

        mode = request.form.get("mode")
        G2 = G

        # validaciones básicas
        if A not in G:
            error_msg = f"El punto A '{A}' no existe en el grafo."
        elif B not in G:
            error_msg = f"El punto B '{B}' no existe en el grafo."

        if not error_msg:
            try:
                if mode == "AB":
                    path = shortest_path_AB(G, A, B)

                elif mode == "ACB":
                    if not C:
                        raise ValueError("Debes seleccionar C para A → C → B")
                    path = shortest_path_A_via_C_B(G, A, C, B)

                elif mode == "avoidC":
                    if not C:
                        raise ValueError("Debes seleccionar C para evitar")
                    path = shortest_path_avoiding_C(G, A, B, C)

                elif mode == "traffic":
                    hour = int(hour) if hour else 12
                    G2 = apply_traffic_weights(G, hour)
                    path = nx.shortest_path(G2, A, B, weight="traffic_weight")

                else:
                    raise ValueError("Modo no reconocido")

                draw_graph_with_path(G2, path, filename="ruta.png")
                image_path = "ruta.png"

            except nx.NetworkXNoPath:
                error_msg = "No existe camino entre los puntos dados."
            except KeyError as e:
                error_msg = str(e)
            except Exception as e:
                # para debug puedes imprimir e
                error_msg = f"Error inesperado: {e}"

    return render_template("index.html", POIS=POIS, image_path=image_path, error_msg=error_msg)

if __name__ == "__main__":
    # debug True arranca con reloader y multi-thread; está bien, Agg evita ventanas GUI.
    app.run(debug=True)