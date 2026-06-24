#!/usr/bin/env python3
"""
Design 09 — Git Aware.
Adds live git context: branch, dirty/clean state, and ahead/behind counts.
Clean teal aesthetic with ▕▏ block bars. Great for repo-heavy workflows.
Extra feature vs the base statusline:  git branch +  dirty/ clean + ↑↓ sync.
"""
import sys, json, time, os, subprocess

def c(n): return f"\033[38;5;{n}m"
B, R, DIM = "\033[1m", "\033[0m", "\033[2m"
FULL, EMP = "▰", "▱"

def bar(pct, w=9):
    try: pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError): pct = 0.0
    col = 43 if pct < 75 else (215 if pct < 90 else 203)
    f = int(round(pct / 100.0 * w))
    return f"{c(col)}{FULL*f}{DIM}{c(238)}{EMP*(w-f)}{R}"

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def pcol(p):
    try: p = float(p)
    except (TypeError, ValueError): return c(43)
    return c(43) if p < 75 else (c(215) if p < 90 else c(203))

def reset(e):
    try: rem = int(e) - int(time.time())
    except (TypeError, ValueError): return ""
    if rem <= 0: return "now"
    d, rem = divmod(rem, 86400); h, rem = divmod(rem, 3600); m = rem // 60
    return f"{d}d {h}h" if d else (f"{h}h {m}m" if h else f"{max(1,m)}m")

def git_segment(cwd):
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
    icon = f"{c(208)}●{R}" if dirty else f"{c(78)}✓{R}"
    sync = ""
    counts = run("rev-list", "--left-right", "--count", "@{u}...HEAD")
    if counts and "\t" in counts:
        behind, ahead = counts.split("\t")[:2]
        if ahead != "0": sync += f" {c(78)}↑{ahead}{R}"
        if behind != "0": sync += f" {c(203)}↓{behind}{R}"
    return f"{c(141)} {B}{c(183)}{branch}{R} {icon}{sync}"

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
    parts = [f"{B}{c(43)}❯ {folder}{R}"]
    g = git_segment(cwd)
    if g: parts.append(g)
    parts.append(f"{c(250)}ctx{R} {bar(cp)} {pcol(cp)}{pf(cp)}{R}")
    if h5: parts.append(f"{c(250)}5h{R} {bar(h5.get('used_percentage'))} {pcol(h5.get('used_percentage'))}{pf(h5.get('used_percentage'))}{R} {DIM}{c(245)}{reset(h5.get('resets_at'))}{R}")
    if d7: parts.append(f"{c(250)}7d{R} {bar(d7.get('used_percentage'))} {pcol(d7.get('used_percentage'))}{pf(d7.get('used_percentage'))}{R} {DIM}{c(245)}{reset(d7.get('resets_at'))}{R}")
    parts.append(f"{B}{c(159)}{model}{R}")
    sys.stdout.write(sep.join(parts))

if __name__ == "__main__":
    main()
