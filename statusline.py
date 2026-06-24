#!/usr/bin/env python3
"""
Enterprise statusline for Claude Code — single line, static green bars.
Shows: working folder, model, context usage, 5h + weekly rate limits.

Input: Claude Code statusLine JSON on stdin.
Schema: model.display_name, cwd/workspace.current_dir,
context_window.used_percentage, rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}
"""
import sys, json, time, os

# ---- 256-color ANSI helpers -------------------------------------------------
def c(code): return f"\033[38;5;{code}m"
B   = "\033[1m"
DIM = "\033[2m"
R   = "\033[0m"

# Green-forward ramps (dark -> bright). Warning ramps kick in at high usage.
GREEN = [22, 28, 34, 40, 46]
AMBER = [94, 136, 178, 214, 220]
RED   = [52, 88, 124, 160, 196]
EMPTY = 236
FULL  = "█"
EMP   = "─"

def ramp_for(pct):
    if pct >= 90: return RED
    if pct >= 75: return AMBER
    return GREEN

def bar(pct, width=8):
    """Static segmented green bar for `pct` (0..100)."""
    try:
        pct = max(0.0, min(100.0, float(pct)))
    except (TypeError, ValueError):
        pct = 0.0
    ramp = ramp_for(pct)
    filled = int(round(pct / 100.0 * width))
    cells = []
    for i in range(width):
        if i < filled:
            frac = i / max(1, width - 1)
            col = ramp[min(len(ramp) - 1, int(frac * (len(ramp) - 1) + 0.5))]
            cells.append(f"{c(col)}{FULL}{R}")
        else:
            cells.append(f"{DIM}{c(EMPTY)}{EMP}{R}")
    return "".join(cells)

def pct_color(pct):
    try: pct = float(pct)
    except (TypeError, ValueError): return c(GREEN[4])
    if pct >= 90: return c(RED[4])
    if pct >= 75: return c(AMBER[4])
    return c(GREEN[4])

def fmt_pct(pct):
    try: return f"{round(float(pct))}%"
    except (TypeError, ValueError): return "--%"

def fmt_reset(epoch):
    """Time remaining until reset, e.g. '2sa 14dk', '45dk', '4g 6sa'."""
    try:
        remaining = int(epoch) - int(time.time())
    except (TypeError, ValueError, OverflowError):
        return ""
    if remaining <= 0:
        return "şimdi"
    days, rem = divmod(remaining, 86400)
    hours, rem = divmod(rem, 3600)
    mins = rem // 60
    if days:
        return f"{days}g {hours}sa"
    if hours:
        return f"{hours}sa {mins}dk"
    return f"{max(1, mins)}dk"

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd") or os.getcwd()
    folder = os.path.basename(cwd.rstrip("/")) or "/"
    model = (data.get("model") or {}).get("display_name") or "?"

    ctx = data.get("context_window") or {}
    ctx_pct = ctx.get("used_percentage")
    if ctx_pct is None:
        size = ctx.get("context_window_size") or 0
        used = ctx.get("total_input_tokens") or 0
        ctx_pct = (used / size * 100.0) if size else 0.0

    rl = data.get("rate_limits") or {}
    h5 = rl.get("five_hour") or {}
    d7 = rl.get("seven_day") or {}

    L   = c(250)              # readable label gray (no DIM)
    SEP = f"{c(240)}  │  {R}" # subtle but visible separator
    RST = c(245)              # reset-time icon
    RSV = f"{B}{c(252)}"      # reset-time value (bold, bright)

    parts = [
        f"📁 {B}{c(48)}{folder}{R}",
        f"🧠 {L}ctx{R} {bar(ctx_pct)} {pct_color(ctx_pct)}{fmt_pct(ctx_pct)}{R}",
    ]

    if h5:
        h5p, h5r = h5.get("used_percentage"), fmt_reset(h5.get("resets_at"))
        seg = f"⏱ {L}5sa{R} {bar(h5p)} {pct_color(h5p)}{fmt_pct(h5p)}{R}"
        if h5r: seg += f" {RST}↻{R} {RSV}{h5r}{R}"
        parts.append(seg)
    if d7:
        d7p, d7r = d7.get("used_percentage"), fmt_reset(d7.get("resets_at"))
        seg = f"📅 {L}7g{R} {bar(d7p)} {pct_color(d7p)}{fmt_pct(d7p)}{R}"
        if d7r: seg += f" {RST}↻{R} {RSV}{d7r}{R}"
        parts.append(seg)
    if not h5 and not d7:
        parts.append(f"{c(245)}limitler ilk API yanıtından sonra…{R}")

    # Model adı en sağda — sabit konum, belirgin.
    parts.append(f"{c(244)}◆{R} {B}{c(159)}{model}{R}")

    sys.stdout.write(SEP.join(parts))

if __name__ == "__main__":
    main()
