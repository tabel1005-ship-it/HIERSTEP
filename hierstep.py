#!/usr/bin/env python3
"""
HIERSTEP - Simulating Emergy and Materials in Hierarchical Steps
Based on Odum, H.T. (2000). Simulating Emergy and Materials in Hierarchical Steps.
Emergy Synthesis I.

Simulates properties of hierarchical steps in steady state; each level is
calculated from the next lower level. Output: numeric table and/or bar graph
on logarithmic scale.
"""

import csv
import math
import os
import argparse
from typing import List, Dict, Any, Optional

# PNG plots are written next to this script, in the Plots subdirectory.
PLOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Plots")


# Default parameters from HIERSTEP.bas (lines 10-360)
DEFAULTS = {
    "S": 1,           # Step size
    "emp": 1e20,      # Empower sej/time of the whole area A
    "M": 1e7,         # Materials in lowest level
    "N": 1000,        # Number of level 1 units and territories
    "Jeo": 1e20,      # Initial energy flow of the whole area
    "eff": 0.1,       # Fraction of energy transformed in each step
    "R": 1.0,         # Initial replacement time
    "Rf": 5.0,        # Factor changing replacement time with level
    "A": 1e9,         # Whole area
    "Ca": 0.05,       # Center fraction of territory area
    "Sf": 0.3,        # Area factor change per step
    "fmc": 2.0,       # Factor changing material/energy coupling with level
    "meo": 1e-13,     # Material coupling to energy flow (initial)
    "Cr": 6,          # Number of centers converging to higher level center
    "me_equation": "linear",  # "linear" (default), "exponential", or "constant" (me unchanged)
    "ens_equation": "multiply",  # "multiply" (Je*R, default) or "divide" (Je/R)
}


def run_simulation(params: Optional[Dict[str, Any]] = None) -> List[Dict[str, float]]:
    """
    Run the hierarchical steps simulation. Returns a list of dicts, one per level,
    each containing L and all computed variables for that level.
    """
    p = {**DEFAULTS, **(params or {})}
    S = p["S"]
    emp = p["emp"]
    M = p["M"]
    N = p["N"]
    Jeo = p["Jeo"]
    eff = p["eff"]
    R = p["R"]
    Rf = p["Rf"]
    A = p["A"]
    Ca = p["Ca"]
    Sf = p["Sf"]
    fmc = p["fmc"]
    meo = p["meo"]
    Cr = p["Cr"]
    me_equation = (p.get("me_equation") or "linear").strip().lower()
    if me_equation not in ("linear", "exponential", "constant"):
        me_equation = "linear"
    ens_equation = (p.get("ens_equation") or "multiply").strip().lower()
    if ens_equation not in ("multiply", "divide"):
        ens_equation = "multiply"

    L = 1
    Je = Jeo
    tr = emp / Je
    at = A / N
    aec = Ca * at
    Jm = meo * Je * (M / A)
    ms = Jm * R
    empg = emp / Jm
    nc = N
    ac = aec * nc
    mc = ms/ac if ac else 0.0
    empd = emp / ac if ac else 0.0
    mfld = Jm / ac
    emter = emp / nc
    ems = emp * R
    me = Jm / Je
    emg = ems / ms if ms else 0.0
    if R:
        ens = Je * R if ens_equation == "multiply" else Je / R
    else:
        ens = 0.0
    ec = ens / ac if ac else 0.0
    emj = ems / ens if ens else 0.0
    efld = Je / ac if ac else 0.0
    ensc = ens / nc if nc else 0.0
    msc = ms / nc if nc else 0.0
    emsc = ems / nc if nc else 0.0
    emc = ems / ac if ac else 0.0

    rows: List[Dict[str, float]] = []
    rows.append({
        "L": L, "at": at, "ac": ac, "aec": aec, "nc": nc,
        "Je": Je, "Jm": Jm, "emp": emp, "tr": tr, "R": R,
        "empd": empd, "empg": empg, "emter": emter, "ems": ems, "emg": emg,
        "ms": ms, "mc": mc, "mfld": mfld, "ens": ens, "ec": ec, "efld": efld, "me": me, "emj": emj,
        "ensc": ensc, "msc": msc, "emsc": emsc, "emc": emc,
    })

    while True:
        L = L + S
        if me_equation == "exponential":
            me = me * (fmc ** S)  # Exponential: multiply by fmc^S each step
        elif me_equation == "linear":
            me = fmc * L * me  # Linear (default): Original BASIC line 507
        # me_equation == "constant": leave me unchanged (me = me)
        Je = Je * eff
        Jm = me * Je
        at = at * Cr
        tr = emp / Je if Je else 0.0
        R = R * Rf
        nc = A / at
        ac = ac * Sf
        aec = ac / nc if nc else 0.0
        empd = emp / ac if ac else 0.0
        empg = emp / Jm if Jm else 0.0
        mfld = Jm / ac if ac else 0.0
        efld = Je / ac if ac else 0.0
        ms = Jm * R
        emter = emp / nc if nc else 0.0
        mc = ms / ac if ac else 0.0
        ems = emp * R
        emg = ems / ms if ms else 0.0
        if R:
            ens = Je * R if ens_equation == "multiply" else Je / R
        else:
            ens = 0.0
        ec = ens / ac if ac else 0.0
        emj = ems / ens
        ensc = ens / nc if nc else 0.0
        msc = ms / nc if nc else 0.0
        emsc = ems / nc if nc else 0.0
        emc = ems / ac if ac else 0.0

        if nc < 1:
            break

        rows.append({
            "L": L, "at": at, "ac": ac, "aec": aec, "nc": nc,
            "Je": Je, "Jm": Jm, "emp": emp, "tr": tr, "R": R,
            "empd": empd, "empg": empg, "emter": emter, "ems": ems, "emg": emg,
            "ms": ms, "mc": mc, "mfld": mfld, "ens": ens, "ec": ec, "efld": efld, "me": me, "emj": emj,
            "ensc": ensc, "msc": msc, "emsc": emsc, "emc": emc,
        })

    return rows


# Variables that can be plotted or printed (name -> description).
# Labels and groupings from "Change labels and groupings.docx".
VARIABLES = {
    "L": "Level, initialized to 1",
    "R": "Replacement time, of center",
    "at": "Area of a territory, at a level",
    "nc": "Number of centers, at a level*",
    "ac": "Area of all centers, at a level*",
    "aec": "Area of ONE center, at a level",
    "Je": "Energy flow",
    "ens": "Energy stored in all centers",
    "ec": "Energy concentrated in all centers^",
    "ensc": "Energy stored in ONE center^",
    "efld": "Energy flow density in centers",
    "Jm": "Mass flow",
    "ms": "Mass stored in all centers",
    "msc": "Mass stored in ONE center^",
    "mc": "Mass concentration in all centers*",
    "mfld": "Mass flow density in all centers*",
    "me": "Mass/energy coupling factor*",
    "emp": "Emergy flow (Empower)",
    "ems": "Emergy stored in all centers",
    "emc": "Emergy concentrated in all centers^",
    "emsc": "Emergy stored in ONE center^",
    "emg": "Emergy per mass stored",
    "emj": "Emergy per energy stored^",
    "empd": "Emergy flow density in all centers (Areal empower density)",
    "emter": "Emergy flow into ONE center (Empower per territory)",
    "tr": "Emergy per energy in flows (Transformity of flows)",
    "empg": "Emergy per mass in flows (Specific emergy of flows)",
}

# Key variables in display order: Space (Scaling) L,R,at,nc,ac,aec; Energy; Materials; Emergy.
KEY_VARIABLES = [
    "L", "R",
    "at", "nc", "ac", "aec",
    "Je", "ens", "ec", "ensc", "efld",
    "Jm", "ms", "msc", "mc", "mfld", "me",
    "emp", "ems", "emc", "emsc", "empd", "emter", "tr", "empg", "emj", "emg",
]

# All GUI/simulation variables with descriptions, except level (L) and replacement time (R),
# in the same order as KEY_VARIABLES (for OOM summary output).
OOM_VARIABLE_KEYS = [k for k in KEY_VARIABLES if k not in ("L", "R")]

# Group headers for GUI: (header text, variable key that follows this header).
GROUP_HEADERS = [
    ("Space (Scaling)", "L"),
    ("Energy", "Je"),
    ("Materials", "Jm"),
    ("Emergy", "emp"),
]


def format_table(rows: List[Dict[str, float]], keys: List[str]) -> str:
    """Return a string with tables for the given variables (for GUI display)."""
    if not rows:
        return ""
    lines = []
    for k in keys:
        if k not in rows[0]:
            continue
        label = VARIABLES.get(k, k)
        lines.append(f"\n{k} ({label})")
        lines.append("-" * 44)
        for r in rows:
            lines.append(f"  L={r['L']:.0f}: {r[k]:.6g}")
    return "\n".join(lines) if lines else ""


def format_oom_table(rows: List[Dict[str, float]]) -> str:
    """
    Two-column text for the GUI: variable name with descriptor, and order-of-magnitude
    difference log10(B/A), where A is the value at the first simulated level and B at the last.
    Undefined (nonpositive ratio) shown as n/a.
    """
    if not rows:
        return ""
    first = rows[0]
    last = rows[-1]
    name_w = 72
    lines = [
        "Log ratio = log10(B/A); A = first level, B = last level.",
        "",
        f"{'Variable Name':<{name_w}}Order of Magnitude Difference",
        f"{'-' * 42:<{name_w}}{'-' * 38}",
    ]
    for k in OOM_VARIABLE_KEYS:
        if k not in first:
            continue
        desc = VARIABLES.get(k, k)
        name_col = f"{k} – {desc}"
        if len(name_col) > name_w:
            name_col = name_col[: name_w - 3] + "..."
        a = first[k]
        b = last[k]
        if a != 0:
            ratio = b / a
            if ratio > 0:
                val = round(math.log10(ratio), 2)
                oom_str = f"{val:.2f}"
            else:
                oom_str = "n/a"
        else:
            oom_str = "n/a"
        lines.append(f"{name_col:<{name_w}}{oom_str}")
    return "\n".join(lines)


def csv_export_heading(key: str) -> str:
    """Human-readable label for CSV columns/rows: ``code – description``, trimming redundant phrases for selected keys."""
    desc = VARIABLES.get(key, key)
    if key in ("at", "nc", "ac", "aec"):
        desc = desc.replace(", at a level", "")
    return f"{key} – {desc}"


def write_csv_export(
    path: str,
    rows: List[Dict[str, float]],
    print_keys: List[str],
    include_oom: bool,
) -> None:
    """
    Write UTF-8 CSV (with BOM for Excel) from current Print selection (level table) and/or OOM block.
    Does not change GUI Output text; mirrors what Print / OOM would include when those options are on.
    """
    if not rows:
        raise ValueError("No simulation rows to export.")
    print_keys = [k for k in print_keys if k in rows[0]]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if print_keys:
            header = ["L"] + [csv_export_heading(k) for k in print_keys]
            w.writerow(header)
            for r in rows:
                w.writerow([r["L"]] + [r[k] for k in print_keys])

        if include_oom:
            first = rows[0]
            last = rows[-1]
            if print_keys:
                w.writerow([])
            w.writerow(["Variable Name", "Order of Magnitude Difference"])
            for k in OOM_VARIABLE_KEYS:
                if k not in first:
                    continue
                label = csv_export_heading(k)
                a = first[k]
                b = last[k]
                if a != 0:
                    ratio = b / a
                    if ratio > 0:
                        val = round(math.log10(ratio), 2)
                        oom_cell = f"{val:.2f}"
                    else:
                        oom_cell = "n/a"
                else:
                    oom_cell = "n/a"
                w.writerow([label, oom_cell])


def print_table(rows: List[Dict[str, float]], var: str) -> None:
    """Print levels and one variable (or 'all' for key variables)."""
    if var == "all":
        keys = KEY_VARIABLES.copy()
    else:
        keys = [var]
    if not rows:
        return
    print(format_table(rows, keys))


def plot_variable(rows: List[Dict[str, float]], var: str, log_scale: bool = True, out_dir: Optional[str] = None) -> str:
    """Bar graph of one variable vs level. Returns path to saved file."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("Agg")
    except ImportError:
        raise RuntimeError("Matplotlib not installed. Install with: pip install matplotlib")

    if var not in rows[0]:
        raise ValueError(f"Unknown variable: {var}")

    levels = [r["L"] for r in rows]
    values = [r[var] for r in rows]

    fig, ax = plt.subplots()
    x_pos = list(range(len(levels)))
    bars = ax.bar(x_pos, values, color="steelblue", edgecolor="navy", alpha=0.8)
    # Show final value above each bar (compact format, e.g. 1e+20)
    ax.bar_label(bars, labels=[f"{v:.3g}" for v in values], padding=2, fontsize=10)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(int(L)) for L in levels])
    ax.set_xlabel("Hierarchical level")
    ax.set_ylabel(VARIABLES.get(var, var))
    ax.set_title(f"{var}: {VARIABLES.get(var, var)}")
    if log_scale and all(v > 0 for v in values):
        ax.set_yscale("log")
    plt.tight_layout()
    dest = PLOTS_DIR if out_dir is None else out_dir
    os.makedirs(dest, exist_ok=True)
    out = os.path.join(dest, f"hierstep_{var}.png")
    plt.savefig(out, dpi=150)
    plt.close()
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HIERSTEP: Simulating Emergy and Materials in Hierarchical Steps"
    )
    parser.add_argument(
        "--plot",
        metavar="VAR",
        default=None,
        help=f"Variable to plot (bar chart). One of: {', '.join(VARIABLES.keys())}",
    )
    parser.add_argument(
        "--print",
        metavar="VAR",
        default=None,
        dest="print_var",
        help="Variable to print (or 'all' for key variables)",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Use linear Y axis for plot (default: log)",
    )
    args = parser.parse_args()

    rows = run_simulation()
    print(f"Simulation: {len(rows)} levels (nc >= 1).")

    if args.print_var:
        print_table(rows, args.print_var)

    if args.plot:
        path = plot_variable(rows, args.plot, log_scale=not args.no_log)
        print(f"Saved plot to {path}")
    elif not args.print_var:
        print_table(rows, "tr")
        path = plot_variable(rows, "tr", log_scale=True)
        print(f"Saved plot to {path}")


if __name__ == "__main__":
    main()
