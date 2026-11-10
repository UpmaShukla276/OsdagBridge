"""
styles.py -- single source of truth for report formatting.

Every layout number, colour and spacing rule used by the LaTeX report lives
here. Chapter files and report_generator.py import from this module and never
hardcode formatting values themselves. To restyle the whole report, edit the
constants below; nothing else needs to change.
"""

# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
FONT_SIZE_PT = 12          # base font size of the document
PAPER = "a4paper"          # paper size
MARGIN_IN = 1              # page margin on all four sides (inches)
LINE_STRETCH = 1.15        # line spacing multiplier (\setstretch)

# ---------------------------------------------------------------------------
# Colours (hex values without '#')
# ---------------------------------------------------------------------------
COLOR_OSDAG_GREEN = "91B014"   # brand colour: rules, footer text, accents

# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
TABLE_TABCOLSEP_PT = 6         # horizontal cell padding
TABLE_ARRAYSTRETCH = 1.12      # row height multiplier
TABLE_EXTRA_ROW_HEIGHT_PT = 0.6
TABLE_RULE_WIDTH_PT = 0.5      # border line thickness
LONGTABLE_SPACE_BEFORE_PT = 0  # gap above a longtable (\LTpre)
LONGTABLE_SPACE_AFTER_PT = 6   # gap below a longtable (\LTpost)

# A table or longtable starts on a new page if fewer than this many text
# lines remain on the current page. This keeps a table's first rows together.
NEEDSPACE_BASELINES = 5


# ---------------------------------------------------------------------------
# LaTeX fragments built from the constants above
# ---------------------------------------------------------------------------
def documentclass_tex():
    return r"\documentclass[" + f"{FONT_SIZE_PT}pt,{PAPER}" + r"]{report}"


def geometry_tex():
    return r"\usepackage[" + f"{PAPER}, margin={MARGIN_IN}in" + r"]{geometry}"


def table_layout_tex():
    """Cell padding, row height, rule thickness and page-break guard."""
    return "\n".join([
        r"\setlength{\tabcolsep}{" + f"{TABLE_TABCOLSEP_PT}pt" + r"}",
        r"\renewcommand{\arraystretch}{" + f"{TABLE_ARRAYSTRETCH}" + r"}",
        r"\setlength{\LTpre}{" + f"{LONGTABLE_SPACE_BEFORE_PT}pt" + r"}",
        r"\setlength{\LTpost}{" + f"{LONGTABLE_SPACE_AFTER_PT}pt" + r"}",
        r"\setlength{\arrayrulewidth}{" + f"{TABLE_RULE_WIDTH_PT}pt" + r"}",
        r"\setlength{\extrarowheight}{" + f"{TABLE_EXTRA_ROW_HEIGHT_PT}pt" + r"}",
    ])


def needspace_tex():
    guard = r"{\needspace{" + f"{NEEDSPACE_BASELINES}" + r"\baselineskip}}"
    return "\n".join([
        r"\BeforeBeginEnvironment{table}" + guard,
        r"\BeforeBeginEnvironment{longtable}" + guard,
    ])


def colors_tex():
    return r"\definecolor{osdagGreen}{HTML}{" + COLOR_OSDAG_GREEN + r"}"


def line_stretch_tex():
    return r"\setstretch{" + f"{LINE_STRETCH}" + r"}"