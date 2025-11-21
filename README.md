# Proyecto de Rutas con Dijkstra y Visualización Web

Este proyecto implementa un sistema de cálculo de rutas utilizando un grafo extraído de OpenStreetMap, procesado con OSMnx y analizado mediante algoritmos de NetworkX.  
Incluye una interfaz web en Flask que permite al usuario seleccionar puntos de interés y visualizar rutas con distintas condiciones (pasar por un punto, evitarlo o ajustar pesos según tráfico simulado).

---

## Funcionalidades principales

- **Ruta más corta A → B** usando Dijkstra.
- **Ruta A → C → B** pasando por un punto intermedio.
- **Ruta A → B evitando C** aplicando restricciones sobre aristas.
- **Ruta A → B ponderada por hora del día**, simulando tráfico.
- **Visualización del grafo** con la ruta resaltada.
- **Interfaz web con Flask** para ingresar parámetros y mostrar resultados.

---

## Requisitos

- Python 3.10+
- pip
- virtualenv (opcional pero recomendado)

---

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo
```

Crea y activa el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala dependencias:

```bash
pip install -r requirements.txt
```

Asegúrate de tener el archivo `grafo.pkl` en la carpeta raíz del proyecto.

---

## Ejecución

Inicia la aplicación Flask desde el directorio de /Djikstra:

```bash
python app.py
```

Abre el navegador en:

```
http://127.0.0.1:5000/
```

---

## Estructura del proyecto

```
/Djisktra
│── LICENSE
│── README.md
│── grafo.pkl                # Grafo final serializado
│── createGraph.py           # Script para crear el grafo y guardarlo como grafo.pkl
│── findPath.py              # Scripts experimentales para pruebas de rutas
│
│── images/                  # Material de apoyo y visualizaciones
│     ├── grafoMapeado.png
│     ├── map&POIs.png
│     └── mapa.png
│
│── gui/                     # Interfaz web con Flask
│     │── app.py             # Servidor Flask principal
│     │
│     ├── static/
│     │     └── ruta.png     # Imagen generada de la ruta (se sobrescribe)
│     │
│     └── templates/
│           └── index.html   # Interfaz web del usuario
│
└── requirements.txt
```

---

## Explicación técnica

- **Dijkstra** es implementado vía funciones integradas de NetworkX:
  - `nx.shortest_path(G, A, B, weight="length")`
- Para evitar un nodo C, se copian las aristas hacia/desde C y se asigna peso infinito.
- Para la simulación de tráfico:
  - Se normaliza el grado de los nodos.
  - Nodos con menor conectividad reciben mayor peso en horas pico.
  - Se utiliza un peso alterno `traffic_weight`.

---

## Trabajo colaborativo

El repositorio debe incluir:
- Commits **progresivos** y **repartidos entre todos los miembros del equipo**.
- Comentarios claros en cada commit que indiquen la contribución realizada.
- Falta de commits individuales se considerará como **no participación** en el proyecto.

---

## Archivo adicional

Este README ha sido exportado también como `README.txt` para cumplir con los requisitos.

---

## Contacto

Para cualquier duda, comuníquese con los desarrolladores del proyecto.
