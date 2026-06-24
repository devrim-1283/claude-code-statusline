#!/usr/bin/env python3
"""
Design 04 — Smooth Gradient Blocks.
Sub-cell partial blocks (▏▎▍▌▋▊▉█) give a smooth, analog fill. Each bar is a
true gradient across a green→teal palette. Polished and modern.
"""
import sys, json, time, os

def c(n): return f"\033[38;5;{n}m"
B, R, DIM = "\033[1m", "\033[0m", "\033[2m"
PARTIALS = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉"]
FULL = "█"
GREEN_RAMP = [22, 29, 35, 42, 48, 50]
AMBER_RAMP = [94, 130, 172, 208, 214, 220]
RED_RAMP = [52, 88, 124, 160, 196, 197]

def bar(pct, w=12):
    try: pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError): pct = 0.0
    ramp = GREEN_RAMP if pct < 75 else (AMBER_RAMP if pct < 90 else RED_RAMP)
    units = pct / 100.0 * w
    full = int(units)
    frac = units - full
    out = ""
    for i in range(w):
        col = ramp[min(len(ramp) - 1, int(i / max(1, w - 1) * (len(ramp) - 1) + 0.5))]
        if i < full:
            out += f"{c(col)}{FULL}"
        elif i == full and frac > 0:
            out += f"{c(col)}{PARTIALS[int(frac * 8)]}"
        else:
            out += f"{DIM}{c(236)}─"
    return out + R

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def pcol(p):
    try: p = float(p)
    except (TypeError, ValueError): return c(48)
    return c(48) if p < 75 else (c(214) if p < 90 else c(196))

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
    sep = f"{c(239)}  ·  {R}"
    parts = [f"{B}{c(48)}❯ {folder}{R}", f"{c(250)}ctx{R} {bar(cp)} {pcol(cp)}{pf(cp)}{R}"]
    if h5: parts.append(f"{c(250)}5h{R} {bar(h5.get('used_percentage'))} {pcol(h5.get('used_percentage'))}{pf(h5.get('used_percentage'))}{R} {DIM}{c(245)}{reset(h5.get('resets_at'))}{R}")
    if d7: parts.append(f"{c(250)}7d{R} {bar(d7.get('used_percentage'))} {pcol(d7.get('used_percentage'))}{pf(d7.get('used_percentage'))}{R} {DIM}{c(245)}{reset(d7.get('resets_at'))}{R}")
    parts.append(f"{B}{c(159)}{model}{R}")
    sys.stdout.write(sep.join(parts))

if __name__ == "__main__":
    main()
