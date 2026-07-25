from time import perf_counter

import cv2

from alarms.alarm_manager import AlarmManager
from capture.capture_manager import CaptureManager
from config import (
    CAMERA_INDEX,
    DROWSINESS_TIME_SECONDS,
    EAR_THRESHOLD,
    FATIGUE_ALERT_THRESHOLD,
    FATIGUE_ATTENTION_THRESHOLD,
    FATIGUE_CRITICAL_THRESHOLD,
    FATIGUE_DECAY_PER_SECOND,
    FATIGUE_EYE_ALERT_POINTS,
    FATIGUE_YAWN_POINTS,
    FPS,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    MAR_THRESHOLD,
    WINDOW_NAME,
    YAWN_LIMIT,
    YAWN_TIME_SECONDS,
    YAWN_WINDOW_SECONDS,
)
from detector.drowsiness import DrowsinessDetector
from detector.eye_detector import EyeDetector
from detector.face_landmarker import FaceLandmarkerDetector
from detector.fatigue_detector import FatigueDetector
from detector.mouth_detector import MouthDetector
from detector.yawn_detector import YawnDetector
from logging_manager.log_manager import LogManager
from report.session_report import SessionReport
from ui import Interface


class Camera:
    """
    Administra la cámara, los detectores, las capturas,
    la interfaz y el reporte final de la sesión.
    """

    YAWN_MESSAGE_SECONDS = 2.0

    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(
            CAMERA_INDEX,
            cv2.CAP_DSHOW,
        )

        self.face_detector = FaceLandmarkerDetector()
        self.eye_detector = EyeDetector()
        self.mouth_detector = MouthDetector()

        self.drowsiness_detector = DrowsinessDetector(
            ear_threshold=EAR_THRESHOLD,
            alert_time_seconds=DROWSINESS_TIME_SECONDS,
        )

        self.yawn_detector = YawnDetector(
            mar_threshold=MAR_THRESHOLD,
            yawn_time_seconds=YAWN_TIME_SECONDS,
        )

        self.fatigue_detector = FatigueDetector(
            yawn_limit=YAWN_LIMIT,
            yawn_window_seconds=YAWN_WINDOW_SECONDS,
            yawn_points=FATIGUE_YAWN_POINTS,
            eye_alert_points=FATIGUE_EYE_ALERT_POINTS,
            decay_per_second=FATIGUE_DECAY_PER_SECOND,
            attention_threshold=FATIGUE_ATTENTION_THRESHOLD,
            alert_threshold=FATIGUE_ALERT_THRESHOLD,
            critical_threshold=FATIGUE_CRITICAL_THRESHOLD,
        )

        self.interface = Interface()
        self.alarm_manager = AlarmManager()

        self.eye_capture_manager = CaptureManager()
        self.yawn_capture_manager = CaptureManager()

        self.log_manager = LogManager()
        self.session_report = SessionReport()

        self.yawn_message_until = 0.0

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            FRAME_WIDTH,
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            FRAME_HEIGHT,
        )

        self.cap.set(
            cv2.CAP_PROP_FPS,
            FPS,
        )

        self.previous_time = perf_counter()
        self.smoothed_fps = 0.0

        self.closed = False

    def start(self) -> None:
        if not self.cap.isOpened():
            print("ERROR: No se pudo abrir la cámara.")
            self.close()
            return

        print("Cámara iniciada.")
        print("Presiona Q o ESC para salir.")

        try:
            while True:
                success, camera_frame = self.cap.read()

                if not success:
                    print(
                        "ERROR: No se pudo leer la cámara."
                    )
                    break

                current_fps = self.calculate_fps()

                landmarks = self.face_detector.process(
                    camera_frame
                )

                landmarks_found = landmarks is not None

                if landmarks_found:
                    (
                        ear,
                        mar,
                        eye_result,
                        yawn_result,
                    ) = self.process_face(
                        camera_frame,
                        landmarks,
                    )
                else:
                    self.reset_detectors()

                    ear = 0.0
                    mar = 0.0

                    eye_result = (
                        self.get_empty_eye_result()
                    )

                    yawn_result = (
                        self.get_empty_yawn_result()
                    )

                eye_alert = eye_result[
                    "alert_active"
                ]

                yawn_active = yawn_result[
                    "yawn_active"
                ]

                fatigue_result = (
                    self.fatigue_detector.update(
                        yawn_active=yawn_active,
                        eye_alert=eye_alert,
                    )
                )

                yawn_count = fatigue_result[
                    "yawn_count"
                ]

                frequent_yawning = fatigue_result[
                    "frequent_yawning"
                ]

                fatigue_elevated = fatigue_result[
                    "fatigue_elevated"
                ]

                fatigue_score = fatigue_result[
                    "score"
                ]

                fatigue_level = fatigue_result[
                    "level"
                ]

                self.session_report.update_status(
                    fatigue_level=fatigue_level,
                    yawn_count=yawn_count,
                )

                if fatigue_result["new_yawn"]:
                    self.yawn_message_until = (
                        perf_counter()
                        + self.YAWN_MESSAGE_SECONDS
                    )

                show_yawn_message = (
                    perf_counter()
                    < self.yawn_message_until
                )

                self.alarm_manager.update(
                    eye_alert
                )

                self.save_eye_event(
                    frame=camera_frame,
                    eye_alert=eye_alert,
                    eye_result=eye_result,
                    ear=ear,
                    mar=mar,
                    fatigue_elevated=fatigue_elevated,
                    fatigue_level=fatigue_level,
                    yawn_count=yawn_count,
                )

                self.save_yawn_event(
                    frame=camera_frame,
                    yawn_active=yawn_active,
                    yawn_result=yawn_result,
                    ear=ear,
                    mar=mar,
                    fatigue_level=fatigue_level,
                    yawn_count=yawn_count,
                )

                (
                    interface_state,
                    interface_duration,
                ) = self.get_interface_status(
                    landmarks_found=landmarks_found,
                    eye_result=eye_result,
                    yawn_result=yawn_result,
                    fatigue_result=fatigue_result,
                    show_yawn_message=show_yawn_message,
                )

                display_frame = (
                    self.interface.create_panel(
                        camera_frame
                    )
                )

                self.interface.draw_status(
                    display_frame,
                    ear=ear,
                    mar=mar,
                    state=interface_state,
                    duration=interface_duration,
                    fps=current_fps,
                    eyes_closed=eye_result[
                        "eyes_closed"
                    ],
                    yawn_count=yawn_count,
                    yawn_limit=YAWN_LIMIT,
                    frequent_yawning=frequent_yawning,
                    eye_alert=eye_alert,
                    fatigue_elevated=fatigue_elevated,
                    fatigue_score=fatigue_score,
                    fatigue_level=fatigue_level,
                )

                cv2.imshow(
                    WINDOW_NAME,
                    display_frame,
                )

                key = cv2.waitKey(1) & 0xFF

                if key in (ord("q"), 27):
                    break

                window_visible = (
                    cv2.getWindowProperty(
                        WINDOW_NAME,
                        cv2.WND_PROP_VISIBLE,
                    )
                )

                if window_visible < 1:
                    break

        except KeyboardInterrupt:
            print()
            print(
                "Sesión interrumpida por el usuario."
            )

        except Exception as error:
            print()
            print(
                "ERROR durante la ejecución:"
            )
            print(error)

        finally:
            self.close()

    def reset_detectors(self) -> None:
        """
        Reinicia los estados instantáneos cuando
        no se detecta el rostro.
        """

        self.drowsiness_detector.reset()
        self.yawn_detector.reset()
        self.fatigue_detector.reset_face_state()

    def save_eye_event(
        self,
        frame,
        eye_alert: bool,
        eye_result: dict,
        ear: float,
        mar: float,
        fatigue_elevated: bool,
        fatigue_level: str,
        yawn_count: int,
    ) -> None:
        """
        Guarda una captura cuando inicia una alerta
        por cierre prolongado de ojos.

        La alerta siempre se cuenta como ojos cerrados.
        Si la fatiga está elevada, también se registra
        esa condición en el reporte.
        """

        if fatigue_elevated:
            capture_type = "fatiga-elevada"
            csv_event_type = "FATIGA_ELEVADA"
        else:
            capture_type = "ojos-cerrados"
            csv_event_type = "OJOS_CERRADOS"

        capture_path = (
            self.eye_capture_manager.update(
                frame,
                eye_alert,
                event_type=capture_type,
            )
        )

        if capture_path is None:
            return

        self.log_manager.save_event(
            event_type=csv_event_type,
            duration=eye_result[
                "closed_duration"
            ],
            ear=ear,
            mar=mar,
            capture_path=capture_path,
            fatigue_level=fatigue_level,
            yawn_counter=(
                f"{yawn_count} de {YAWN_LIMIT}"
            ),
        )

        self.session_report.register_eye_alert(
            fatigue_level=fatigue_level,
            yawn_count=yawn_count,
            fatigue_elevated=fatigue_elevated,
            capture_created=True,
        )

    def save_yawn_event(
        self,
        frame,
        yawn_active: bool,
        yawn_result: dict,
        ear: float,
        mar: float,
        fatigue_level: str,
        yawn_count: int,
    ) -> None:
        """
        Guarda una captura cuando inicia
        un nuevo bostezo confirmado.
        """

        capture_path = (
            self.yawn_capture_manager.update(
                frame,
                yawn_active,
                event_type="bostezo",
            )
        )

        if capture_path is None:
            return

        self.log_manager.save_event(
            event_type="BOSTEZO",
            duration=yawn_result[
                "open_duration"
            ],
            ear=ear,
            mar=mar,
            capture_path=capture_path,
            fatigue_level=fatigue_level,
            yawn_counter=(
                f"{yawn_count} de {YAWN_LIMIT}"
            ),
        )

        self.session_report.register_yawn(
            fatigue_level=fatigue_level,
            yawn_count=yawn_count,
            capture_created=True,
        )

    @staticmethod
    def get_interface_status(
        landmarks_found: bool,
        eye_result: dict,
        yawn_result: dict,
        fatigue_result: dict,
        show_yawn_message: bool,
    ) -> tuple[str, float]:
        if not landmarks_found:
            return "SIN ROSTRO", 0.0

        if fatigue_result["fatigue_elevated"]:
            return (
                "FATIGA ELEVADA",
                eye_result["closed_duration"],
            )

        if eye_result["alert_active"]:
            return (
                "SOMNOLENCIA DETECTADA",
                eye_result["closed_duration"],
            )

        if show_yawn_message:
            return (
                "BOSTEZO DETECTADO",
                yawn_result["open_duration"],
            )

        if fatigue_result["level"] == "CRITICO":
            return "FATIGA ACUMULADA", 0.0

        if fatigue_result["level"] == "ALERTA":
            return "RIESGO DE FATIGA", 0.0

        if fatigue_result["level"] == "ATENCION":
            return "ATENCION: FATIGA", 0.0

        if fatigue_result["frequent_yawning"]:
            return "ATENCION: FATIGA", 0.0

        if eye_result["eyes_closed"]:
            return (
                eye_result["state"],
                eye_result["closed_duration"],
            )

        if yawn_result["mouth_open"]:
            return (
                "BOCA ABIERTA",
                yawn_result["open_duration"],
            )

        return "DESPIERTO", 0.0

    def process_face(
        self,
        frame,
        landmarks,
    ):
        left_eye, right_eye = (
            self.eye_detector.get_eye_points(
                landmarks,
                frame,
            )
        )

        left_ear = (
            self.eye_detector.calculate_ear(
                left_eye
            )
        )

        right_ear = (
            self.eye_detector.calculate_ear(
                right_eye
            )
        )

        average_ear = (
            left_ear + right_ear
        ) / 2.0

        eye_result = (
            self.drowsiness_detector.update(
                average_ear
            )
        )

        mouth_points = (
            self.mouth_detector.get_mouth_points(
                landmarks,
                frame,
            )
        )

        mar = self.mouth_detector.calculate_mar(
            mouth_points
        )

        yawn_result = self.yawn_detector.update(
            mar
        )

        self.eye_detector.draw_eye(
            frame,
            left_eye,
        )

        self.eye_detector.draw_eye(
            frame,
            right_eye,
        )

        self.mouth_detector.draw_mouth(
            frame,
            mouth_points,
        )

        return (
            average_ear,
            mar,
            eye_result,
            yawn_result,
        )

    def calculate_fps(self) -> float:
        current_time = perf_counter()

        elapsed = (
            current_time
            - self.previous_time
        )

        self.previous_time = current_time

        if elapsed <= 0:
            return self.smoothed_fps

        instant_fps = 1.0 / elapsed

        if self.smoothed_fps == 0:
            self.smoothed_fps = instant_fps
        else:
            self.smoothed_fps = (
                0.9 * self.smoothed_fps
                + 0.1 * instant_fps
            )

        return self.smoothed_fps

    @staticmethod
    def get_empty_eye_result() -> dict:
        return {
            "state": "SIN ROSTRO",
            "eyes_closed": False,
            "closed_duration": 0.0,
            "alert_active": False,
        }

    @staticmethod
    def get_empty_yawn_result() -> dict:
        return {
            "state": "SIN ROSTRO",
            "mouth_open": False,
            "open_duration": 0.0,
            "yawn_active": False,
        }

    def close(self) -> None:
        """
        Libera los recursos y genera el reporte final.
        """

        if self.closed:
            return

        self.closed = True

        print()
        print("Finalizando sesión...")

        try:
            self.alarm_manager.stop()
        except Exception as error:
            print(
                "No se pudo detener la alarma:",
                error,
            )

        try:
            if self.cap.isOpened():
                self.cap.release()
        except Exception as error:
            print(
                "No se pudo liberar la cámara:",
                error,
            )

        try:
            self.face_detector.close()
        except Exception as error:
            print(
                "No se pudo cerrar Face Landmarker:",
                error,
            )

        cv2.destroyAllWindows()

        try:
            self.session_report.generate_report()
        except Exception as error:
            print()
            print(
                "ERROR: No se pudo generar "
                "el reporte de sesión."
            )
            print(error)