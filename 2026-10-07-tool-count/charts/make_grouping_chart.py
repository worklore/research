# Grouped vs separate MCP tools: accuracy and input tokens per run (numbers from the public report.md)
rows = [  # label, sublabel, acc_sep, acc_grp, tok_sep, tok_grp
    ("Claude Code", "tool search off", 100, 100, 27.9, 14.2),
    ("Claude Code", "tool search on (default)", 100, 100, 17.4, 16.1),
    ("Codex CLI", "code mode", 100, 100, 61.4, 50.6),
    ("Antigravity", "Gemini 3.1 Pro", 100, 89, 20.5, 34.1),
]
W, H = 1200, 640
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#77766f", "#e1e0d9", "#c3c2b7"
SEP, GRP = "#2a78d6", "#e5713a"
BAR, GAP, ROW, TOP = 24, 2, 96, 176
A0, AW = 250, 360          # accuracy panel
B0, BW = 700, 420          # tokens panel
TMAX = 70.0
F = "font-family='Inter, -apple-system, Segoe UI, Helvetica, Arial, sans-serif'"
o = []
def t(x, y, s, size=15, fill=INK, anchor="start", weight=400):
    o.append(f"<text x='{x}' y='{y}' {F} font-size='{size}' fill='{fill}' text-anchor='{anchor}' font-weight='{weight}'>{s}</text>")
def bar(x0, y, w, color):
    r = 4
    if w < r * 2: o.append(f"<rect x='{x0}' y='{y}' width='{w}' height='{BAR}' fill='{color}'/>"); return
    o.append(f"<path d='M{x0},{y} H{x0+w-r} Q{x0+w},{y} {x0+w},{y+r} V{y+BAR-r} Q{x0+w},{y+BAR} {x0+w-r},{y+BAR} H{x0} Z' fill='{color}'/>")
o.append(f"<rect width='{W}' height='{H}' fill='{SURF}'/>")
t(40, 52, "Grouping MCP tools: cheaper in Claude Code, worse in Gemini", 26, INK, weight=650)
t(40, 84, "The same 50 operations, exposed as 50 separate tools or as 7 grouped tools. 36 runs per bar. Gemini's 89% is the only accuracy drop in all 1,932 runs.", 16, INK2)
# legend
lx, ly = 40, 118
o.append(f"<rect x='{lx}' y='{ly-13}' width='16' height='16' rx='3' fill='{SEP}'/>"); t(lx+24, ly, "50 separate tools", 15, INK)
o.append(f"<rect x='{lx+190}' y='{ly-13}' width='16' height='16' rx='3' fill='{GRP}'/>"); t(lx+214, ly, "7 grouped tools", 15, INK)
# panel titles
t(A0, 158, "Runs fully correct", 15, INK, weight=600)
t(B0, 158, "Input tokens per run", 15, INK, weight=600)
bottom = TOP + ROW * len(rows) - 20
# gridlines + ticks
for v in (0, 25, 50, 75, 100):
    x = A0 + AW * v / 100
    o.append(f"<line x1='{x}' y1='{TOP-6}' x2='{x}' y2='{bottom}' stroke='{GRID if v else AXIS}' stroke-width='1'/>")
    t(x, bottom + 20, f"{v}%", 13, MUTED, "middle")
for v in (0, 20, 40, 60):
    x = B0 + BW * v / TMAX
    o.append(f"<line x1='{x}' y1='{TOP-6}' x2='{x}' y2='{bottom}' stroke='{GRID if v else AXIS}' stroke-width='1'/>")
    t(x, bottom + 20, f"{v}k", 13, MUTED, "middle")
for i, (lab, sub, a_s, a_g, k_s, k_g) in enumerate(rows):
    y = TOP + i * ROW
    t(40, y + 22, lab, 16, INK, weight=600); t(40, y + 42, sub, 14, INK2)
    # accuracy
    bar(A0, y, AW * a_s / 100, SEP); bar(A0, y + BAR + GAP, AW * a_g / 100, GRP)
    t(A0 + AW * a_s / 100 + 8, y + 17, f"{a_s}%", 14, INK2)
    if a_g < 100:
        t(A0 + AW * a_g / 100 + 8, y + BAR + GAP + 17, f"{a_g}%", 14, INK, weight=700)
        t(A0 + AW * a_g / 100 + 8, y + 2 * BAR + GAP + 18, "32 of 36", 13, INK2)
    else:
        t(A0 + AW * a_g / 100 + 8, y + BAR + GAP + 17, f"{a_g}%", 14, INK2)
    # tokens
    bar(B0, y, BW * k_s / TMAX, SEP); bar(B0, y + BAR + GAP, BW * k_g / TMAX, GRP)
    t(B0 + BW * k_s / TMAX + 8, y + 17, f"{k_s}k", 14, INK2)
    d = round((k_g / k_s - 1) * 100)
    t(B0 + BW * k_g / TMAX + 8, y + BAR + GAP + 17, f"{k_g}k  ({'+' if d > 0 else '−'}{abs(d)}%)", 14, INK, weight=600 if abs(d) >= 30 else 400)
t(40, H - 28, "Data and kit: github.com/worklore/worklore-mcp/tree/main/research/tools-count  ·  Claude Opus 5.5, GPT-6.1-sol, Gemini 3.1 Pro  ·  October 2026", 13, MUTED)
svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>" + "".join(o) + "</svg>"
open("grouping.svg", "w").write(svg)
open("grouping.html", "w").write(f"<!doctype html><html><body style='margin:0;background:{SURF}'>{svg}</body></html>")
