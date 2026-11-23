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

# A section heading that is followed by a table moves to the next page
# unless this many text lines fit below it (stops orphaned headings).
SECTION_NEEDSPACE_BASELINES = 10

# ---------------------------------------------------------------------------
# Charts (matplotlib figures embedded in the report)
# ---------------------------------------------------------------------------
CHART_DPI = 200                    # resolution of the saved PNG
CHART_WIDTH_IN = 6.5               # figure width in inches
CHART_HEIGHT_IN = 3.2              # figure height in inches
CHART_FONT_SIZE = 9                # axis labels, ticks and legend
CHART_TITLE_SIZE = 10              # chart title
CHART_VALUE_LABEL_SIZE = 8         # numbers printed above the bars
CHART_EMBED_WIDTH = r"0.85\textwidth"   # width of the chart in the PDF

CHART_COLOR_PASS = "#" + COLOR_OSDAG_GREEN   # bars with UR <= 1.0
CHART_COLOR_FAIL = "#C0392B"                 # bars with UR > 1.0
CHART_COLOR_SECOND = "#4A6FA5"               # second series in grouped charts
CHART_COLOR_THIRD = "#E0A030"                # third series / quantity charts
CHART_COLOR_LIMIT = "red"                    # the UR = 1.0 limit line
CHART_LIMIT_STYLE = "--"                     # dashed
CHART_LIMIT_WIDTH = 1.3
UR_LIMIT = 1.0                               # utilization ratio limit


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
        CLINE_NOBREAK_TEX,
    ])


# ---------------------------------------------------------------------------
# Spacing and colours used by the chapter files
# ---------------------------------------------------------------------------
COLOR_FAIL = "FF0000"          # FAIL status text
COLOR_TEXT = "000000"          # normal body text

SPACE_XS = "2pt"               # \osdagGapXS
SPACE_S = "4pt"                # \osdagGapS
SPACE_M = "6pt"                # \osdagGapM
SPACE_TIGHT = "0.4em"          # \osdagGapTight
SPACE_L = "1em"                # \osdagGapL  (gap between blocks)
SPACE_CM = "0.4cm"             # \osdagGapCm

_SPACING_MACROS = {
    "osdagGapXS": SPACE_XS,
    "osdagGapS": SPACE_S,
    "osdagGapM": SPACE_M,
    "osdagGapTight": SPACE_TIGHT,
    "osdagGapL": SPACE_L,
    "osdagGapCm": SPACE_CM,
}


def colors_tex():
    """Named colours and spacing macros, defined once in the preamble."""
    lines = [
        r"\definecolor{osdagGreen}{HTML}{" + COLOR_OSDAG_GREEN + r"}",
        r"\definecolor{osdagFail}{HTML}{" + COLOR_FAIL + r"}",
        r"\definecolor{osdagText}{HTML}{" + COLOR_TEXT + r"}",
    ]
    for name, value in _SPACING_MACROS.items():
        lines.append(r"\newcommand{" + "\\" + name + r"}{" + value + r"}")
    lines.append(r"\newcommand{\osdagSectionGuard}{\needspace{"
                 + f"{SECTION_NEEDSPACE_BASELINES}" + r"\baselineskip}}")
    return "\n".join(lines)


def line_stretch_tex():
    return r"\setstretch{" + f"{LINE_STRETCH}" + r"}"

# ---------------------------------------------------------------------------
# Per-chapter table padding (used by the chapter files)
# ---------------------------------------------------------------------------
TABCOLSEP_COMPACT_PT = 4       # compact tables (chapters 2 and 5)
TABCOLSEP_TIGHT_PT = 3         # tight tables (chapter 4 maximum-demand table)
TABCOLSEP_SUMMARY_PT = 3.5     # summary tables (chapters 7 and 8)
ARRAYSTRETCH_TIGHT = 1.25      # row height multiplier for the chapter 4 table


def tabcolsep_tex(pt):
    """LaTeX line that sets the horizontal cell padding to `pt` points."""
    return r"\setlength{\tabcolsep}{" + f"{pt}pt" + r"}"


def arraystretch_tex(factor):
    """LaTeX line that sets the row height multiplier."""
    return r"\renewcommand{\arraystretch}{" + f"{factor}" + r"}"

# ---------------------------------------------------------------------------
# Keep a girder's rows together (page-break rule for grouped tables)
# ---------------------------------------------------------------------------
ROW_END_TEX = r"\\[6pt]"            # normal row end used by the grouped tables
ROW_END_NOBREAK_TEX = r"\\*[6pt]"   # same, but forbids a page break after the row
KEEP_GROUP_MAX_ROWS = 16            # longer blocks are left free to break

# No page break right after a \cline rule (needs etoolbox, loaded by the preamble)
CLINE_NOBREAK_TEX = "\n".join([
    r"\makeatletter",
    r"\patchcmd{\@cline}{\vskip -\arrayrulewidth}{\penalty\@M\vskip -\arrayrulewidth}{}"
    r"{\PackageWarning{osdag}{cline no-break patch failed}}",
    r"\makeatother",
])


def keep_rows_together(group_tex):
    """Forbid a page break inside one block of table rows.

    Every row end except the last one in the block becomes the no-break
    version, so the whole block moves to the next page together instead of
    splitting (for example G5 Live Load on one page and G5 Total Load on the
    next). Blocks with fewer than 2 or more than KEEP_GROUP_MAX_ROWS rows are
    returned unchanged.
    """
    parts = group_tex.split(ROW_END_TEX)
    n_rows = len(parts) - 1
    if n_rows < 2 or n_rows > KEEP_GROUP_MAX_ROWS:
        return group_tex
    return ROW_END_NOBREAK_TEX.join(parts[:-1]) + ROW_END_TEX + parts[-1]


# ---------------------------------------------------------------------------
# Header / footer (fancyhdr) theme
# ---------------------------------------------------------------------------
FOOTER_LEFT_TEXT = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
FOOTER_RIGHT_TEXT = r"Page \thepage\ of \pageref{LastPage}"
HEADRULE_WIDTH_PT = 1
FOOTRULE_WIDTH_PT = 1


def header_footer_tex(project, job, date, rev):
    """All fancyhdr page styles (main, plain, firstpage) in one place."""
    head = (r"  \fancyhf{}" "\n"
            r"  \fancyhead[L]{" + project + r" $|$ " + job + "}\n"
            r"  \fancyhead[R]{" + date + r" $|$ " + rev + "}\n"
            r"  \fancyfoot[L]{" + FOOTER_LEFT_TEXT + "}\n"
            r"  \fancyfoot[R]{" + FOOTER_RIGHT_TEXT + "}\n"
            r"  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height "
            + f"{HEADRULE_WIDTH_PT}pt" + r" \vspace{2pt}}" "\n"
            r"  \renewcommand{\footrule}{%" "\n"
            r"    \ifbool{hasSDonPage}{%" "\n"
            r"      \vspace{-20pt}%" "\n"
            r"      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%" "\n"
            r"      \vspace{4pt}%" "\n"
            r"    }{%" "\n"
            r"      \vspace{-8pt}%" "\n"
            r"    }%" "\n"
            r"    \color{osdagGreen}\hrule width\headwidth height "
            + f"{FOOTRULE_WIDTH_PT}pt" + r" \vspace{6pt}%" "\n"
            r"  }" "\n")
    first = (r"  \fancyhf{}" "\n"
             r"  \renewcommand{\headrulewidth}{0pt}" "\n"
             r"  \fancyfoot[L]{" + FOOTER_LEFT_TEXT + "}\n"
             r"  \fancyfoot[R]{" + FOOTER_RIGHT_TEXT + "}\n"
             r"  \renewcommand{\footrule}{\vspace{-8pt}\color{osdagGreen}\hrule width\headwidth height "
             + f"{FOOTRULE_WIDTH_PT}pt" + r" \vspace{6pt}}" "\n")
    return (r"\fancypagestyle{main}{" "\n" + head + "}\n"
            r"\fancypagestyle{plain}{" "\n" + head + "}\n"
            r"\fancypagestyle{firstpage}{" "\n" + first + "}\n"
            r"\pagestyle{main}")
