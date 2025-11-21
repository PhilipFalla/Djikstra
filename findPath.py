import networkx as nx
import pickle

with open("grafo.pkl", "rb") as f:
    G = pickle.load(f)

print("Graph loaded with", len(G.nodes()), "nodes and", len(G.edges()), "edges")

POIS = [
    "UFM",
    "Cayala",
    "ParqueLasAmericas",
    "PlazaDecimaZ14",
    "FridaysZ10",
    "MercadoLaVilla",
    "MyHouse",
    "TheSecretGardenZ9",
    "PraderaZ10",
    "MetroBowlZ15"
]

def shortest_path_AB(G, source, target, weight="length"):
    return nx.shortest_path(G, source=source, target=target, weight=weight)

def shortest_path_A_via_C_B(G, A, C, B, weight="length"):
    path_AC = nx.shortest_path(G, A, C, weight=weight)
    path_CB = nx.shortest_path(G, C, B, weight=weight)
    return path_AC + path_CB[1:]

def shortest_path_avoiding_C(G, A, B, C, weight="length"):
    G2 = G.copy()

    # aumentar pesos alrededor de C
    for u, v, data in G2.in_edges(C, data=True):
        data[weight] = float("inf")
    for u, v, data in G2.out_edges(C, data=True):
        data[weight] = float("inf")

    return nx.shortest_path(G2, A, B, weight=weight)

def apply_traffic_weights(G, hour):
    G2 = G.copy()

    peak = (7 <= hour <= 9) or (16 <= hour <= 19)
    if not peak:
        return G2

    degrees = dict(G2.degree())
    min_deg = min(degrees.values())
    max_deg = max(degrees.values())

    for u, v, data in G2.edges(data=True):
        base = data["length"]
        deg_u = degrees[u]
        factor = 1 + 3 * (1 - (deg_u - min_deg) / (max_deg - min_deg))
        data["traffic_weight"] = base * factor

    return G2


# ======================
# MENU PARA EL USUARIO
# ======================
def choose_poi(prompt):
    print(f"\n{prompt}")
    for i, poi in enumerate(POIS):
        print(f"{i+1}. {poi}")
    idx = int(input("Seleccione un número: ")) - 1
    return "POI_" + POIS[idx]

def choose_operation():
    print("\nSeleccione la operación a realizar:")
    print("1. Ruta más corta A → B")
    print("2. Ruta más corta A → C → B")
    print("3. Ruta A → B evitando C")
    print("4. Ruta A → B con pesos de tráfico")
    return int(input("Opción: "))


if __name__ == "__main__":

    op = choose_operation()

    # A y B siempre son necesarios
    A = choose_poi("Seleccione el punto A")
    B = choose_poi("Seleccione el punto B")

    if op == 1:
        print("\n=== SHORTEST A → B ===")
        print(shortest_path_AB(G, A, B))

    elif op == 2:
        C = choose_poi("Seleccione el punto C")
        print("\n=== SHORTEST A → C → B ===")
        print(shortest_path_A_via_C_B(G, A, C, B))

    elif op == 3:
        C = choose_poi("Seleccione el punto C (evitar)")
        print("\n=== SHORTEST A → B evitando C ===")
        print(shortest_path_avoiding_C(G, A, B, C))

    elif op == 4:
        hour = int(input("Ingrese la hora del día (0–23): "))
        G_peak = apply_traffic_weights(G, hour)
        print(f"\n=== SHORTEST UNDER TRAFFIC (hora={hour}) ===")
        print(shortest_path_AB(G_peak, A, B, weight="traffic_weight"))

    else:
        print("Opción inválida.")