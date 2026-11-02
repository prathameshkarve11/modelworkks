
import cv2
import threading

from ultralytics import YOLO

from config import (
    CAMERA_INDEX,
    YOLO_CONFIDENCE,
    YOLO_IMAGE_SIZE,
    YOLO_MODEL,
)


class VisionSystem:

    def __init__(self):
        print("Loading YOLO26...")
        self.yolo = YOLO(YOLO_MODEL)

        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError("Could not open camera.")

        self.latest_frame = None
        self.detected_objects = []

        self.running = False
        self.listen_requested = threading.Event()
        self.lock = threading.Lock()

        self.thread = None

    def vision_loop(self):

        cv2.namedWindow("AVAQ V3", cv2.WINDOW_NORMAL)

        try:
            while self.running:

                success, frame = self.cap.read()

                if not success:
                    print("Camera frame could not be read.")
                    break

                results = self.yolo(
                    frame,
                    verbose=False,
                    imgsz=YOLO_IMAGE_SIZE,
                )

                result = results[0]
                objects = []

                for box in result.boxes:

                    confidence = float(box.conf[0])

                    if confidence >= YOLO_CONFIDENCE:
                        class_id = int(box.cls[0])
                        name = self.yolo.names[class_id]
                        objects.append(name)

                with self.lock:
                    self.detected_objects = list(set(objects))
                    self.latest_frame = frame.copy()

                annotated = result.plot()

                cv2.putText(
                    annotated,
                    "AVAQ - PRESS SPACE TO ASK",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )

                cv2.imshow("AVAQ V3", annotated)

                key = cv2.waitKey(1) & 0xFF

                if key == ord(" "):
                    self.listen_requested.set()

                elif key == ord("q"):
                    break

        finally:
            self.running = False
            cv2.destroyAllWindows()

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self.vision_loop,
            daemon=True,
        )

        self.thread.start()

    def get_latest_frame(self):

        with self.lock:
            if self.latest_frame is None:
                return None

            return self.latest_frame.copy()

    def get_detected_objects(self):

        with self.lock:
            return self.detected_objects.copy()

    def stop(self):

        self.running = False

        if self.thread is not None:
            self.thread.join(timeout=2)

        self.cap.release()
        cv2.destroyAllWindows()
