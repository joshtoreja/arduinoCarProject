import json, argparse, heapq
from collections import defaultdict

DIRS = [(0,1,"U"), (1,0,"R"), (0,-1,"D"), (-1,0,"L")]

def load_grid(path):
    with open(path, "r") as f:
        data = json.load(f)
    n = data["axis_max"] + 1 if "axis_max" in data else data["grid_size"]
    points = data.get("points", [])
    wblob = data.get("weights", None)
    w = defaultdict(lambda: 1)
    if wblob and "cells" in wblob:
        for c in wblob["cells"]:
            w[(int(c["x"]), int(c["y"]))] = int(c["w"])
    return n, points, w

def collect_color_points(points, color):
    return [(p["x"], p["y"]) for p in points if p["color"].upper() == color.upper()]

def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
def in_bounds(x, y, n): return 0 <= x < n and 0 <= y < n

def dijkstra_weighted(n, start, goal, weight_fn, verbose=True):
    INF = 10**12
    dist = defaultdict(lambda: INF)
    prev = {}
    dist[start] = 0
    pq = [(0, start)]
    logs = []
    step = 0
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]: continue
        step += 1
        if u == goal: break
        ux, uy = u
        for dx, dy, _ in DIRS:
            v = (ux + dx, uy + dy)
            if not in_bounds(v[0], v[1], n): continue
            nd = d + weight_fn(v)
            if nd < dist[v]:
                dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    if dist[goal] >= INF: return dist, prev, None, logs
    path = []; cur = goal
    while cur != start: path.append(cur); cur = prev[cur]
    path.append(start); path.reverse()
    return dist, prev, path, logs

def parse_xy(s):
    x,y = s.split(",")
    return (int(x), int(y))

def path_to_moves(path):
    moves = []
    for i in range(1, len(path)):
        (x0,y0),(x1,y1) = path[i-1], path[i]
        dx,dy = x1-x0, y1-y0
        if (dx,dy)==(0,1): moves.append("U")
        elif (dx,dy)==(1,0): moves.append("R")
        elif (dx,dy)==(0,-1): moves.append("D")
        elif (dx,dy)==(-1,0): moves.append("L")
        else: raise ValueError("non-unit step")
    return moves

def condense_moves(m):
    if not m: return []
    out=[]; cur=m[0]; c=1
    for x in m[1:]:
        if x==cur: c+=1
        else: out.append((cur,c)); cur=x; c=1
    out.append((cur,c)); return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", required=True)
    ap.add_argument("--color", default="R", choices=["R","G","B"])
    ap.add_argument("--start", type=parse_xy, default=None)
    ap.add_argument("--goal",  type=parse_xy, default=None)
    ap.add_argument("--save-path", default=None)
    ap.add_argument("--save-moves", default=None)
    ap.add_argument("--moves-list", action="store_true")
    ap.add_argument("--save-moves-txt", default=None)
    a = ap.parse_args()

    n, points, weights = load_grid(a.grid)
    start = a.start if a.start else (0,0)
    if a.goal: goal = a.goal
    else:
        cand = [p for p in collect_color_points(points, a.color) if p != start]
        if not cand: raise SystemExit("no goal candidate")
        goal = min(cand, key=lambda p: manhattan(start,p))

    dist, prev, path, logs = dijkstra_weighted(n, start, goal, lambda xy: weights[xy], verbose=False)
    if path is None: raise SystemExit("no path")

    if a.save_path:
        with open(a.save_path,"w") as f: json.dump({"path": [[x,y] for (x,y) in path]}, f, indent=2)
    moves = path_to_moves(path)
    if a.save_moves:
        out = {"moves": moves} if a.moves_list else {"moves": "".join(moves)}
        with open(a.save_moves,"w") as f: json.dump(out, f, indent=2)
    if a.save_moves_txt:
        cm = [f"{d}{n}" for (d,n) in condense_moves(moves)]
        with open(a.save_moves_txt,"w") as f:
            f.write("S\n"); [f.write(c+"\n") for c in cm]; f.write("E\n")

if __name__ == "__main__":
    main()
