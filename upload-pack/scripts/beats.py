#!/usr/bin/env python3
"""Print each beat's start in the final video, after edits.json inserts.

Usage: beats.py <timing.json> [edits.json]

Prints the expected final duration, then one line per beat:
<M:SS start>  <length in final video>  <id>  <title>
Starts use the same shift as make_srt.py, rounded down to whole seconds.
"""
import json
import sys

from make_srt import load_inserts, shift


def clock(seconds):
    s = int(seconds)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        timing = json.load(f)
    inserts = load_inserts(sys.argv[2] if len(sys.argv) == 3 else None)
    added = sum(i["duration"] for i in inserts)
    total = timing["duration"] + added

    print(f"expected duration: {total:.2f}s (timing.json {timing['duration']:.2f}s + inserts {added:.2f}s)")
    starts = [shift(b["start"], inserts) for b in timing["beats"]]
    starts[0] = 0.0
    for i, beat in enumerate(timing["beats"]):
        end = starts[i + 1] if i + 1 < len(starts) else total
        print(f"{clock(starts[i])}\t{end - starts[i]:.1f}s\t{beat['id']}\t{beat['title']}")


if __name__ == "__main__":
    main()
