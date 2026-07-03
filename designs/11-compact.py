#!/usr/bin/env python3
"""
Design 11 — Compact.
The small-footprint build: labeled colored percentages, nothing else.
  folder · git branch(+dirty) · ctx% · 5h% · 7d% · model
Everything the base tracks, squeezed to the narrowest readable single line.
Dropped vs base/09/10: bars, reset clocks, emoji, ahead/behind, token/cost.
"""
import sys, json, os, time, subprocess

def c(n): return f"\033[38;5;{n}m"
B, R, DIM = "\033[1m", "\033[0m", "\033[2m"

def reset(e):
    """Time until reset, single dominant unit: '4g', '2sa', '45dk', 'şimdi'."""
    try:
        rem = int(e) - int(time.time())
    except (TypeError, ValueError, OverflowError):
        return ""
    if rem <= 0:
        return "şimdi"
    d, rem = divmod(rem, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        return f"{d}g"
    if h:
        return f"{h}sa"
    return f"{max(1, m)}dk"

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def pcol(p):
    try: p = float(p)
    except (TypeError, ValueError): return c(46)
    return c(196) if p >= 90 else (c(214) if p >= 75 else c(46))

def metric(label, p, e=None):
    seg = f"{DIM}{c(245)}{label}{R} {pcol(p)}{pf(p)}{R}"
    r = reset(e)
    if r:
        seg += f" {DIM}{c(245)}{r}{R}"
    return seg

def git_branch(cwd):
    def run(*a):
        try:
            return subprocess.run(["git", "-C", cwd, *a], capture_output=True,
                                  text=True, timeout=0.5).stdout.strip()
        except Exception:
            return ""
    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    if not branch:
        return None
    dirty = bool(run("status", "--porcelain"))
    star = f"{c(208)}*{R}" if dirty else ""
    return f"{c(141)}{branch}{R}{star}"

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
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

    parts = [f"{B}{c(48)}{folder}{R}"]
    g = git_branch(cwd)
    if g:
        parts.append(g)
    parts.append(metric("ctx", cp))
    if h5:
        parts.append(metric("5h", h5.get("used_percentage"), h5.get("resets_at")))
    if d7:
        parts.append(metric("7d", d7.get("used_percentage"), d7.get("resets_at")))
    parts.append(f"{B}{c(159)}{model}{R}")

    sys.stdout.write("  ".join(parts))

if __name__ == "__main__":
    main()
