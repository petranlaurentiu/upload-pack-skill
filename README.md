# upload-pack: a Claude Code skill for YouTube uploads

One command turns a finished video into everything you need to upload it: three title options, a description, chapters, tags, and SRT captions timed to the word.

```
> /upload-pack episode 1
```

Built and tested on camera, bugs included, in **[Claude Code Skills Tutorial: I Automated My YouTube Uploads](<VIDEO LINK>)** on LoFi Code Cafe.

## Quick start

```bash
git clone https://github.com/petranlaurentiu/upload-pack-skill.git
cp -R upload-pack-skill/upload-pack your-project/.claude/skills/
```

Then put each video in `your-project/videos/<name>/` with a script `.md` and a `timing.json` (see `examples/videos/video-01/`), open Claude Code in `your-project`, and run `/upload-pack <name>`, or just ask it to "prep the YouTube stuff for episode 1".

Full install notes, the folder layout and the three lines to change for your own channel are in [upload-pack/README.md](upload-pack/README.md).

## What's inside

| File | What it does |
|---|---|
| `upload-pack/SKILL.md` | The skill: when to use it, the steps, the output rules |
| `upload-pack/references/channel-style.md` | Your channel's voice and honesty rules (edit this) |
| `upload-pack/scripts/resolve.sh` | Turns `1`, `ep1`, `episode 1` or `video-01` into a folder, and measures the real video with ffprobe |
| `upload-pack/scripts/make_srt.py` | Builds captions from word timestamps, max 42 chars per line |
| `upload-pack/scripts/beats.py` | Chapter times, shifted for clips inserted after the voiceover (`edits.json`) |
| `examples/videos/video-01/` | A small made-up example to try it on |

## Build your own instead

This is the prompt that created the first version of the skill in the video. Paste it into Claude Code and change the outputs to whatever your workflow needs:

```
Create a project skill at .claude/skills/upload-pack/ that prepares everything I need to upload a YouTube video.

Input: a folder name under videos/ (e.g. video-01). Each folder has a script .md and a timing.json with word timestamps: {duration, beats[{id,title,start,end,text}], words[{w,s,e,b}]}.

Output into videos/<name>/upload/:
- title.txt: 3 title options, search keyword first, under 70 characters
- description.md: 2-line hook, chapters, a "what I used" section with links, an AI-voice disclosure line
- chapters.txt: one line per beat, M:SS format, first one at 0:00
- tags.txt: comma-separated, under 500 characters
- captions.srt: built by a bundled Python script from timing.json, max 42 chars per line, split on sentence ends

Requirements:
- SKILL.md frontmatter: name, a description, argument-hint "[video-folder]", arguments: [video]
- Use $video for the folder
- Use !`ffprobe` dynamic context to read the real duration of videos/$video/*.mp4 if one exists, otherwise say "no video file"
- Put the SRT logic in scripts/make_srt.py and call it with ${CLAUDE_SKILL_DIR}
- Put my channel style rules in references/channel-style.md and tell SKILL.md when to read it: Loficode Cafe, honest, no clickbait claims the video doesn't back up, always disclose AI voice
- Keep SKILL.md under 100 lines

Don't run it yet. Show me the file tree when you're done.
```

The video then fixes four real bugs in what this prompt produces. The finished versions are the files in this repo.

## Requirements

- Claude Code (needs a paid Claude plan)
- `python3` (standard library only)
- `ffprobe` from ffmpeg, to check the real video length (`brew install ffmpeg`)

## License

MIT. See [LICENSE](LICENSE).
