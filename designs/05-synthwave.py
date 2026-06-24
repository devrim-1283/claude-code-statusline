#!/usr/bin/env python3
"""
Design 05 — Synthwave Neon.
Hot magenta, cyan, and electric purple. Retro-futuristic, glowing.
Bars use a magenta→cyan ramp regardless of level; severity shows in the % color.
"""
import sys, json, time, os

def c(n): return f"\033[38;5;{n}m"
B, R, DIM = "\033[1m", "\033[0m", "\033[2m"
NEON = [201, 200, 199, 170, 141, 99, 75, 51]  # magenta -> cyan
FULL, EMP = "▮", "▯"

def bar(pct, w=8):
    try: pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError): pct = 0.0
    f = int(round(pct / 100.0 * w))
    out = ""
    for i in range(w):
        col = NEON[min(len(NEON) - 1, int(i / max(1, w - 1) * (len(NEON) - 1) + 0.5))]
        out += f"{B}{c(col)}{FULL}" if i < f else f"{DIM}{c(54)}{EMP}"
    return out + R

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def pcol(p):
    try: p = float(p)
    except (TypeError, ValueError): return c(51)
    return c(51) if p < 75 else (c(213) if p < 90 else c(198))

def reset(e):
    try: rem = int(e) - int(time.time())
    except (TypeError, ValueError): return ""
    if rem <= 0: return "now"
    d, rem = divmod(rem, 86400); h, rem = divmod(rem, 3600); m = rem // 60
    return f"{d}d {h}h" if d else (f"{h}h {m}m" if h else f"{max(1,m)}m")

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
    sep = f"{c(57)} ▓ {R}"
    parts = [f"{B}{c(213)}▰ {folder}{R}", f"{c(141)}ctx{R} {bar(cp)} {B}{pcol(cp)}{pf(cp)}{R}"]
    if h5: parts.append(f"{c(141)}5h{R} {bar(h5.get('used_percentage'))} {B}{pcol(h5.get('used_percentage'))}{pf(h5.get('used_percentage'))}{R} {c(99)}{reset(h5.get('resets_at'))}{R}")
    if d7: parts.append(f"{c(141)}7d{R} {bar(d7.get('used_percentage'))} {B}{pcol(d7.get('used_percentage'))}{pf(d7.get('used_percentage'))}{R} {c(99)}{reset(d7.get('resets_at'))}{R}")
    parts.append(f"{B}{c(51)}◈ {model}{R}")
    sys.stdout.write(sep.join(parts))

if __name__ == "__main__":
    main()
