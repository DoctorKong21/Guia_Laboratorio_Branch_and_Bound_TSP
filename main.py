import os
import shutil
import subprocess
from copy import deepcopy

from PIL import Image, ImageDraw, ImageFont

import bnb_tsp

INF = bnb_tsp.INF


def resolve_dot_command() -> str:
    """Return the Graphviz dot executable path if available, else empty string."""
    cmd = shutil.which("dot")
    if cmd:
        return cmd

    windows_default = r"C:\Program Files\Graphviz\bin\dot.exe"
    if os.path.exists(windows_default):
        return windows_default

    return ""


def ensure_output_dirs() -> None:
    os.makedirs("outputs/json", exist_ok=True)
    os.makedirs("outputs/dot", exist_ok=True)
    os.makedirs("outputs/png", exist_ok=True)


def remove_root_artifacts() -> None:
    stray_files = [
        "tree_best_reduction.json",
        "tree_best_reduction.dot",
        "tree_lifo_reduction.json",
        "tree_lifo_reduction.dot",
        "tree_best_weak.json",
        "tree_best_weak.dot",
        "tree_best_CE99.json",
        "tree_best_CE99.dot",
    ]

    for filename in stray_files:
        if os.path.exists(filename):
            os.remove(filename)


def export_tree_png(filename: str, nodes) -> None:
    if not nodes:
        image = Image.new("RGB", (800, 400), "white")
        draw = ImageDraw.Draw(image)
        draw.text((24, 24), "No hay nodos para exportar.", fill="black")
        image.save(filename)
        return

    font = ImageFont.load_default()

    node_map = {node.id: node for node in nodes}
    children_map = {
        node.id: sorted(node.children)
        for node in nodes
    }
    roots = [node.id for node in nodes if node.parent_id is None]
    roots.sort()

    box_width = 180
    box_height = 72
    horizontal_gap = 240
    vertical_gap = 120
    margin_x = 60
    margin_y = 50

    positions = {}
    next_leaf_x = [0]

    def layout(node_id: int, depth: int) -> float:
        child_ids = children_map.get(node_id, [])
        y = margin_y + depth * vertical_gap

        if not child_ids:
            x = margin_x + next_leaf_x[0] * horizontal_gap
            next_leaf_x[0] += 1
        else:
            child_centers = [layout(child_id, depth + 1) for child_id in child_ids]
            x = (child_centers[0] + child_centers[-1]) / 2

        positions[node_id] = (x, y)
        return x

    for root_id in roots:
        layout(root_id, 0)

    max_x = max(x for x, _ in positions.values())
    max_y = max(y for _, y in positions.values())
    width = int(max(1000, max_x + box_width + margin_x))
    height = int(max(700, max_y + box_height + margin_y))

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    edge_color = (120, 120, 120)
    fill_map = {
        "Expandido": (173, 216, 230),
        "Podado por Cota": (240, 128, 128),
        "Podado por Inviabilidad": (255, 200, 120),
        "Solución Completa": (144, 238, 144),
    }

    for node in nodes:
        if node.parent_id is None:
            continue

        parent_pos = positions.get(node.parent_id)
        child_pos = positions.get(node.id)
        if not parent_pos or not child_pos:
            continue

        parent_center = (parent_pos[0] + box_width / 2, parent_pos[1] + box_height)
        child_center = (child_pos[0] + box_width / 2, child_pos[1])
        mid_y = (parent_center[1] + child_center[1]) / 2

        draw.line(
            [parent_center, (parent_center[0], mid_y)],
            fill=edge_color,
            width=2,
        )
        draw.line(
            [(parent_center[0], mid_y), (child_center[0], mid_y)],
            fill=edge_color,
            width=2,
        )
        draw.line(
            [(child_center[0], mid_y), child_center],
            fill=edge_color,
            width=2,
        )

    for node in nodes:
        x, y = positions[node.id]
        fill = fill_map.get(node.state, (255, 255, 255))
        outline = (70, 70, 70)
        draw.rounded_rectangle(
            [x, y, x + box_width, y + box_height],
            radius=12,
            fill=fill,
            outline=outline,
            width=2,
        )

        lines = [
            f"ID: {node.id}",
            node.path_string(),
            f"Bound: {node.bound_cost}",
            node.state,
        ]

        text = "\n".join(lines)
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=3, align="center")
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = x + (box_width - text_width) / 2
        text_y = y + (box_height - text_height) / 2

        draw.multiline_text(
            (text_x, text_y),
            text,
            fill="black",
            font=font,
            spacing=3,
            align="center",
        )

    image.save(filename)

base_matrix = [
    [INF, 14, 4, 10, 20],
    [14, INF, 7, 8, 12],
    [4, 5, INF, 16, 3],
    [11, 7, 16, INF, 2],
    [18, 10, 4, 2, INF]
]


def run_experiment(
    matrix,
    experiment_name,
    strategy,
    bound_type
):

    print("=" * 60)

    print(
        f"Experimento: {experiment_name}"
    )

    print(
        f"Estrategia: {strategy}"
    )

    print(
        f"Cota: {bound_type}"
    )

    path, cost = bnb_tsp.branch_and_bound(
        matrix,
        start=0,
        strategy=strategy,
        bound_type=bound_type
    )

    print(f"Mejor ruta: {path}")

    print(f"Mejor costo: {cost}")

    json_name = (
        f"outputs/json/{experiment_name}.json"
    )

    dot_name = (
        f"outputs/dot/{experiment_name}.dot"
    )

    bnb_tsp.export_json(
        json_name,
        bnb_tsp.all_nodes
    )

    bnb_tsp.export_dot(
        dot_name,
        bnb_tsp.all_nodes
    )

    png_name = f"outputs/png/{experiment_name}.png"

    dot_cmd = resolve_dot_command()
    if dot_cmd:
        subprocess.run(
            [dot_cmd, "-Tpng", dot_name, "-o", png_name],
            check=True
        )
    else:
        export_tree_png(png_name, bnb_tsp.all_nodes)
        print("No se encontro Graphviz (dot). Se genero el PNG con un fallback local.")

    print(f"Exportado: {png_name}")
    print(
        f"Exportado: {json_name}"
    )

    print(
        f"Exportado: {dot_name}"
    )

    print("=" * 60)


if __name__ == "__main__":
    ensure_output_dirs()
    remove_root_artifacts()

    # =====================================
    # PREGUNTA 4.1
    # =====================================

    run_experiment(
        base_matrix,
        "tree_best_reduction",
        "best",
        "reduction"
    )

    run_experiment(
        base_matrix,
        "tree_lifo_reduction",
        "lifo",
        "reduction"
    )

    # =====================================
    # PREGUNTA 4.2
    # =====================================

    run_experiment(
        base_matrix,
        "tree_best_weak",
        "best",
        "weak"
    )

    # =====================================
    # PREGUNTA 4.3
    # =====================================

    modified = deepcopy(base_matrix)

    # C -> E = 99

    modified[2][4] = 99

    run_experiment(
        modified,
        "tree_best_CE99",
        "best",
        "reduction"
    )

    print("Laboratorio finalizado.")
