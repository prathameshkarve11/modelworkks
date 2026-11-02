
from pathlib import Path

import cv2

from vision import VisionSystem
from audio import AudioSystem
from assistant import AvaqAssistant
from tts import speak_sarah

from config import LIVE_FRAME_PATH


def main():

    print("========================================")
    print("          AVAQ V3 STARTING")
    print("========================================")

    vision = VisionSystem()
    audio = AudioSystem()
    assistant = AvaqAssistant()

    vision.start()

    print("\n========================================")
    print("          AVAQ IS READY")
    print("========================================")
    print("Press SPACE on the camera window to ask Avaq.")
    print("Press Q on the camera window to quit.")

    try:

        while vision.running:

            if not vision.listen_requested.wait(timeout=0.1):
                continue

            vision.listen_requested.clear()

            if not vision.running:
                break

            print("\n🔥 SPACE PRESSED!")
            print("🎤 AVAQ is listening...")

            question = audio.listen_for_question()

            if not question:
                print("❌ I didn't hear a question.")
                print("👂 Going back to sleep...")
                continue

            frame = vision.get_latest_frame()

            if frame is None:
                print("No camera frame available.")
                continue

            cv2.imwrite(
                str(LIVE_FRAME_PATH),
                frame,
            )

            detected_objects = vision.get_detected_objects()

            answer = assistant.ask_question(
                question,
                LIVE_FRAME_PATH,
                detected_objects,
            )

            print("\n========================================")
            print("                  AVAQ")
            print("========================================")
            print(answer)
            print("========================================")

            speak_sarah(answer)

            print("\n🔴 AVAQ sleeping...")

    except KeyboardInterrupt:
        print("\nAVAQ interrupted.")

    finally:
        vision.stop()
        print("\nAVAQ stopped.")


if __name__ == "__main__":
    main()
