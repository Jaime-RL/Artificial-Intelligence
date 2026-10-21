# Artificial Intelligence Algorithms

Classic AI techniques implemented from scratch in Python: **informed and uninformed search**, **constraint satisfaction**, **metaheuristics**, **adversarial search** and a **neural network trained with backpropagation** — no ML frameworks.

## Contents

| Folder | File | Technique | Problem |
|---|---|---|---|
| `search/` | `pathfinding_gbfs_astar.py` | Greedy Best-First Search, **A\*** | Shortest route between Spanish cities using a straight-line-distance heuristic |
| `search/` | `knapsack_bfs_dfs.py` | Breadth-first & depth-first tree search | 0/1 knapsack (exhaustive search for the optimal selection) |
| `csp/` | `sudoku_backtracking.py` | Backtracking + inference (constraint propagation) | Sudoku solver |
| `metaheuristics/` | `tsp_genetic_ant_colony.py` | **Genetic algorithm** & **Ant Colony Optimization** | Travelling Salesman Problem (`berlin52`) with convergence plots |
| `games/` | `mancala_minimax_client.py` | **Minimax** with heuristic evaluation | Mancala bot that plays against other bots through a socket game server |
| `neural_network/` | `neural_network_scratch.py` | Feed-forward NN, sigmoid, backpropagation (NumPy) | Handwritten digit classification (784 → hidden → 10), train/val/test split |

## Running

```bash
pip install -r requirements.txt

cd search
python pathfinding_gbfs_astar.py   # sample map included
python knapsack_bfs_dfs.py         # sample instance included
```

Other scripts expect their input file in the working directory:

| Script | Input |
|---|---|
| `sudoku_backtracking.py` | `sudoku.txt` (one or more 9×9 puzzles) |
| `tsp_genetic_ant_colony.py` | `berlin52.tsp` from [TSPLIB](http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/) |
| `neural_network_scratch.py` | CSV with the label in the first column followed by 784 pixel values (0–255) |
| `mancala_minimax_client.py` | A running Mancala game server on `127.0.0.1:30000` (provided by the course) |

## Tech

Python 3 · NumPy · pandas · Matplotlib

*Coursework from the Artificial Intelligence course (DVA340) at Mälardalen University, Sweden.*
