from math import hypot

import cv2


class EyeDetector:
    # Seis puntos por ojo:
    # extremo izquierdo, superior izquierdo, superior derecho,
    # extremo derecho, inferior derecho, inferior izquierdo.
    LEFT_EYE = (33, 160, 158, 133, 153, 144)
    RIGHT_EYE = (362, 385, 387, 263, 373, 380)

    @staticmethod
    def landmark_to_pixel(landmark, frame_width: int, frame_height: int):
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)
        return x, y

    def get_eye_points(self, landmarks, frame):
        frame_height, frame_width = frame.shape[:2]

        left_eye = [
            self.landmark_to_pixel(
                landmarks[index],
                frame_width,
                frame_height,
            )
            for index in self.LEFT_EYE
        ]

        right_eye = [
            self.landmark_to_pixel(
                landmarks[index],
                frame_width,
                frame_height,
            )
            for index in self.RIGHT_EYE
        ]

        return left_eye, right_eye

    @staticmethod
    def calculate_ear(eye_points) -> float:
        p1, p2, p3, p4, p5, p6 = eye_points

        vertical_1 = hypot(
            p2[0] - p6[0],
            p2[1] - p6[1],
        )

        vertical_2 = hypot(
            p3[0] - p5[0],
            p3[1] - p5[1],
        )

        horizontal = hypot(
            p1[0] - p4[0],
            p1[1] - p4[1],
        )

        if horizontal == 0:
            return 0.0

        return (vertical_1 + vertical_2) / (2.0 * horizontal)

    @staticmethod
    def draw_eye(frame, eye_points) -> None:
        for point in eye_points:
            cv2.circle(frame, point, 3, (0, 255, 255), -1)

        cv2.line(frame, eye_points[0], eye_points[3], (255, 0, 0), 1)
        cv2.line(frame, eye_points[1], eye_points[5], (0, 255, 0), 1)
        cv2.line(frame, eye_points[2], eye_points[4], (0, 255, 0), 1)