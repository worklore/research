# Honest vs vague tool names at 100 tools: schemas loaded and input tokens per run (numbers from report.md / names.md)
rows = [  # label, sublabel, schemas honest, schemas vague (None = n/a + note), tokens honest, tokens vague
    ("Claude Code", "поиск включён (по умолчанию)", 1.58, 7.61, None, 19.9, 24.1),
    ("Antigravity", "Gemini 3.1 Pro", 0.94, 3.69, None, 18.6, 25.7),
    ("Claude Code", "поиск выключен", None, None, "все 100 схем уже в промпте", 48.6, 47.5),
    ("Codex CLI", "code mode", None, None, "ищет определения кодом", 78.2, 73.2),
]
W, H = 1200, 700
SURF, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#77766f", "#e1e0d9", "#c3c2b7"
HON, VAG = "#2a78d6", "#e5713a"
BAR, GAP, ROW, TOP = 24, 2, 96, 206
A0, AW, AMAX = 330, 300, 8.0      # schemas panel
B0, BW, TMAX = 740, 360, 80.0     # tokens panel
F = "font-family='Inter, -apple-system, Segoe UI, Helvetica, Arial, sans-serif'"
o = []
def t(x, y, s, size=15, fill=INK, anchor="start", weight=400):
    o.append(f"<text x='{x}' y='{y}' {F} font-size='{size}' fill='{fill}' text-anchor='{anchor}' font-weight='{weight}'>{s}</text>")
def bar(x0, y, w, color):
    r = 4
    if w < r * 2: o.append(f"<rect x='{x0}' y='{y}' width='{w}' height='{BAR}' fill='{color}'/>"); return
    o.append(f"<path d='M{x0},{y} H{x0+w-r} Q{x0+w},{y} {x0+w},{y+r} V{y+BAR-r} Q{x0+w},{y+BAR} {x0+w-r},{y+BAR} H{x0} Z' fill='{color}'/>")
c = lambda v: str(v).replace('.', ',')
o.append(f"<rect width='{W}' height='{H}' fill='{SURF}'/>")
t(40, 52, "Невнятные названия: ответы те же, читать приходится больше", 26, INK, weight=650)
t(40, 82, "Те же 100 инструментов и описания, только названия вроде optimize_file и process_image. 36 прогонов на столбец.", 16, INK2)
t(40, 104, "Точность не изменилась: 276 из 276 прогонов с невнятными названиями правильные.", 16, INK, weight=600)
lx, ly = 40, 140
o.append(f"<rect x='{lx}' y='{ly-13}' width='16' height='16' rx='3' fill='{HON}'/>"); t(lx+24, ly, "точные названия (pdf_compress)", 15, INK)
o.append(f"<rect x='{lx+300}' y='{ly-13}' width='16' height='16' rx='3' fill='{VAG}'/>"); t(lx+324, ly, "невнятные (optimize_file)", 15, INK)
t(A0, 190, "Схем прочитано за прогон", 15, INK, weight=600)
t(B0, 190, "Входные токены за прогон", 15, INK, weight=600)
bottom = TOP + ROW * len(rows) - 20
for v in (0, 2, 4, 6, 8):
    x = A0 + AW * v / AMAX
    o.append(f"<line x1='{x}' y1='{TOP-6}' x2='{x}' y2='{bottom}' stroke='{GRID if v else AXIS}' stroke-width='1'/>")
    t(x, bottom + 20, str(v), 13, MUTED, "middle")
for v in (0, 20, 40, 60, 80):
    x = B0 + BW * v / TMAX
    o.append(f"<line x1='{x}' y1='{TOP-6}' x2='{x}' y2='{bottom}' stroke='{GRID if v else AXIS}' stroke-width='1'/>")
    t(x, bottom + 20, f"{v}k", 13, MUTED, "middle")
for i, (lab, sub, s_h, s_v, note, k_h, k_v) in enumerate(rows):
    y = TOP + i * ROW
    t(40, y + 22, lab, 16, INK, weight=600); t(40, y + 42, sub, 14, INK2)
    if s_h is None:
        t(A0 + 8, y + 30, note, 14, MUTED)
    else:
        bar(A0, y, AW * s_h / AMAX, HON); bar(A0, y + BAR + GAP, AW * s_v / AMAX, VAG)
        t(A0 + AW * s_h / AMAX + 8, y + 17, c(round(s_h, 1)), 14, INK2)
        t(A0 + AW * s_v / AMAX + 8, y + BAR + GAP + 17, f"{c(round(s_v, 1))}  (×{c(round(s_v / s_h, 1))})", 14, INK, weight=700)
    bar(B0, y, BW * k_h / TMAX, HON); bar(B0, y + BAR + GAP, BW * k_v / TMAX, VAG)
    t(B0 + BW * k_h / TMAX + 8, y + 17, f"{c(k_h)}k", 14, INK2)
    d = round((k_v / k_h - 1) * 100)
    t(B0 + BW * k_v / TMAX + 8, y + BAR + GAP + 17, f"{c(k_v)}k  ({'+' if d > 0 else '−'}{abs(d)}%)", 14, INK, weight=700 if abs(d) >= 15 else 400)
yn = bottom + 58
t(40, yn, "Gemini с невнятными названиями (50 и 100 инструментов): первой открыл схему не того инструмента", 15, INK2)
t(40, yn + 22, "в 34 прогонах из 72, а в 10 прогонах пробовал вызвать не тот инструмент с пустыми аргументами.", 15, INK2)
t(40, H - 24, "У Codex с невнятными названиями 30 прогонов вместо 36 (лимит подписки)  ·  Данные: github.com/worklore/worklore-mcp/tree/main/research/tools-count  ·  октябрь 2026", 13, MUTED)
svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>" + "".join(o) + "</svg>"
open("names-ru.svg", "w").write(svg)
open("names-ru.html", "w").write(f"<!doctype html><html><body style='margin:0;background:{SURF}'>{svg}</body></html>")
