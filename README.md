# Branch & Bound para el Problema del Viajante (TSP)

## Descripción

Este proyecto implementa el Problema del Viajante de Comercio (TSP) utilizando la técnica de Ramificación y Poda (Branch & Bound), incorporando estrategias de exploración FIFO, LIFO y Best-First.

Exportando cada nodo generado en formato JSON y Graphviz DOT, permitiendo visualizar el comportamiento de la poda y el impacto de distintas funciones de acotación.

---

## Requisitos

* Python 3.10+
* Graphviz instalado

Instalación de dependencias:

```bash
pip install graphviz
```

---

## Ejecución

Ejecutar:

```bash
python tsp_branch_bound.py
```

El programa generará:

* Árboles en formato `.json`
* Árboles en formato `.dot`
* Imágenes `.png`

---

## Escenarios Generados

### 1. Best-First + Reducción Completa

Archivo:

* tree_best_reduction.json
* tree_best_reduction.png

### 2. LIFO + Reducción Completa

Archivo:

* tree_lifo_reduction.json
* tree_lifo_reduction.png

### 3. Best-First + Cota Débil

Archivo:

* tree_best_weak.json
* tree_best_weak.png

### 4. Best-First + Modificación C→E = 99

Archivo:

* tree_best_CE99.json
* tree_best_CE99.png

---

## Matriz Utilizada

|   | A  | B  | C  | D  | E  |
| - | -- | -- | -- | -- | -- |
| A | ∞  | 14 | 4  | 10 | 20 |
| B | 14 | ∞  | 7  | 8  | 12 |
| C | 4  | 5  | ∞  | 16 | 3  |
| D | 11 | 7  | 16 | ∞  | 2  |
| E | 18 | 10 | 4  | 2  | ∞  |

---

