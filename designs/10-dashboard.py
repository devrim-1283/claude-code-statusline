#!/usr/bin/env python3
"""
Design 10 — Full Dashboard.
The kitchen-sink build. Everything at a glance:
  📁 folder ·  git branch+state ·  clock ·  token count + $ cost estimate
  · 🧠 ctx · ⏱ 5h · 📅 7d · ◆ model
Extra features vs base: git branch/dirty, wall-clock time, live token total,
and a rough session cost estimate derived from token usage.
"""
import sys, json, time, os, subprocess

def c(n): return f"\033[38;5;{n}m"
B, R, DIM = "\033[1m", "\033[0m", "\033[2m"
GREEN = [22, 28, 34, 40, 46]; AMBER = [94, 136, 178, 214, 220]; RED = [52, 88, 124, 160, 196]
FULL, EMP = "█", "─"

def ramp(p): return RED if p >= 90 else (AMBER if p >= 75 else GREEN)

def bar(pct, w=8):
    try: pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError): pct = 0.0
    rmp = ramp(pct); f = int(round(pct / 100.0 * w)); out = ""
    for i in range(w):
        if i < f:
            col = rmp[min(len(rmp)-1, int(i/max(1,w-1)*(len(rmp)-1)+0.5))]
            out += f"{c(col)}{FULL}"
        else:
            out += f"{DIM}{c(236)}{EMP}"
    return out + R

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def pcol(p):
    try: p = float(p)
    except (TypeError, ValueError): return c(46)
    return c(196) if p >= 90 else (c(214) if p >= 75 else c(46))

def reset(e):
    try: rem = int(e) - int(time.time())
    except (TypeError, ValueError): return ""
    if rem <= 0: return "now"
    d, rem = divmod(rem, 86400); h, rem = divmod(rem, 3600); m = rem // 60
    return f"{d}d {h}h" if d else (f"{h}h {m}m" if h else f"{max(1,m)}m")

def human_tokens(n):
    try: n = int(n)
    except (TypeError, ValueError): return None
    if n >= 1000: return f"{n/1000:.1f}k"
    return str(n)

def git_branch(cwd):
    try:
        b = subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=0.5).stdout.strip()
        if not b: return None
        dirty = bool(subprocess.run(["git", "-C", cwd, "status", "--porcelain"],
                                    capture_output=True, text=True, timeout=0.5).stdout.strip())
        mark = f"{c(208)}*{R}" if dirty else ""
        return f"{c(141)} {c(183)}{b}{R}{mark}"
    except Exception:
        return None

def main():
    try: data = json.load(sys.stdin)
    except Exception: data = {}
    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd") or os.getcwd()
    folder = os.path.basename(cwd.rstrip("/")) or "/"
    model = (data.get("model") or {}).get("display_name") or "?"
    ctx = data.get("context_window") or {}
    cp = ctx.get("used_percentage")
    used = ctx.get("total_input_tokens") or 0
    if cp is None:
        s = ctx.get("context_window_size") or 0
        cp = (used / s * 100.0) if s else 0.0
    rl = data.get("rate_limits") or {}
    h5, d7 = rl.get("five_hour") or {}, rl.get("seven_day") or {}

    # cost estimate (rough): treat reported tokens as input @ ~$15/Mtok Opus-class
    cost = (used / 1_000_000.0) * 15.0 if used else 0.0

    sep = f"{c(240)}  │  {R}"
    parts = [f"📁 {B}{c(48)}{folder}{R}"]
    g = git_branch(cwd)
    if g: parts.append(g)
    parts.append(f"🕐 {c(252)}{time.strftime('%H:%M')}{R}")
    tk = human_tokens(used)
    if tk and tk != "0":
        parts.append(f"🪙 {c(180)}{tk}{R} {DIM}{c(245)}≈${cost:.2f}{R}")
    parts.append(f"🧠 {c(250)}ctx{R} {bar(cp)} {pcol(cp)}{pf(cp)}{R}")
    if h5:
        seg = f"⏱ {c(250)}5h{R} {bar(h5.get('used_percentage'))} {pcol(h5.get('used_percentage'))}{pf(h5.get('used_percentage'))}{R}"
        r = reset(h5.get('resets_at'));  seg += f" {DIM}{c(245)}↻{r}{R}" if r else ""
        parts.append(seg)
    if d7:
        seg = f"📅 {c(250)}7d{R} {bar(d7.get('used_percentage'))} {pcol(d7.get('used_percentage'))}{pf(d7.get('used_percentage'))}{R}"
        r = reset(d7.get('resets_at'));  seg += f" {DIM}{c(245)}↻{r}{R}" if r else ""
        parts.append(seg)
    parts.append(f"{c(244)}◆{R} {B}{c(159)}{model}{R}")
    sys.stdout.write(sep.join(parts))

if __name__ == "__main__":
    main()
