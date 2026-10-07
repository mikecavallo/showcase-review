#!/bin/sh
# finish_reel.sh <in.mp4> <out.mp4>: add the score, fade out
set -e
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1")
python3 build/music.py "$D" build/_reel_music.wav >/dev/null
ffmpeg -v error -y -i "$1" -i build/_reel_music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -af "volume=1.6,afade=t=out:st=$(python3 -c "print(max(0,$D-2.5))"):d=2.5" -shortest -movflags +faststart "$2"
echo "$2"
