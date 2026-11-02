
import ollama

from config import OLLAMA_MODEL


class AvaqAssistant:

    def __init__(self):
        self.model = OLLAMA_MODEL

    def ask_question(self, question, image_path, detected_objects):

        objects_text = ", ".join(detected_objects)

        prompt = f"""
You are AVAQ, a fast local visual assistant.

YOLO detects:
{objects_text}

User:
{question}

Look at the image and answer directly.

Rules:
- Give the answer immediately.
- Maximum 1-2 short sentences.
- No reasoning.
- No explanations unless requested.
- If unsure, say you are unsure.
"""

        print("\n🧠 Qwen is thinking...")

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [
                        str(image_path)
                    ],
                }
            ],
        )

        answer = response["message"]["content"]

        return answer
