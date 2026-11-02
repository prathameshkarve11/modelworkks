
import subprocess

from config import SARAH_TTS


def speak_sarah(text):

    if not text or not text.strip():
        return

    print("\n🔊 Sarah is speaking...")

    try:
        subprocess.run(
            [
                str(SARAH_TTS),
                "CONIN$",
                "--stream",
                "--lang",
                "en-us",
                "--voice",
                "af_sarah"
            ],
            input=text.strip(),
            text=True,
            check=True
        )

    except Exception as e:
        print(f"Sarah TTS error: {e}")
