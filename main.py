# =========================
# main.py
# =========================
import os
import shutil
import subprocess
from copy import deepcopy
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
        print("No se encontro Graphviz (dot). Se omite exportacion PNG.")

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
