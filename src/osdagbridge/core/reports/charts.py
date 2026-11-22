"""
charts.py -- matplotlib charts embedded in the design report.

* ur_charts_tex(checks, chart_dir)        -> LaTeX for the Section 5.5 charts
* quantity_charts_tex(input_dict, chart_dir) -> LaTeX for the Chapter 7 charts

Charts are drawn with the object-oriented Figure/Agg API (not pyplot), so they
are safe to create from the report worker thread and never open a GUI window.
Every size, font and colour comes from styles.py. Each function returns an
empty string when there is no usable data or no chart folder, so the report is
simply built without the chart instead of failing.
"""

import os
import re

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from osdagbridge.core.reports import styles
from osdagbridge.core.reports.report_utils import _fig_embed


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _to_float(value):
    """'41.12' -> 41.12, '\\textcolor{red}{1.84}' -> 1.84, 'N.A.' / '---' -> None."""
    if value is None:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _new_figure(height=None):
    fig = Figure(figsize=(styles.CHART_WIDTH_IN, height or styles.CHART_HEIGHT_IN),
                 dpi=styles.CHART_DPI)
    FigureCanvasAgg(fig)
    return fig


def _style_axes(ax):
    ax.tick_params(labelsize=styles.CHART_FONT_SIZE)
    ax.yaxis.grid(True, alpha=0.35, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def _label_bars(ax, bars, values):
    for bar, value in zip(bars, values):
        ax.annotate("{:.2f}".format(value),
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 2), textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=styles.CHART_VALUE_LABEL_SIZE,
                    bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"))


def _draw_limit_line(ax):
    ax.axhline(styles.UR_LIMIT, color=styles.CHART_COLOR_LIMIT,
               linestyle=styles.CHART_LIMIT_STYLE,
               linewidth=styles.CHART_LIMIT_WIDTH,
               label="UR = {:.1f} limit".format(styles.UR_LIMIT))


def _save(fig, chart_dir, name):
    os.makedirs(chart_dir, exist_ok=True)
    path = os.path.join(chart_dir, name)
    fig.tight_layout()
    fig.savefig(path, dpi=styles.CHART_DPI)
    return path.replace("\\", "/")


def _figure_tex(path, caption):
    return "\n\\vspace{1em}\n" + _fig_embed(path, caption,
                                            width=styles.CHART_EMBED_WIDTH)


# ---------------------------------------------------------------------------
# Utilization ratio charts (Section 5.5)
# ---------------------------------------------------------------------------
UR_ELEMENT_ORDER = ["Steel Plate Girders", "Concrete Deck Slab",
                    "Cross Bracing", "End Diaphragms"]


def classify_ur_element(label):
    """Map a row label of the overall summary table to a primary element."""
    text = str(label).lower()
    if text.startswith("girder"):
        return "Steel Plate Girders"
    if text.startswith("deck") or "(slab)" in text:
        return "Concrete Deck Slab"
    if text.startswith("cross bracing"):
        return "Cross Bracing"
    if text.startswith("end diaphragm"):
        return "End Diaphragms"
    return None


def _ur_governing_png(checks, chart_dir):
    worst = {}
    for label, ur in checks:
        element, ur = classify_ur_element(label), _to_float(ur)
        if element is not None and ur is not None:
            worst[element] = max(ur, worst.get(element, 0.0))
    names = [e for e in UR_ELEMENT_ORDER if e in worst]
    if not names:
        return None
    values = [worst[n] for n in names]
    colors = [styles.CHART_COLOR_FAIL if v > styles.UR_LIMIT else styles.CHART_COLOR_PASS
              for v in values]
    fig = _new_figure()
    ax = fig.add_subplot(111)
    bars = ax.bar(names, values, color=colors, width=0.55)
    _draw_limit_line(ax)
    _label_bars(ax, bars, values)
    ax.set_ylabel("Utilization Ratio (Demand / Capacity)", fontsize=styles.CHART_FONT_SIZE)
    ax.set_title("Governing Utilization Ratio by Element", fontsize=styles.CHART_TITLE_SIZE)
    ax.set_ylim(0, max(1.15, max(values) * 1.18))
    ax.legend(fontsize=styles.CHART_FONT_SIZE, loc="upper right", frameon=False)
    _style_axes(ax)
    return _save(fig, chart_dir, "ur_governing.png")


def _ur_all_checks_png(checks, chart_dir):
    rows = []
    for label, ur in checks:
        if classify_ur_element(label) is not None and _to_float(ur) is not None:
            rows.append((label, _to_float(ur)))
    if not rows:
        return None
    labels = [re.sub(r"\s*---\s*", " - ", r[0]) for r in rows]
    values = [r[1] for r in rows]
    colors = [styles.CHART_COLOR_FAIL if v > styles.UR_LIMIT else styles.CHART_COLOR_PASS
              for v in values]
    fig = _new_figure(height=styles.CHART_HEIGHT_IN + 1.2)
    ax = fig.add_subplot(111)
    bars = ax.bar(range(len(values)), values, color=colors, width=0.65)
    _draw_limit_line(ax)
    _label_bars(ax, bars, values)
    ax.set_xticks(range(len(values)))
    ax.set_xticklabels(labels, rotation=55, ha="right",
                       fontsize=styles.CHART_FONT_SIZE - 1)
    ax.set_ylabel("Utilization Ratio", fontsize=styles.CHART_FONT_SIZE)
    ax.set_title("Utilization Ratio of Each Design Check", fontsize=styles.CHART_TITLE_SIZE)
    ax.set_ylim(0, max(1.15, max(values) * 1.18))
    ax.legend(fontsize=styles.CHART_FONT_SIZE, loc="upper right", frameon=False)
    _style_axes(ax)
    return _save(fig, chart_dir, "ur_all_checks.png")


def ur_charts_tex(checks, chart_dir):
    """LaTeX for the utilization ratio charts of Section 5.5.

    checks -- list of (row label, UR text) read from the overall summary table.
    """
    if not chart_dir:
        return ""
    parts = ""
    gov = _ur_governing_png(checks, chart_dir)
    if gov:
        parts += _figure_tex(gov, "Figure 5.1: Governing utilization ratio of each "
                                  "primary element (UR = Demand / Capacity)")
    every = _ur_all_checks_png(checks, chart_dir)
    if every:
        parts += _figure_tex(every, "Figure 5.2: Utilization ratio of every design check")
    return parts


# ---------------------------------------------------------------------------
# Material quantity charts (Chapter 7)
# ---------------------------------------------------------------------------
def _steel_png(input_dict, chart_dir):
    girders = _to_float(input_dict.get("steel_girders_wt_total"))
    parts = [_to_float(input_dict.get(k)) for k in
             ("bracing_top_wt_total", "bracing_bot_wt_total", "bracing_diag_wt_total")]
    bracing = sum(p for p in parts if p is not None) if any(p is not None for p in parts) else None
    diaphragm = _to_float(input_dict.get("end_diaphragm_wt_total"))
    items = [(n, v) for n, v in (("Girders", girders), ("Cross Bracing", bracing),
                                 ("End Diaphragms", diaphragm)) if v is not None]
    if not items:
        return None
    names, values = [n for n, _ in items], [v for _, v in items]
    fig = _new_figure()
    ax = fig.add_subplot(111)
    bars = ax.bar(names, values, color=styles.CHART_COLOR_SECOND, width=0.5)
    _label_bars(ax, bars, values)
    ax.set_ylabel("Weight (MT)", fontsize=styles.CHART_FONT_SIZE)
    ax.set_title("Structural Steel Quantity", fontsize=styles.CHART_TITLE_SIZE)
    ax.set_ylim(0, max(values) * 1.18)
    _style_axes(ax)
    return _save(fig, chart_dir, "qty_steel.png")


def _concrete_rebar_png(input_dict, chart_dir):
    concrete = _to_float(input_dict.get("concrete_deck_vol_total"))
    rebar = _to_float(input_dict.get("rebar_deck_wt_total"))
    if concrete is None and rebar is None:
        return None
    fig = _new_figure()
    for position, value, label, unit, color in (
            (121, concrete, "Concrete (deck slab)", "Volume (m$^3$)", styles.CHART_COLOR_THIRD),
            (122, rebar, "Reinforcement steel", "Weight (MT)", styles.CHART_COLOR_SECOND)):
        ax = fig.add_subplot(position)
        if value is None:
            ax.text(0.5, 0.5, "N.A.", ha="center", va="center", transform=ax.transAxes,
                    fontsize=styles.CHART_FONT_SIZE)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            bars = ax.bar([label], [value], color=color, width=0.45)
            ax.set_xlim(-0.9, 0.9)
            _label_bars(ax, bars, [value])
            ax.set_ylim(0, value * 1.2 if value > 0 else 1)
            _style_axes(ax)
        ax.set_ylabel(unit, fontsize=styles.CHART_FONT_SIZE)
    fig.suptitle("Concrete Volume and Reinforcement Steel Weight",
                 fontsize=styles.CHART_TITLE_SIZE)
    return _save(fig, chart_dir, "qty_concrete_rebar.png")


def quantity_charts_tex(input_dict, chart_dir):
    """LaTeX for the Chapter 7 material quantity charts."""
    if not chart_dir:
        return ""
    parts = ""
    steel = _steel_png(input_dict, chart_dir)
    if steel:
        parts += _figure_tex(steel, "Figure 7.1: Structural steel quantity (MT)")
    concrete = _concrete_rebar_png(input_dict, chart_dir)
    if concrete:
        parts += _figure_tex(concrete, "Figure 7.2: Concrete volume (m$^3$) and "
                                       "reinforcement steel weight (MT)")
    return parts
