import cv2
import numpy as np

from config import PANEL_WIDTH


class Interface:
    # Colores BGR utilizados por OpenCV
    WHITE = (255, 255, 255)
    GRAY = (170, 170, 170)
    DARK_GRAY = (55, 55, 55)

    GREEN = (0, 255, 0)
    YELLOW = (0, 255, 255)
    ORANGE = (0, 165, 255)
    RED = (0, 0, 255)
    MAGENTA = (255, 0, 255)

    def create_panel(self, camera_frame):
        """
        Agrega un panel negro a la izquierda
        del fotograma de la cámara.
        """
        frame_height, frame_width = camera_frame.shape[:2]

        display_frame = np.zeros(
            (
                frame_height,
                frame_width + PANEL_WIDTH,
                3,
            ),
            dtype=np.uint8,
        )

        display_frame[
            :,
            PANEL_WIDTH:PANEL_WIDTH + frame_width,
        ] = camera_frame

        return display_frame

    def draw_status(
        self,
        frame,
        ear: float,
        mar: float,
        state: str,
        duration: float,
        fps: float,
        eyes_closed: bool,
        yawn_count: int,
        yawn_limit: int,
        frequent_yawning: bool,
        eye_alert: bool,
        fatigue_elevated: bool,
        fatigue_score: float,
        fatigue_level: str,
    ) -> None:
        """
        Dibuja la información principal del sistema.

        fatigue_score se conserva en los parámetros
        para mantener compatibilidad con camera.py,
        aunque ya no se muestra como barra.
        """

        state_color = self._get_state_color(
            state=state,
            eyes_closed=eyes_closed,
            frequent_yawning=frequent_yawning,
            eye_alert=eye_alert,
            fatigue_elevated=fatigue_elevated,
        )

        level_color = self._get_level_color(
            fatigue_level
        )

        self._draw_header(frame)

        # EAR
        self._draw_label(
            frame,
            text="EAR",
            y=145,
        )

        ear_color = (
            self.RED
            if eyes_closed
            else self.GREEN
        )

        self._draw_value(
            frame,
            text=f"{ear:.3f}",
            y=183,
            color=ear_color,
        )

        # MAR
        self._draw_label(
            frame,
            text="MAR",
            y=225,
        )

        mar_color = (
            self.MAGENTA
            if mar >= 0.25
            else self.GREEN
        )

        self._draw_value(
            frame,
            text=f"{mar:.3f}",
            y=263,
            color=mar_color,
        )

        # Contador real de bostezos
        self._draw_label(
            frame,
            text="BOSTEZOS RECIENTES",
            y=305,
        )

        yawn_color = (
            self.YELLOW
            if frequent_yawning
            else self.WHITE
        )

        self._draw_value(
            frame,
            text=f"{yawn_count} / {yawn_limit}",
            y=343,
            color=yawn_color,
        )

        # Estado general
        self._draw_label(
            frame,
            text="ESTADO",
            y=385,
        )

        self._draw_state(
            frame,
            state=state,
            y=423,
            color=state_color,
        )

        # Nivel de fatiga
        self._draw_label(
            frame,
            text="NIVEL",
            y=465,
        )

        self._draw_value(
            frame,
            text=fatigue_level,
            y=503,
            color=level_color,
            font_scale=0.68,
        )

        # Tiempo del evento actual
        self._draw_label(
            frame,
            text="TIEMPO DEL EVENTO",
            y=545,
        )

        self._draw_value(
            frame,
            text=f"{duration:.2f} s",
            y=583,
            color=state_color,
        )

        # FPS
        self._draw_label(
            frame,
            text="FPS",
            y=625,
        )

        self._draw_value(
            frame,
            text=f"{fps:.1f}",
            y=663,
            color=self.WHITE,
        )

        self._draw_exit_message(frame)

        # El banner y la alarma visual aparecen
        # únicamente por cierre prolongado de ojos.
        if eye_alert:
            self._draw_alert_banner(
                frame,
                fatigue_elevated=fatigue_elevated,
            )

    def _draw_header(self, frame) -> None:
        cv2.putText(
            frame,
            "MONITOREO",
            (30, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.90,
            self.WHITE,
            2,
            cv2.LINE_AA,
        )

        cv2.line(
            frame,
            (25, 95),
            (PANEL_WIDTH - 25, 95),
            self.DARK_GRAY,
            1,
        )

    def _draw_label(
        self,
        frame,
        text: str,
        y: int,
    ) -> None:
        cv2.putText(
            frame,
            text,
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            self.GRAY,
            1,
            cv2.LINE_AA,
        )

    def _draw_value(
        self,
        frame,
        text: str,
        y: int,
        color,
        font_scale: float = 0.72,
    ) -> None:
        cv2.putText(
            frame,
            text,
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            2,
            cv2.LINE_AA,
        )

    def _draw_state(
        self,
        frame,
        state: str,
        y: int,
        color,
    ) -> None:
        """
        Ajusta automáticamente el tamaño del estado
        para que no salga del panel.
        """
        if len(state) >= 22:
            font_scale = 0.42
        elif len(state) >= 17:
            font_scale = 0.48
        elif len(state) >= 13:
            font_scale = 0.55
        else:
            font_scale = 0.65

        cv2.putText(
            frame,
            state,
            (30, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            2,
            cv2.LINE_AA,
        )

    def _draw_exit_message(
        self,
        frame,
    ) -> None:
        frame_height = frame.shape[0]

        cv2.putText(
            frame,
            "Q / ESC: salir",
            (30, frame_height - 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.43,
            self.GRAY,
            1,
            cv2.LINE_AA,
        )

    def _draw_alert_banner(
        self,
        frame,
        fatigue_elevated: bool,
    ) -> None:
        frame_width = frame.shape[1]

        if fatigue_elevated:
            banner_text = "FATIGA ELEVADA"
        else:
            banner_text = "SOMNOLENCIA DETECTADA"

        cv2.rectangle(
            frame,
            (PANEL_WIDTH, 0),
            (frame_width, 105),
            self.RED,
            -1,
        )

        cv2.putText(
            frame,
            banner_text,
            (PANEL_WIDTH + 45, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.95,
            self.WHITE,
            2,
            cv2.LINE_AA,
        )

    def _get_level_color(
        self,
        fatigue_level: str,
    ):
        if fatigue_level == "CRITICO":
            return self.RED

        if fatigue_level == "ALERTA":
            return self.ORANGE

        if fatigue_level == "ATENCION":
            return self.YELLOW

        return self.GREEN

    def _get_state_color(
        self,
        state: str,
        eyes_closed: bool,
        frequent_yawning: bool,
        eye_alert: bool,
        fatigue_elevated: bool,
    ):
        if fatigue_elevated or eye_alert:
            return self.RED

        if frequent_yawning:
            return self.YELLOW

        if eyes_closed:
            return self.ORANGE

        if state in (
            "BOSTEZO DETECTADO",
            "BOCA ABIERTA",
        ):
            return self.MAGENTA

        if state == "SIN ROSTRO":
            return self.GRAY

        return self.GREEN