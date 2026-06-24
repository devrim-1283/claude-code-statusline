#!/usr/bin/env python3
"""
Design 03 — Braille Density.
Bars rendered as braille dot-density glyphs. Ultra-compact, techy, hacker vibe.
"""
import sys, json, time, os

def c(n): return f"\033[38;5;{n}m"
B, R, DIM = "\033[1m", "\033[0m", "\033[2m"
# Braille ramp from empty -> full (8 dot levels)
DOTS = ["⠀", "⡀", "⡄", "⡆", "⡇", "⣇", "⣧", "⣷", "⣿"]

def bar(pct, cells=6):
    try: pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError): pct = 0.0
    col = 40 if pct < 75 else (214 if pct < 90 else 196)
    total = pct / 100.0 * cells  # cells of fullness
    out = ""
    for i in range(cells):
        level = max(0.0, min(1.0, total - i))
        out += DOTS[int(round(level * 8))]
    return f"{c(col)}{out}{R}"

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def reset(e):
    try: rem = int(e) - int(time.time())
    except (TypeError, ValueError): return ""
    if rem <= 0: return "now"
    d, rem = divmod(rem, 86400); h, rem = divmod(rem, 3600); m = rem // 60
    return f"{d}d{h}h" if d else (f"{h}h{m}m" if h else f"{max(1,m)}m")

def main():
    try: data = json.load(sys.stdin)
    except Exception: data = {}
    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd") or os.getcwd()
    folder = os.path.basename(cwd.rstrip("/")) or "/"
    model = (data.get("model") or {}).get("display_name") or "?"
    ctx = data.get("context_window") or {}
    cp = ctx.get("used_percentage")
    if cp is None:
        s, u = ctx.get("context_window_size") or 0, ctx.get("total_input_tokens") or 0
        cp = (u / s * 100.0) if s else 0.0
    rl = data.get("rate_limits") or {}
    h5, d7 = rl.get("five_hour") or {}, rl.get("seven_day") or {}
    sep = f"{DIM}{c(240)} ⡇ {R}"
    parts = [f"{B}{c(45)}⠿ {folder}{R}", f"{c(248)}ctx{R} {bar(cp)} {c(252)}{pf(cp)}{R}"]
    if h5: parts.append(f"{c(248)}5h{R} {bar(h5.get('used_percentage'))} {c(252)}{pf(h5.get('used_percentage'))}{R} {DIM}{c(245)}{reset(h5.get('resets_at'))}{R}")
    if d7: parts.append(f"{c(248)}7d{R} {bar(d7.get('used_percentage'))} {c(252)}{pf(d7.get('used_percentage'))}{R} {DIM}{c(245)}{reset(d7.get('resets_at'))}{R}")
    parts.append(f"{c(244)}»{R} {B}{c(81)}{model}{R}")
    sys.stdout.write(sep.join(parts))

if __name__ == "__main__":
    main()
