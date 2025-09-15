# dijkstra_print.py
# Reads a grid JSON (from grid_gen.py), ALWAYS starts at (0,0),
# chooses the CLOSEST other node of the chosen color as goal,
# runs Dijkstra on a 4-neighbor grid, and prints logs + final path.

import json, argparse, heapq
from collections import defaultdict

DIRS = [(0,1,"N"), (1,0,"E"), (0,-1,"S"), (-1,0,"W")]  # 4-neighbors (Manhattan)

def load_grid(path):
    with open(path, "r") as f:
        data = json.load(f)
    # Support both formats (axis_max or grid_size)
    if "axis_max" in data:
        n = data["axis_max"] + 1
    else:
        n = data["grid_size"]
    points = data["points"]
    return n, points

def collect_color_points(points, color):
    return [(p["x"], p["y"]) for p in points if p["color"].upper() == color.upper()]

def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def in_bounds(x, y, n): return 0 <= x < n and 0 <= y < n

def dijkstra_with_logs(n, start, goal, verbose=True):
    INF = 10**9
    dist = defaultdict(lambda: INF)
    prev = {}
    dist[start] = 0
    pq = [(0, start)]
    logs = []
    step = 0

    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue  # stale
        step += 1
        if verbose:
            logs.append(f"[POP {step}] node={u} dist={d}")
        if u == goal:
            if verbose:
                logs.append(f"Reached goal {goal} with dist {d}.")
            break
        ux, uy = u
        for dx, dy, _ in DIRS:
            v = (ux + dx, uy + dy)
            if not in_bounds(v[0], v[1], n):
                continue
            nd = d + 1  # uniform cost
            if nd < dist[v]:
                old = dist[v]
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
                if verbose:
                    logs.append(f"  [RELAX] {u} -> {v}: dist {old} -> {nd}")

    # Reconstruct path
    if dist[goal] >= 10**9:
        path = None
    else:
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = prev[cur]
        path.append(start)
        path.reverse()

    return dist, prev, path, logs

def summarize_dist(dist, n, sample=10):
    reachable = [(xy, d) for xy, d in dist.items() if d < 10**9]
    reachable.sort(key=lambda t: (t[1], t[0]))
    lines = [f"Reachable nodes: {len(reachable)} / {n*n}"]
    for (xy, d) in reachable[:sample]:
        lines.append(f"  {xy}: {d}")
    if len(reachable) > sample:
        lines.append("  ...")
    return "\n".join(lines)

def parse_xy(s):
    parts = s.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Coordinate must be x,y")
    try:
        return (int(parts[0]), int(parts[1]))
    except:
        raise argparse.ArgumentTypeError("Coordinate must be integers like 3,7")

def main():
    ap = argparse.ArgumentParser(description="Run Dijkstra from origin to closest same-color node and print steps.")
    ap.add_argument("--grid", required=True, help="Path to grid JSON (from grid_gen.py)")
    ap.add_argument("--color", default="R", choices=["R","G","B"], help="Color to connect from origin")
    ap.add_argument("--quiet", action="store_true", help="Suppress per-step logs (only summary + path)")
    # Optional overrides if you ever need them:
    ap.add_argument("--start", type=parse_xy, default=None, help="Override start x,y (default 0,0)")
    ap.add_argument("--goal",  type=parse_xy, default=None, help="Override goal x,y (otherwise picks closest of color)")
    args = ap.parse_args()

    n, points = load_grid(args.grid)

    # Start at origin unless explicitly overridden
    start = args.start if args.start is not None else (0, 0)

    # Choose goal:
    if args.goal is not None:
        goal = args.goal
    else:
        color_pts = collect_color_points(points, args.color)
        if not color_pts:
            raise SystemExit(f"No points of color {args.color} found in {args.grid}.")
        # Exclude start itself so we go to another node of that color
        candidates = [p for p in color_pts if p != start]
        if not candidates:
            raise SystemExit(f"Only {start} exists for color {args.color}; no other node to route to.")
        goal = min(candidates, key=lambda p: manhattan(start, p))

    print(f"Grid size: {n}×{n}")
    print(f"Color: {args.color}")
    print(f"Start: {start}  Goal: {goal}\n")

    dist, prev, path, logs = dijkstra_with_logs(n, start, goal, verbose=not args.quiet)

    if not args.quiet:
        print("=== Dijkstra logs ===")
        for line in logs:
            print(line)
        print()

    if path is None:
        print("No path found (unexpected on empty 4-neighbor grid).")
        return

    print("=== Distance summary (sample) ===")
    print(summarize_dist(dist, n))
    print()

    length = len(path) - 1
    print(f"=== Shortest path ({length} steps) ===")
    print(" -> ".join(str(p) for p in path))

if __name__ == "__main__":
    main()
