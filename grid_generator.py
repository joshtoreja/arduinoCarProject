import json, random, argparse
import matplotlib.pyplot as plt

def generate_weights(max_coord, kind, wmin, wmax, seed=None):
    rnd = random.Random(seed + 1337) if seed is not None else random
    n = max_coord + 1
    cells = []
    if kind == "none":
        for x in range(n):
            for y in range(n):
                cells.append({"x": x, "y": y, "w": 1})
    elif kind == "random":
        for x in range(n):
            for y in range(n):
                cells.append({"x": x, "y": y, "w": rnd.randint(wmin, wmax)})
    elif kind == "checker":
        for x in range(n):
            for y in range(n):
                cells.append({"x": x, "y": y, "w": (wmin if (x+y)%2==0 else wmax)})
    else:
        raise ValueError("unknown weight kind")
    return {"kind": kind, "wmin": wmin, "wmax": wmax, "cells": cells}

def generate_grid(max_coord=10, k_per_color=10, seed=None,
                  out_json="grid.json", out_png="grid.png",
                  weighted="none", wmin=1, wmax=1):
    if seed is not None:
        random.seed(seed)
    n = max_coord + 1
    all_cells = [(x, y) for x in range(n) for y in range(n)]
    available = [(x, y) for (x, y) in all_cells if (x, y) != (0, 0)]
    random.shuffle(available)
    points = [{"x":0,"y":0,"color":c} for c in ("R","G","B")]
    remaining = {c: max(0, k_per_color-1) for c in ("R","G","B")}
    total = sum(remaining.values())
    if total > len(available):
        raise ValueError("not enough cells")
    for c in ("R","G","B"):
        for _ in range(remaining[c]):
            x,y = available.pop()
            points.append({"x":x,"y":y,"color":c})
    weights = generate_weights(max_coord, weighted, wmin, wmax, seed=seed)
    data = {"axis_min":0, "axis_max":max_coord, "points":points, "weights":weights}
    with open(out_json,"w") as f: json.dump(data,f,indent=2)

    fig, ax = plt.subplots()
    ax.set_xlim(-0.5, max_coord + 0.5); ax.set_ylim(-0.5, max_coord + 0.5); ax.set_aspect("equal")
    ax.set_xticks(range(0, max_coord + 1)); ax.set_yticks(range(0, max_coord + 1)); ax.grid(True, linewidth=0.75)
    cmap = {"R":"red","G":"green","B":"blue"}
    for p in points:
      ax.plot(p["x"], p["y"], "o", markersize=10, color=cmap[p["color"]])
    ax.set_title(f"Grid 0..{max_coord}, k={k_per_color}, weights={weighted}")
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.show()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--json", default="grid.json")
    ap.add_argument("--png", default="grid.png")
    ap.add_argument("--weighted", choices=["none","random","checker"], default="none")
    ap.add_argument("--wmin", type=int, default=1)
    ap.add_argument("--wmax", type=int, default=4)
    a = ap.parse_args()
    generate_grid(a.max, a.k, a.seed, a.json, a.png, a.weighted, a.wmin, a.wmax)

if __name__ == "__main__":
    main()
