from math import hypot

import cv2


class MouthDetector:
    # Extremos horizontales de la boca.
    LEFT_CORNER = 78
    RIGHT_CORNER = 308

    # Labio superior e inferior internos.
    UPPER_LIP = 13
    LOWER_LIP = 14

    MOUTH_POINTS = (
        LEFT_CORNER,
        UPPER_LIP,
        RIGHT_CORNER,
        LOWER_LIP,
    )

    def get_mouth_points(
        self,
        landmarks,
        frame,
    ):
        height, width = frame.shape[:2]

        points = []

        for index in self.MOUTH_POINTS:
            landmark = landmarks[index]

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            points.append((x, y))

        return points

    def calculate_mar(
        self,
        mouth_points,
    ) -> float:
        """
        MAR = distancia vertical / distancia horizontal.
        """

        left_corner = mouth_points[0]
        upper_lip = mouth_points[1]
        right_corner = mouth_points[2]
        lower_lip = mouth_points[3]

        vertical_distance = self._distance(
            upper_lip,
            lower_lip,
        )

        horizontal_distance = self._distance(
            left_corner,
            right_corner,
        )

        if horizontal_distance == 0:
            return 0.0

        return vertical_distance / horizontal_distance

    def draw_mouth(
        self,
        frame,
        mouth_points,
    ) -> None:
        left_corner = mouth_points[0]
        upper_lip = mouth_points[1]
        right_corner = mouth_points[2]
        lower_lip = mouth_points[3]

        for point in mouth_points:
            cv2.circle(
                frame,
                point,
                3,
                (255, 0, 255),
                -1,
            )

        cv2.line(
            frame,
            left_corner,
            right_corner,
            (255, 0, 255),
            1,
        )

        cv2.line(
            frame,
            upper_lip,
            lower_lip,
            (255, 0, 255),
            1,
        )

    @staticmethod
    def _distance(
        point_a,
        point_b,
    ) -> float:
        return hypot(
            point_a[0] - point_b[0],
            point_a[1] - point_b[1],
        )