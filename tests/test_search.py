"""Tests for the search algorithms in search/ (knapsack BFS/DFS and A* route finding)."""
import heapq
import itertools
import random
import sys
from pathlib import Path

import pytest

SEARCH_DIR = Path(__file__).resolve().parents[1] / "search"
sys.path.insert(0, str(SEARCH_DIR))
import knapsack_bfs_dfs as ks  # noqa: E402
import pathfinding_gbfs_astar as pf  # noqa: E402


# ---------------------------------------------------------------- knapsack

def brute_force_knapsack(capacity, weights, profits):
    best = 0
    for choice in itertools.product([0, 1], repeat=len(weights)):
        w = sum(c * wi for c, wi in zip(choice, weights))
        if w <= capacity:
            best = max(best, sum(c * p for c, p in zip(choice, profits)))
    return best


def check_selection(selection, capacity, weights, profits, expected_profit):
    assert sum(c * w for c, w in zip(selection, weights)) <= capacity
    assert sum(c * p for c, p in zip(selection, profits)) == expected_profit


@pytest.mark.parametrize("search", [ks.BFS, ks.DFS])
def test_knapsack_sample_file(search):
    capacity, n, weights, profits, _ = ks.read_knapsack_file(SEARCH_DIR / "knapsack.txt")
    profit, selection = search(capacity, n, weights, profits)
    assert profit == brute_force_knapsack(capacity, weights, profits)
    check_selection(selection, capacity, weights, profits, profit)


@pytest.mark.parametrize("seed", range(10))
def test_knapsack_random_instances(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 10)
    weights = [rng.randint(1, 15) for _ in range(n)]
    profits = [rng.randint(1, 50) for _ in range(n)]
    capacity = rng.randint(5, 40)

    expected = brute_force_knapsack(capacity, weights, profits)
    for search in (ks.BFS, ks.DFS):
        profit, selection = search(capacity, n, weights, profits)
        assert profit == expected
        if profit:
            check_selection(selection, capacity, weights, profits, profit)


# ---------------------------------------------------------------- A*

def dijkstra_cost(graph, start, goal):
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if node == goal:
            return d
        if d > dist[node]:
            continue
        for nxt, w in graph[node].items():
            if d + w < dist.get(nxt, float("inf")):
                dist[nxt] = d + w
                heapq.heappush(heap, (d + w, nxt))
    return float("inf")


@pytest.fixture
def road_map(monkeypatch):
    # The search functions read the module-level `graph` and `distances`.
    graph, distances = pf.read_pathfinding_file(SEARCH_DIR / "pathfinding.txt")
    monkeypatch.setattr(pf, "graph", graph, raising=False)
    monkeypatch.setattr(pf, "distances", distances, raising=False)
    return graph


def path_cost(graph, path):
    return sum(graph[a][b] for a, b in zip(path, path[1:]))


def test_a_star_finds_optimal_route(road_map):
    path = pf.A_star("Malaga", "Valladolid")
    assert path[0] == "Malaga" and path[-1] == "Valladolid"
    assert all(b in road_map[a] for a, b in zip(path, path[1:]))
    assert path_cost(road_map, path) == dijkstra_cost(road_map, "Malaga", "Valladolid")


def test_gbfs_reaches_goal(road_map):
    expanded = pf.GBFS("Malaga", "Valladolid")
    assert expanded[0] == "Malaga" and expanded[-1] == "Valladolid"
