#!/usr/bin/env bash
# Resolve a video folder under videos/ and print two lines:
#   folder: video-NN
#   duration: <seconds of the first .mp4, or "no video file">
# Exits non-zero with a reason if no folder matches or the video can't be measured.
set -u

# Accept "video-01", "1", "01", "ep1" or "episode 1" (possibly split across args).
arg="$*"
# Resolve videos/ from the project root, not the caller's working directory.
root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../../../.." && pwd)}"

note=""
folder="$arg"
if [ -z "$arg" ]; then
  # No argument: use the only folder under videos/, or list them and stop.
  folders=$(find "$root/videos" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null | sort)
  count=$(printf '%s' "$folders" | grep -c .)
  if [ "$count" -ne 1 ]; then
    list=$(printf '%s' "$folders" | tr '\n' ' ' | sed 's/ $//')
    echo "no folder given and $count folders under videos/ (pass one): ${list:-none}"
    exit 1
  fi
  folder="$folders"
  note=" (no argument given; using the only folder under videos/)"
elif [ ! -d "$root/videos/$folder" ]; then
  num=$(printf '%s' "$arg" | grep -oE '[0-9]+' | tail -n 1)
  if [ -n "$num" ]; then
    folder=$(printf 'video-%02d' "$((10#$num))")
  fi
fi
dir="$root/videos/$folder"

if [ ! -d "$dir" ]; then
  existing=$(ls -1 "$root/videos" 2>/dev/null | tr '\n' ' ')
  echo "no video folder matches \"$arg\"; folders under videos/: ${existing:-none}"
  exit 1
fi
echo "folder: $folder$note"

f=$(find "$dir" -maxdepth 1 -name '*.mp4' \( -type f -o -type l \) | sort | head -n 1)
if [ -z "$f" ]; then
  echo "duration: no video file"
  exit 0
fi

real=$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$f")
if [ ! -f "$real" ]; then
  echo "duration: broken symlink: $(basename "$f") -> $real"
  exit 1
fi

if ! command -v ffprobe >/dev/null 2>&1; then
  echo "duration: ffprobe not found (brew install ffmpeg)"
  exit 1
fi

if ! out=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$real" 2>&1) || [ -z "$out" ]; then
  echo "duration: ffprobe failed on $real: $out"
  exit 1
fi
echo "duration: $out"
