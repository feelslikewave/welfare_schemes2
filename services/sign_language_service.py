import os
import uuid
import numpy as np
import imageio
from pathlib import Path
from PIL import Image


class SignLanguageService:
    def __init__(self):
        # 🔥 Base project directory (auto-detects correctly)
        BASE_DIR = Path(__file__).resolve().parent.parent

        # 📁 Required folders inside project root
        self.op_dest = BASE_DIR / "filtered_data"   # Word GIFs (.webp)
        self.alpha_dest = BASE_DIR / "alphabet"     # Letter GIFs
        self.video_output_dir = BASE_DIR / "data" / "videos"

        # Ensure video folder exists
        self.video_output_dir.mkdir(parents=True, exist_ok=True)

        # 🔎 Load word mapping
        self.file_map = {}

        if self.op_dest.exists():
            for file in os.listdir(self.op_dest):
                if file.endswith(".webp") or file.endswith(".gif"):
                    words = file.replace(".webp", "").replace(".gif", "").split()
                    self.file_map[file] = words

        print("✅ SignLanguageService Initialized")
        print("Word GIF folder:", self.op_dest)
        print("Alphabet folder:", self.alpha_dest)
        print("Loaded word files:", len(self.file_map))

    # 🔍 Check if full word GIF exists
    def check_sim(self, word):
        for file, words in self.file_map.items():
            if word in words:
                return True, file
        return False, None

    # 🎥 Main video generation function
    def generate_video(self, text: str):
        if not text.strip():
            raise Exception("Empty text received")

        words = text.strip().upper().split()
        frames = []
        gestures_used = []

        for word in words:
            found, file = self.check_sim(word.lower())

            # ✅ If full word GIF exists
            if found:
                gestures_used.append(word)
                gif_path = self.op_dest / file

                if not gif_path.exists():
                    continue

                gif = Image.open(gif_path)

                for frame in range(getattr(gif, "n_frames", 1)):
                    gif.seek(frame)
                    frame_img = gif.convert("RGB")
                    frame_img = frame_img.resize((380, 260))
                    frames.append(np.array(frame_img))

            # 🔤 Otherwise spell letter by letter
            else:
                for char in word:
                    if not char.isalpha():
                        continue

                    gestures_used.append(char)

                    letter_path = self.alpha_dest / f"{char.lower()}_small.gif"

                    if not letter_path.exists():
                        continue

                    gif = Image.open(letter_path)

                    for frame in range(getattr(gif, "n_frames", 1)):
                        gif.seek(frame)
                        frame_img = gif.convert("RGB")
                        frame_img = frame_img.resize((380, 260))

                        # Repeat frames slightly for smoother playback
                        for _ in range(4):
                            frames.append(np.array(frame_img))

        if not frames:
            raise Exception("No frames generated — check GIF folders")

        # 🎬 Create MP4 file
        filename = f"{uuid.uuid4().hex}.mp4"
        video_path = self.video_output_dir / filename

        imageio.mimsave(video_path, frames, fps=10)

        duration = round(len(frames) / 10, 2)

        return {
            "filename": filename,
            "duration": duration,
            "words_count": len(words),
            "gestures_used": gestures_used
        }
