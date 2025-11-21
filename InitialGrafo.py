import osmnx as ox
import networkx as nx
from shapely.geometry import Polygon, Point
from geopy.distance import geodesic

# Define POLYGON area
poly_coords = [
    (-90.48948993505584, 14.61677635838943),
    (-90.48985599150609, 14.611051119286799),
    (-90.49288282245121, 14.610521970686008),
    (-90.4959034655792,  14.607774273537402),
    (-90.49701852547847, 14.603181311466741),
    (-90.49703041876597, 14.598854712523234),
    (-90.49893020278289, 14.602816768695135),
    (-90.50070319030728, 14.606966364160002),
    (-90.50507381071615, 14.612552234373794),
    (-90.52571318543703, 14.610890960804753),
    (-90.52946337212731, 14.60448930672949),
    (-90.52343779126637, 14.595967070404512),
    (-90.51926567402818, 14.59420948863071),
    (-90.52642588212251, 14.573561432572973),
    (-90.52521638751215, 14.571969438588667),
    (-90.51583070933442, 14.582738585385457),
    (-90.50632643420168, 14.579205629831549),
    (-90.50108005170567, 14.584645589076658),
    (-90.48961432146666, 14.575671464124369),
    (-90.48777810191125, 14.578071093731438),
    (-90.48449935256788, 14.57710368474173),
    (-90.48292543673881, 14.580651088069317),
    (-90.49026130498139, 14.590034730068552),
    (-90.49418283505527, 14.595233917960414),
    (-90.4948901077214,  14.60480012031644),
    (-90.493882419999,   14.60835055539357),
    (-90.48450317273755, 14.606150292523935),
    (-90.4825394735865,  14.616651348836726),
    (-90.48948993505584, 14.61677635838943)
]

polygon = Polygon(poly_coords)

# ---------------------------------------------------------
# 2. Load OSM graph
# ---------------------------------------------------------
ox.settings.use_cache = True
ox.settings.log_console = True

G = ox.graph_from_polygon(polygon, network_type="drive")

print("\nGraph loaded!")
print(f"Nodes: {len(G.nodes())}")
print(f"Edges: {len(G.edges())}")


# Define POI coordinates (lat, lon)
pois = {
    "UFM": (14.603554, -90.489188),
    "Cayala": (14.606130, -90.489984),
    "ParqueLasAmericas": (14.594133, -90.514833),
    "PlazaDecimaZ14": (14.598799, -90.508603),
    "FridaysZ10": (14.588306, -90.513110),
    "MercadoLaVilla": (14.590766, -90.519698),
    "MyHouse": (14.584265071692746, -90.5098467388304),
    "TheSecretGardenZ9": (14.605342, -90.513807),
    "PraderaZ10": (14.588566, -90.510002),
    "MetroBowlZ15": (14.6010, -90.4985)
}

# Add POIs to graph + connect them to nearest street node
def add_poi_node(G, poi_name, lat, lon):
    poi_id = f"POI_{poi_name}"

    # Find closest OSM node
    nearest_node = ox.distance.nearest_nodes(G, lon, lat)
    
    # Add the node
    G.add_node(poi_id, y=lat, x=lon, type="poi")

    # Distance in meters
    d = geodesic((lat, lon), (G.nodes[nearest_node]['y'], G.nodes[nearest_node]['x'])).meters

    # Add bidirectional edges (because it's a drive network)
    G.add_edge(poi_id, nearest_node, length=d)
    G.add_edge(nearest_node, poi_id, length=d)

    print(f"✔ Added POI '{poi_name}' → connected to OSM node {nearest_node} at {int(d)} m")

# Add all POIs
for name, (lat, lon) in pois.items():
    add_poi_node(G, name, lat, lon)

print("\nAll POIs added successfully!")
print("Total nodes now:", len(G.nodes()))
print("Total edges now:", len(G.edges()))

import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 3. Visualize the street graph + POIs
# ---------------------------------------------------------

# Get node positions for plotting
pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}

# Separate normal nodes and POI nodes
normal_nodes = [n for n, d in G.nodes(data=True) if d.get("type") != "poi"]
poi_nodes     = [n for n, d in G.nodes(data=True) if d.get("type") == "poi"]

# Plot graph
plt.figure(figsize=(12, 12))

# Plot edges
nx.draw_networkx_edges(G, pos, edge_color="gray", width=0.8, alpha=0.7)

# Plot normal nodes
nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes,
                       node_size=5, node_color="black", alpha=0.6)

# Plot POI nodes
nx.draw_networkx_nodes(G, pos, nodelist=poi_nodes,
                       node_size=80, node_color="red", alpha=0.9)

# Add POI labels
nx.draw_networkx_labels(G, pos,
                        labels={n: n.replace("POI_", "") for n in poi_nodes},
                        font_size=9, font_color="red")

plt.title("Street Network + POIs")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.axis("equal")
plt.tight_layout()
plt.show()