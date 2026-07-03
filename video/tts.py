"""Synthesize the voiceover (ElevenLabs with word timestamps; edge-tts fallback)."""
import json
import os
import subprocess
import sys
from lib.script import load_script

VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "Gfpl8Yo74Is0W6cPUWWT")  # Skyler's chosen ElevenLabs voice


def _warn_if_stub():
    if os.environ.get("TTS_STUB"):
        print("[tts] TTS_STUB active — audio is silent, captions are NOT voice-aligned",
              file=sys.stderr)


def words_from_alignment(alignment):
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]
    words, cur, w_start = [], "", None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                words.append({"word": cur, "start": w_start, "end": prev_end})
                cur, w_start = "", None
            continue
        if not cur:
            w_start = s
        cur += c
        prev_end = e
    if cur:
        words.append({"word": cur, "start": w_start, "end": prev_end})
    return words


def _ffprobe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else 0.0


def _elevenlabs_beat(text, out_mp3):
    """Returns word list or raises."""
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    resp = client.text_to_speech.convert_with_timestamps(voice_id=VOICE_ID, text=text,
                                                          model_id="eleven_multilingual_v2")
    audio_b64 = resp.audio_base64 if hasattr(resp, "audio_base64") else resp["audio_base64"]
    import base64
    open(out_mp3, "wb").write(base64.b64decode(audio_b64))
    alignment = resp.alignment if hasattr(resp, "alignment") else resp["alignment"]
    return words_from_alignment(alignment if isinstance(alignment, dict) else alignment.__dict__)


def _edge_beat(text, out_mp3):
    subprocess.run([sys.executable, "-m", "edge_tts", "--text", text, "--write-media", out_mp3], check=True)
    return []  # edge-tts gives no word alignment


def _stub_beat(text, out_mp3):
    """Offline stub: silent audio sized to the text, with evenly-spaced word timestamps.
    Used for the credential- and network-free placeholder smoke render (TTS_STUB env)."""
    words = text.split()
    dur = max(1.5, len(words) * 0.35)
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", f"{dur}", "-q:a", "9", out_mp3], check=True, capture_output=True)
    per = dur / max(1, len(words))
    return [{"word": w, "start": round(i * per, 3), "end": round((i + 1) * per, 3)} for i, w in enumerate(words)]


def synthesize(script_path, out_mp3, out_timestamps, work="capture"):
    _warn_if_stub()
    beats = load_script(script_path)
    per_beat, mp3s = {}, []
    for b in beats:
        # id-only filename: beat order comes from script.json, so no index prefix —
        # inserting a beat never shifts another beat's cached take.
        mp3 = os.path.join(work, f"vo_{b.id}.mp3")
        if os.environ.get("TTS_STUB"):
            words = _stub_beat(b.vo, mp3)
        else:
            try:
                words = _elevenlabs_beat(b.vo, mp3)
            except Exception as exc:               # noqa: BLE001 — fall back, but surface why
                print(f"[tts] ElevenLabs failed for '{b.id}' ({exc}); falling back to edge-tts", file=sys.stderr)
                words = _edge_beat(b.vo, mp3)
        per_beat[b.id] = {"duration": _ffprobe_duration(mp3), "words": words}
        mp3s.append(mp3)
    # concat all beat mp3s into one voiceover.mp3 (ffmpeg concat demuxer)
    listfile = os.path.join(work, "vo_list.txt")
    open(listfile, "w").write("".join(f"file '{os.path.abspath(m)}'\n" for m in mp3s))
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
                    "-c", "copy", out_mp3], check=True)
    json.dump({"beats": per_beat}, open(out_timestamps, "w"), indent=2)
    print(f"wrote {out_mp3} + {out_timestamps}")


if __name__ == "__main__":
    synthesize(sys.argv[1], sys.argv[2], sys.argv[3])
