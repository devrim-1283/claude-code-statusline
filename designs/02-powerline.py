#!/usr/bin/env python3
"""
Design 02 — Powerline.
Solid background segments with  arrow transitions. Bold, structured, IDE-like.
Requires a Powerline / Nerd Font for the  glyphs (falls back gracefully visually).
"""
import sys, json, time, os

def fg(n): return f"\033[38;5;{n}m"
def bg(n): return f"\033[48;5;{n}m"
B, R = "\033[1m", "\033[0m"
ARROW = ""  #

def reset(e):
    try: rem = int(e) - int(time.time())
    except (TypeError, ValueError): return ""
    if rem <= 0: return "now"
    d, rem = divmod(rem, 86400); h, rem = divmod(rem, 3600); m = rem // 60
    return f"{d}d{h}h" if d else (f"{h}h{m}m" if h else f"{max(1,m)}m")

def pf(p):
    try: return f"{round(float(p))}%"
    except (TypeError, ValueError): return "--%"

def color_for(p):
    try: p = float(p)
    except (TypeError, ValueError): return 240
    return 28 if p < 75 else (130 if p < 90 else 124)

def seg(text, bgc, fgc=255):
    return f"{bg(bgc)}{fg(fgc)}{B} {text} {R}"

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

    chunks = []  # (text, bg)
    chunks.append((f" {folder}", 24))
    chunks.append((f"ctx {pf(cp)}", color_for(cp)))
    if h5: chunks.append((f"5h {pf(h5.get('used_percentage'))} {reset(h5.get('resets_at'))}", color_for(h5.get('used_percentage'))))
    if d7: chunks.append((f"7d {pf(d7.get('used_percentage'))} {reset(d7.get('resets_at'))}", color_for(d7.get('used_percentage'))))
    chunks.append((f"◆ {model}", 53))

    out = ""
    for i, (text, bgc) in enumerate(chunks):
        out += seg(text, bgc)
        nxt = chunks[i + 1][1] if i + 1 < len(chunks) else None
        if nxt is not None:
            out += f"{bg(nxt)}{fg(bgc)}{ARROW}{R}"
        else:
            out += f"{fg(bgc)}{ARROW}{R}"
    sys.stdout.write(out)

if __name__ == "__main__":
    main()
