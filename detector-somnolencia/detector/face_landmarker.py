from time import monotonic

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    MIN_FACE_DETECTION_CONFIDENCE,
    MIN_FACE_PRESENCE_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MODEL_PATH,
)


class FaceLandmarkerDetector:
    def __init__(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo de MediaPipe en: {MODEL_PATH}"
            )

        base_options = python.BaseOptions(
            model_asset_path=str(MODEL_PATH)
        )

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=MIN_FACE_DETECTION_CONFIDENCE,
            min_face_presence_confidence=MIN_FACE_PRESENCE_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )

        self.landmarker = vision.FaceLandmarker.create_from_options(options)
        self.start_time = monotonic()
        self.last_timestamp_ms = -1

    def process(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=frame_rgb,
        )

        timestamp_ms = int((monotonic() - self.start_time) * 1000)

        # MediaPipe exige timestamps crecientes.
        if timestamp_ms <= self.last_timestamp_ms:
            timestamp_ms = self.last_timestamp_ms + 1

        self.last_timestamp_ms = timestamp_ms

        result = self.landmarker.detect_for_video(
            mp_image,
            timestamp_ms,
        )

        if not result.face_landmarks:
            return None

        return result.face_landmarks[0]

    @staticmethod
    def draw_landmarks(frame, landmarks) -> None:
        height, width = frame.shape[:2]

        for landmark in landmarks:
            x = int(landmark.x * width)
            y = int(landmark.y * height)

            if 0 <= x < width and 0 <= y < height:
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    def close(self) -> None:
        self.landmarker.close()