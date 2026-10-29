#!/usr/bin/env python3
"""Build an SRT caption file from a timing.json with word timestamps.

Usage: make_srt.py <timing.json> <out.srt> [edits.json]

timing.json: {duration, beats[{id,title,start,end,text}], words[{w,s,e,b}]}
edits.json:  {inserts[{at, duration, label, caption?}]}  (times in timing.json seconds)

Cues end at sentence ends (. ! ?), at beat changes and at inserts. Each cue is
at most 2 lines of MAX_CHARS characters. Long sentences are split at a clause
break (, ; :) when possible, otherwise when the next word would overflow.

Inserts are clips added to the video after the voiceover: every word starting
at or after `at` moves `duration` seconds later, and the insert gets its own
cue (`caption`, default "[<label>]").
"""
import json
import sys

MAX_CHARS = 42
MAX_LINES = 2
MIN_CUE_SECONDS = 1.0
GAP_SECONDS = 0.04
TRAILING = "\"')]}”’"


def load_inserts(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        return sorted(json.load(f).get("inserts", []), key=lambda i: i["at"])


def offset(t, inserts):
    """Seconds added before timing.json time `t` by inserts."""
    return sum(i["duration"] for i in inserts if t >= i["at"])


def shift(t, inserts):
    """Map a timing.json time to the final video's time."""
    return t + offset(t, inserts)


def ends_with(word, chars):
    return word.rstrip(TRAILING)[-1:] in chars


def wrap(words):
    """Split words into at most MAX_LINES balanced lines, or None if they don't fit."""
    text = " ".join(words)
    if len(text) <= MAX_CHARS:
        return [text]
    best = None
    for i in range(1, len(words)):
        top, bottom = " ".join(words[:i]), " ".join(words[i:])
        if len(top) <= MAX_CHARS and len(bottom) <= MAX_CHARS:
            width = max(len(top), len(bottom))
            if best is None or width < best[0]:
                best = (width, [top, bottom])
    return best[1] if best else None


def group_cues(words, inserts):
    cues, cur = [], []
    for word in words:
        if cur and (
            word["b"] != cur[-1]["b"]
            or offset(word["s"], inserts) != offset(cur[-1]["s"], inserts)
            or wrap([x["w"] for x in cur + [word]]) is None
        ):
            cues.append(cur)
            cur = []
        cur.append(word)
        text_len = len(" ".join(x["w"] for x in cur))
        if ends_with(word["w"], ".!?") or (ends_with(word["w"], ",;:") and text_len >= MAX_CHARS):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return cues


def timestamp(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        timing = json.load(f)
    inserts = load_inserts(sys.argv[3] if len(sys.argv) == 4 else None)
    words = [w for w in timing["words"] if w["w"].strip()]
    if not words:
        sys.exit("error: timing.json has no words")

    cues = []  # (start, end, lines)
    for cue in group_cues(words, inserts):
        delta = offset(cue[0]["s"], inserts)
        lines = wrap([w["w"] for w in cue]) or [" ".join(w["w"] for w in cue)]
        cues.append((cue[0]["s"] + delta, cue[-1]["e"] + delta, lines))
    for ins in inserts:
        start = ins["at"] + sum(i["duration"] for i in inserts if i["at"] < ins["at"])
        caption = ins.get("caption") or f"[{ins.get('label', 'clip')}]"
        cues.append((start, start + ins["duration"], [caption]))
    cues.sort(key=lambda c: c[0])

    total = timing.get("duration", cues[-1][1]) + sum(i["duration"] for i in inserts)
    blocks, longest = [], 0
    for i, (start, end, lines) in enumerate(cues):
        next_start = cues[i + 1][0] if i + 1 < len(cues) else total
        # Short cues are hard to read: stretch them, but never into the next cue.
        end = max(end, min(start + MIN_CUE_SECONDS, next_start - GAP_SECONDS))
        end = min(end, next_start - GAP_SECONDS) if i + 1 < len(cues) else end
        longest = max(longest, *(len(line) for line in lines))
        blocks.append(f"{i + 1}\n{timestamp(start)} --> {timestamp(end)}\n" + "\n".join(lines) + "\n")

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("\n".join(blocks))

    print(f"wrote {len(blocks)} cues ({len(inserts)} inserts) to {sys.argv[2]}; longest line {longest} chars")
    if longest > MAX_CHARS:
        print(f"warning: a line is longer than {MAX_CHARS} chars", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
