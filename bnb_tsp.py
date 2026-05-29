import heapq
import json
import logging
from collections import deque
from copy import deepcopy
from typing import List, Optional

INF = 10**9

# =========================
# CONFIGURACION LOGS
# =========================

logger = logging.getLogger("bnb_tsp")

if not logger.handlers:
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

# =========================
# VARIABLES GLOBALES
# =========================

node_counter = 0
all_nodes = []

stats = {
    "generated": 0,
    "expanded": 0,
    "pruned": 0,
    "completed": 0
}

CITY_NAMES = ["A", "B", "C", "D", "E"]

# =========================
# NODO
# =========================

class Node:

    def __init__(
        self,
        parent_id: Optional[int],
        path: List[int],
        reduced_matrix: List[List[int]],
        bound_cost: float,
        real_cost: float,
        level: int,
        state: str
    ):

        global node_counter

        self.id = node_counter
        node_counter += 1

        self.parent_id = parent_id

        self.path = path[:]

        self.reduced_matrix = reduced_matrix

        self.bound_cost = bound_cost

        self.real_cost = real_cost

        self.level = level

        self.state = state

        self.children = []

        all_nodes.append(self)

        stats["generated"] += 1

        logger.info(
            f"Nodo {self.id} creado | "
            f"path={self.path} | "
            f"bound={self.bound_cost}"
        )

    def path_string(self):

        return " -> ".join(CITY_NAMES[i] for i in self.path)

    def to_dict(self):

        matrix = []

        for row in self.reduced_matrix:
            matrix.append([
                None if x >= INF else x
                for x in row
            ])

        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "children": self.children,
            "path": self.path_string(),
            "bound_cost": self.bound_cost,
            "real_cost": self.real_cost,
            "level": self.level,
            "state": self.state,
            "reduced_matrix": matrix
        }


# =========================
# REDUCCION MATRIZ
# =========================

def reduce_matrix(matrix):

    n = len(matrix)

    mat = deepcopy(matrix)

    reduction_cost = 0

    # -------------------------
    # REDUCCION FILAS
    # -------------------------

    for i in range(n):

        row_min = INF

        for j in range(n):
            if mat[i][j] < row_min:
                row_min = mat[i][j]

        if row_min == INF or row_min == 0:
            continue

        reduction_cost += row_min

        for j in range(n):
            if mat[i][j] < INF:
                mat[i][j] -= row_min

    # -------------------------
    # REDUCCION COLUMNAS
    # -------------------------

    for j in range(n):

        col_min = INF

        for i in range(n):
            if mat[i][j] < col_min:
                col_min = mat[i][j]

        if col_min == INF or col_min == 0:
            continue

        reduction_cost += col_min

        for i in range(n):
            if mat[i][j] < INF:
                mat[i][j] -= col_min

    return mat, reduction_cost


# =========================
# COTA INGENUA
# =========================

def naive_bound(path, original_matrix):

    n = len(original_matrix)

    visited = set(path)

    total = 0

    for i in range(n):

        if i in visited:
            continue

        min_edge = INF

        for j in range(n):

            if i == j:
                continue

            if original_matrix[i][j] < min_edge:
                min_edge = original_matrix[i][j]

        total += min_edge

    return total


# =========================
# CREAR HIJO
# =========================

def create_child(parent, i, j, original_matrix, start):

    n = len(parent.reduced_matrix)

    if parent.reduced_matrix[i][j] >= INF:
        return None

    matrix = deepcopy(parent.reduced_matrix)

    real_edge_cost = original_matrix[i][j]

    # -------------------------
    # BLOQUEAR FILA
    # -------------------------

    for col in range(n):
        matrix[i][col] = INF

    # -------------------------
    # BLOQUEAR COLUMNA
    # -------------------------

    for row in range(n):
        matrix[row][j] = INF

    # -------------------------
    # EVITAR CICLOS PREMATUROS
    # -------------------------

    matrix[j][start] = INF

    reduced_matrix, reduction_cost = reduce_matrix(matrix)

    new_real_cost = parent.real_cost + real_edge_cost

    new_bound = new_real_cost + reduction_cost

    child = Node(
        parent_id=parent.id,
        path=parent.path + [j],
        reduced_matrix=reduced_matrix,
        bound_cost=new_bound,
        real_cost=new_real_cost,
        level=parent.level + 1,
        state="Expandido"
    )

    parent.children.append(child.id)

    return child


# =========================
# BRANCH AND BOUND
# =========================

def branch_and_bound(
    original_matrix,
    start=0,
    strategy="best",
    bound_type="reduction"
):

    global node_counter
    global all_nodes
    global stats

    node_counter = 0
    all_nodes = []

    stats = {
        "generated": 0,
        "expanded": 0,
        "pruned": 0,
        "completed": 0
    }

    n = len(original_matrix)

    root_matrix, root_reduction = reduce_matrix(original_matrix)

    root = Node(
        parent_id=None,
        path=[start],
        reduced_matrix=root_matrix,
        bound_cost=root_reduction,
        real_cost=0,
        level=0,
        state="Expandido"
    )

    best_cost = INF
    best_path = None

    # -------------------------
    # BEST FIRST
    # -------------------------

    if strategy == "best":

        structure = []

        heapq.heappush(
            structure,
            (root.bound_cost, root.id, root)
        )

    # -------------------------
    # LIFO
    # -------------------------

    elif strategy == "lifo":

        structure = [root]

    # -------------------------
    # FIFO
    # -------------------------

    elif strategy == "fifo":

        structure = deque([root])

    else:

        raise ValueError("Estrategia inválida")

    # =========================
    # BUCLE PRINCIPAL
    # =========================

    while True:

        # -------------------------
        # EXTRAER NODO
        # -------------------------

        if strategy == "best":

            if not structure:
                break

            _, _, node = heapq.heappop(structure)

        elif strategy == "lifo":

            if not structure:
                break

            node = structure.pop()

        else:

            if not structure:
                break

            node = structure.popleft()

        stats["expanded"] += 1

        logger.info(
            f"Expandiendo nodo {node.id}"
        )

        # -------------------------
        # PODA POR COTA
        # -------------------------

        if node.bound_cost >= best_cost:

            node.state = "Podado por Cota"

            stats["pruned"] += 1

            logger.info(
                f"Nodo {node.id} podado "
                f"(bound={node.bound_cost} >= "
                f"incumbente={best_cost})"
            )

            continue

        # -------------------------
        # SOLUCION COMPLETA
        # -------------------------

        if node.level == n - 1:

            last = node.path[-1]

            if original_matrix[last][start] >= INF:

                node.state = "Podado por Inviabilidad"

                stats["pruned"] += 1

                continue

            total_cost = (
                node.real_cost +
                original_matrix[last][start]
            )

            node.state = "Solución Completa"

            stats["completed"] += 1

            logger.info(
                f"Solucion encontrada "
                f"nodo={node.id} "
                f"costo={total_cost}"
            )

            if total_cost < best_cost:

                best_cost = total_cost

                best_path = node.path + [start]

                logger.info(
                    f"Nuevo incumbente = {best_cost}"
                )

            continue

        # -------------------------
        # EXPANDIR HIJOS
        # -------------------------

        current_city = node.path[-1]

        visited = set(node.path)

        for j in range(n):

            if j in visited:
                continue

            child = create_child(
                node,
                current_city,
                j,
                original_matrix,
                start
            )

            if child is None:

                continue

            # -------------------------
            # COTA
            # -------------------------

            if bound_type == "weak":

                bound = (
                    child.real_cost +
                    naive_bound(
                        child.path,
                        original_matrix
                    )
                )

            else:

                bound = child.bound_cost

            child.bound_cost = bound

            # -------------------------
            # PODA
            # -------------------------

            if bound >= best_cost:

                child.state = "Podado por Cota"

                stats["pruned"] += 1

                continue

            # -------------------------
            # INSERTAR
            # -------------------------

            if strategy == "best":

                heapq.heappush(
                    structure,
                    (bound, child.id, child)
                )

            elif strategy == "lifo":

                structure.append(child)

            else:

                structure.append(child)

    logger.info("=================================")
    logger.info(f"MEJOR COSTO: {best_cost}")
    logger.info(f"MEJOR RUTA: {best_path}")
    logger.info(f"NODOS GENERADOS: {stats['generated']}")
    logger.info(f"NODOS EXPANDIDOS: {stats['expanded']}")
    logger.info(f"NODOS PODADOS: {stats['pruned']}")
    logger.info("=================================")

    return best_path, best_cost


# =========================
# EXPORT JSON
# =========================

def export_json(filename, nodes):

    data = [node.to_dict() for node in nodes]

    with open(filename, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# =========================
# EXPORT DOT
# =========================

def export_dot(filename, nodes):

    color_map = {
        "Expandido": "lightblue",
        "Podado por Cota": "red",
        "Podado por Inviabilidad": "orange",
        "Solución Completa": "green"
    }

    with open(filename, "w", encoding="utf-8") as f:

        f.write('ratio=compress;\n')

        f.write('size="20,20";\n')
        
        f.write("digraph TSP_Tree {\n")

        f.write('rankdir=TB;\n')

        f.write('nodesep=0.5;\n')

        f.write('ranksep=1.2;\n')

        f.write('splines=true;\n')

        f.write('overlap=false;\n')

        f.write('dpi=200;\n')
        f.write('node [shape=box, fontname="Arial", fontsize=10, width=2.5, height=1];\n')

        for node in nodes:

            color = color_map.get(
                node.state,
                "white"
            )

            label = (
                f"ID: {node.id}\\n"
                f"{node.path_string()}\\n"
                f"Bound: {node.bound_cost}\\n"
                f"Estado: {node.state}"
            )

            f.write(
                f'Node{node.id} '
                f'[label="{label}", '
                f'style=filled, '
                f'fillcolor={color}];\n'
            )

            if node.parent_id is not None:

                f.write(
                    f"Node{node.parent_id} "
                    f"-> Node{node.id};\n"
                )

        f.write("}\n")

