# grid_gen.py
# 11x11 grid with coordinates 0..10 inclusive.
# Places 10 points each of R, G, B (30 total), with (0,0) guaranteed
# to exist for ALL three colors. Saves JSON + PNG and shows a Matplotlib plot.

import json, random, argparse
import matplotlib.pyplot as plt  # pip install matplotlib

def generate_grid(max_coord=10, k_per_color=10, seed=None,
                  out_json="grid.json", out_png="grid.png"):
    """
    max_coord=10 -> coordinates 0..10 inclusive => (max_coord+1)^2 cells
    k_per_color=10 -> 10 points for each of R, G, B
    (0,0) is included ONCE per color (same coordinate, different colors).
    """
    if seed is not None:
        random.seed(seed)

    n = max_coord + 1  # number of discrete positions along each axis
    all_cells = [(x, y) for x in range(n) for y in range(n)]

    # Reserve (0,0) for all three colors; do NOT use it for remaining random picks
    available = [(x, y) for (x, y) in all_cells if (x, y) != (0, 0)]
    random.shuffle(available)

    # Start with origin for each color
    points = [
        {"x": 0, "y": 0, "color": "R"},
        {"x": 0, "y": 0, "color": "G"},
        {"x": 0, "y": 0, "color": "B"},
    ]

    # Add remaining random points for each color
    remaining = {
        "R": max(0, k_per_color - 1),
        "G": max(0, k_per_color - 1),
        "B": max(0, k_per_color - 1),
    }
    total_needed = sum(remaining.values())
    if total_needed > len(available):
        raise ValueError(f"Need {total_needed} unique cells (excluding origin), but only {len(available)} available.")

    for color in ["R", "G", "B"]:
        for _ in range(remaining[color]):
            x, y = available.pop()
            points.append({"x": x, "y": y, "color": color})

    data = {"axis_min": 0, "axis_max": max_coord, "points": points}

    # Write JSON
    with open(out_json, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {out_json} with {len(points)} colored points (R={k_per_color}, G={k_per_color}, B={k_per_color}).")

    # Plot
    fig, ax = plt.subplots()
    ax.set_xlim(-0.5, max_coord + 0.5)
    ax.set_ylim(-0.5, max_coord + 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(0, max_coord + 1))
    ax.set_yticks(range(0, max_coord + 1))
    ax.grid(True, linewidth=0.75)

    color_map = {"R": "red", "G": "green", "B": "blue"}
    for p in points:
        ax.plot(p["x"], p["y"], "o", markersize=10, color=color_map[p["color"]])
        # Slight label offset
        ax.text(p["x"] + 0.15, p["y"] + 0.15, p["color"], fontsize=9, fontweight="bold")

    ax.set_title(f"Grid 0..{max_coord} with {k_per_color} each of R/G/B (origin has R,G,B)")
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"Wrote {out_png}")

    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Generate a colored grid (0..10) with origin R/G/B.")
    parser.add_argument("--max", type=int, default=10, help="Maximum coordinate (inclusive). Default 10.")
    parser.add_argument("--k", type=int, default=10, help="Points per color. Default 10.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument("--json", default="grid.json", help="Output JSON filename.")
    parser.add_argument("--png", default="grid.png", help="Output PNG filename.")
    args = parser.parse_args()

    generate_grid(max_coord=args.max, k_per_color=args.k, seed=args.seed,
                  out_json=args.json, out_png=args.png)

if __name__ == "__main__":
    main()
