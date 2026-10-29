# upload-pack

A Claude Code skill that turns a finished video folder into a YouTube upload pack: three title options,
a description, chapters, tags and SRT captions. Captions and chapter times come from bundled scripts,
not from the model, so they line up with the real video.

## Install

Copy the whole `upload-pack` folder (with `references/` and `scripts/`):

- **Personal use**, available in every project:
  ```bash
  cp -R upload-pack ~/.claude/skills/
  ```
- **One project**, shared with everyone who clones it:
  ```bash
  cp -R upload-pack your-project/.claude/skills/
  ```

Make sure the scripts are executable (`chmod +x upload-pack/scripts/*`). You need `python3` (standard library
only) and `ffprobe` from ffmpeg (`brew install ffmpeg`) to measure the real video length.

The skill always reads `videos/` in the project you run Claude Code from, even when it is installed in
`~/.claude/skills/`.

## Folder layout

```
videos/
  video-01/
    video-01-explainer-script.md   # the script: source of truth for every claim
    timing.json                    # voiceover beats and word timings
    edits.json                     # optional: clips inserted after the voiceover
    video-01.mp4                   # the final render (a symlink is fine)
    upload/                        # written by the skill
```

## Make it yours: three lines to change

Everything about the channel lives in `references/channel-style.md`. Change these three lines:

1. **Line 1, the heading:** `# Loficode Cafe channel style` → your channel's name.
2. **Line 3, the channel name and pitch:**
   `Channel name: **Loficode Cafe**. Calm, practical videos about building things with code and AI tools.`
   → your name and a one-sentence description of what your videos are. This sets the tone of every title and hook.
3. **Line 29, the AI voice disclosure:**
   `> Voice: my own voice, cloned with ElevenLabs (AI-generated narration). The script, testing and results are mine.`
   → your own wording and voice tool. If you don't use an AI voice, replace it with the disclosure you do need.
   Don't delete the line: the skill puts it in every description.

The rest of the file (no clickbait, real numbers only, keyword-first titles) is meant to work for any channel.

## Example run

```
> /upload-pack episode 1
```

The argument can be `video-01`, `1`, `ep1` or `episode 1`. With no argument, the skill uses the only folder under
`videos/` if there is exactly one, and otherwise lists the folders and stops.

The skill checks the real video length against the voiceover timing plus inserts, and stops to ask if they differ by
more than a second. Then it writes `videos/video-01/upload/` and reports:

```
Duration: real 188.21s vs expected 188.36s (timing.json 183.36s + 5.00s intro insert)

Titles:
  Claude Code motion graphics: 10 prompts, 2 real bugs, about 50 min   (66)
  Claude Code + Remotion: I made an intro without After Effects        (61)
  Remotion and Claude Code: a glitch intro, and where it broke         (60)

Tags: 287 characters. Captions: 75 cues, longest line 42 characters.

Merged chapters: "The problem" (9.8s) into "First prompt, then a soft glitch" (YouTube needs 10s minimum).
Placeholders: "Remotion skills for Claude Code: <add link>" in description.md.
```

The upload folder then contains `title.txt`, `description.md`, `chapters.txt`, `tags.txt` and `captions.srt`.
