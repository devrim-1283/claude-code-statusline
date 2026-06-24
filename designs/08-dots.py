#!/usr/bin/env python3
"""
Design 08 — Dot Meter.
Five round pips per metric (●●●○○). Glanceable, calm, dashboard-like.
"""
import sys, json, time, os

def c(n): return f"\033[38;5;{n}m"
B, R, DIM = "\033[1m", "\033[0m", "\033[2m"
FULL, EMP = "●", "○"

def dots(pct, n=5):
    try: pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError): pct = 0.0
    col = 78 if pct < 75 else (221 if pct < 90 else 210)
    f = int(round(pct / 100.0 * n))
    return f"{c(col)}{FULL*f}{DIM}{c(239)}{EMP*(n-f)}{R}"

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def pcol(p):
    try: p = float(p)
    except (TypeError, ValueError): return c(78)
    return c(78) if p < 75 else (c(221) if p < 90 else c(210))

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
    sep = f"{c(240)}   {R}"
    parts = [f"{B}{c(80)}◗ {folder}{R}", f"{c(247)}ctx{R} {dots(cp)} {pcol(cp)}{pf(cp)}{R}"]
    if h5: parts.append(f"{c(247)}5h{R} {dots(h5.get('used_percentage'))} {pcol(h5.get('used_percentage'))}{pf(h5.get('used_percentage'))}{R} {DIM}{c(245)}{reset(h5.get('resets_at'))}{R}")
    if d7: parts.append(f"{c(247)}7d{R} {dots(d7.get('used_percentage'))} {pcol(d7.get('used_percentage'))}{pf(d7.get('used_percentage'))}{R} {DIM}{c(245)}{reset(d7.get('resets_at'))}{R}")
    parts.append(f"{c(244)}◆ {B}{c(159)}{model}{R}")
    sys.stdout.write(sep.join(parts))

if __name__ == "__main__":
    main()
