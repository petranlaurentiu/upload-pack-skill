---
name: upload-pack
description: Prepare a YouTube upload pack (titles, description, chapters, tags, SRT captions) for a video folder under videos/. Use when the user wants to get a video ready to upload, or asks for its title, description, chapters, tags or captions.
argument-hint: "[video-folder | episode-number]"
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/resolve.sh *) Bash(python3 *) Read Write
---

# Upload pack for `$ARGUMENTS`

## Context

- Resolved folder and real video duration (seconds): !`${CLAUDE_SKILL_DIR}/scripts/resolve.sh $ARGUMENTS`

If there is no `folder:` line, no folder matched: stop and show the user that line (it lists the folders under `videos/`).
If the `duration:` line is an error (ffprobe failed, broken symlink, not found), stop and show it to the user.

`FOLDER` below means the name on the `folder:` line (e.g. `video-01`), without any note in parentheses after it.
Use it for every path, never the raw argument: the user may have typed `1`, `ep1` or `episode 1`.
If the `folder:` line says no argument was given, tell the user which folder was picked.

## Inputs

- `videos/FOLDER/*.md`: the script. The source of truth for what the video says and claims.
- `videos/FOLDER/timing.json`: `{duration, beats[{id,title,start,end,text}], words[{w,s,e,b}]}`.
  `b` is the 0-based beat index of each word. Times are from the voiceover, before video edits.
- `videos/FOLDER/edits.json` (optional): clips inserted into the video after the voiceover,
  `{"inserts": [{"at": 3.46, "duration": 5.0, "label": "intro clip", "caption": "[intro plays]"}]}`.
  Everything at or after `at` (timing.json seconds) is `duration` seconds later in the real video.

Below, `EDITS` means `"videos/FOLDER/edits.json"` if that file exists, and nothing otherwise.

Before writing anything:

1. Read the script and `timing.json`.
2. Read `references/channel-style.md` (in this skill's folder: `${CLAUDE_SKILL_DIR}/references/channel-style.md`).
   It governs every piece of text you write (titles, description, tags). Read it before drafting, not after.
3. Get the expected duration and shifted beat starts:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/beats.py" "videos/FOLDER/timing.json" EDITS`
4. Compare the real duration with the expected duration from step 3.
   - Differ by more than 1 second: **stop and ask the user** (likely a missing or wrong insert in
     `edits.json`). Write nothing until they answer.
   - "no video file": say so, and continue with the expected duration.

## Outputs

Write everything to `videos/FOLDER/upload/` (create it). Overwrite existing files there.

### captions.srt

Run the bundled script; do not write captions by hand:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/make_srt.py" "videos/FOLDER/timing.json" "videos/FOLDER/upload/captions.srt" EDITS
```

It shifts words past each insert, adds a caption for each insert, splits cues on sentence ends and beat
changes, wraps to at most 2 lines of 42 characters, and prints a summary. If it reports a line over 42
characters or exits non-zero, show the user the output.

### chapters.txt

One line per beat, in order: `M:SS Title`, using the starts and lengths printed by `beats.py` in step 3
(already shifted for inserts and rounded down). Never compute starts from raw `timing.json`.
- The first line is always `0:00`. `beats.py` switches to `H:MM:SS` for videos an hour or longer.
- YouTube needs at least 3 chapters, each at least 10 seconds long. If a beat is shorter, merge it into the
  previous chapter and tell the user.
- Beat titles may be internal labels; rewrite unclear ones into short viewer-facing titles that match the beat text.

### title.txt

Three options, one per line, no numbering. Each one:
- starts with the main search keyword (the tool or topic a viewer would type into search),
- is under 70 characters (count them),
- makes only claims the script backs up.

### description.md

In this order:
1. **Hook**: 2 lines. The first line carries the search keyword. Both lines must be true to the video.
2. **Chapters**: the exact contents of `chapters.txt`.
3. **What I used**: one bullet per tool, product or service named in the script, with its official link.
   Use only URLs you are certain are official. If unsure, write `<add link>` and list it for the user.
4. **AI voice disclosure**: one line, worded as in `references/channel-style.md`.

### tags.txt

Comma-separated, one line, under 500 characters total including commas and spaces. Most specific first
(tool names, exact topic), then broader topics. No tags for things the video doesn't cover.

## Finish

Report to the user:
- the real vs expected duration (timing.json + inserts), or "no video file",
- the three titles with their character counts,
- tags character count and caption cue count,
- any `<add link>` placeholders, merged chapters, or claims you softened to stay honest.
