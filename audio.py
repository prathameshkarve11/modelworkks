
import sounddevice as sd
import numpy as np

from faster_whisper import WhisperModel

from config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    SAMPLE_RATE,
    BLOCK_DURATION,
    MAX_RECORDING_SECONDS,
    SILENCE_SECONDS,
    SPEECH_THRESHOLD,
)


class AudioSystem:

    def __init__(self):

        print("Loading Whisper...")

        self.whisper = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )

    def listen_for_question(self):

        print("\n🟢 AVAQ AWAKE!")
        print("🎤 Ask your question...")

        samplerate = SAMPLE_RATE

        block_size = int(
            samplerate * BLOCK_DURATION
        )

        max_blocks = int(
            MAX_RECORDING_SECONDS / BLOCK_DURATION
        )

        silence_blocks_needed = int(
            SILENCE_SECONDS / BLOCK_DURATION
        )

        recorded = []

        silence_blocks = 0
        speech_started = False

        print("🎤 Listening...")

        with sd.InputStream(
            samplerate=samplerate,
            channels=1,
            dtype="float32",
            blocksize=block_size,
        ) as mic:

            for _ in range(max_blocks):

                audio_block, overflowed = mic.read(
                    block_size
                )

                audio_block = np.squeeze(audio_block)

                recorded.append(
                    audio_block.copy()
                )

                volume = np.sqrt(
                    np.mean(audio_block ** 2)
                )

                if volume > SPEECH_THRESHOLD:

                    speech_started = True
                    silence_blocks = 0

                elif speech_started:

                    silence_blocks += 1

                    if silence_blocks >= silence_blocks_needed:
                        break

        if not recorded:
            return ""

        audio_data = np.concatenate(recorded)

        if len(audio_data) == 0:
            return ""

        print("🧠 Understanding...")

        segments, info = self.whisper.transcribe(
            audio_data,
            language="en",
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 500
            },
            beam_size=5,
            condition_on_previous_text=False,
        )

        question = ""

        for segment in segments:
            question += segment.text

        question = question.strip()

        print(f"\nYOU:\n{question}")

        return question
