from collections import deque
from time import perf_counter


class FatigueDetector:
    def __init__(
        self,
        yawn_limit: int,
        yawn_window_seconds: float,
        yawn_points: float,
        eye_alert_points: float,
        decay_per_second: float,
        attention_threshold: float,
        alert_threshold: float,
        critical_threshold: float,
    ) -> None:
        self.yawn_limit = yawn_limit
        self.yawn_window_seconds = yawn_window_seconds

        self.yawn_points = yawn_points
        self.eye_alert_points = eye_alert_points
        self.decay_per_second = decay_per_second

        self.attention_threshold = attention_threshold
        self.alert_threshold = alert_threshold
        self.critical_threshold = critical_threshold

        self.yawn_times = deque()

        self.previous_yawn_active = False
        self.previous_eye_alert = False

        self.score = 0.0
        self.previous_update_time = perf_counter()

    def update(
        self,
        yawn_active: bool,
        eye_alert: bool,
    ) -> dict:
        current_time = perf_counter()

        elapsed = (
            current_time
            - self.previous_update_time
        )

        self.previous_update_time = current_time

        # Reduce gradualmente el puntaje.
        self._apply_decay(elapsed)

        # Detecta únicamente el inicio de un bostezo.
        new_yawn = (
            yawn_active
            and not self.previous_yawn_active
        )

        # Detecta únicamente el inicio de una
        # alerta por ojos cerrados.
        new_eye_alert = (
            eye_alert
            and not self.previous_eye_alert
        )

        if new_yawn:
            self.yawn_times.append(current_time)

            self.score += self.yawn_points

        if new_eye_alert:
            self.score += self.eye_alert_points

        self.previous_yawn_active = yawn_active
        self.previous_eye_alert = eye_alert

        self._remove_expired_yawns(
            current_time
        )

        self.score = max(
            0.0,
            min(self.score, 100.0),
        )

        yawn_count = len(self.yawn_times)

        frequent_yawning = (
            yawn_count >= self.yawn_limit
        )

        fatigue_elevated = (
            eye_alert
            and frequent_yawning
        )

        level = self._get_level()

        return {
            "score": self.score,
            "level": level,
            "new_yawn": new_yawn,
            "new_eye_alert": new_eye_alert,
            "yawn_count": yawn_count,
            "frequent_yawning": frequent_yawning,
            "fatigue_elevated": fatigue_elevated,
        }

    def _apply_decay(
        self,
        elapsed: float,
    ) -> None:
        if elapsed <= 0:
            return

        reduction = (
            self.decay_per_second
            * elapsed
        )

        self.score = max(
            0.0,
            self.score - reduction,
        )

    def _remove_expired_yawns(
        self,
        current_time: float,
    ) -> None:
        while self.yawn_times:
            oldest_yawn = self.yawn_times[0]

            elapsed = (
                current_time
                - oldest_yawn
            )

            if elapsed <= self.yawn_window_seconds:
                break

            self.yawn_times.popleft()

    def _get_level(self) -> str:
        if self.score >= self.critical_threshold:
            return "CRITICO"

        if self.score >= self.alert_threshold:
            return "ALERTA"

        if self.score >= self.attention_threshold:
            return "ATENCION"

        return "NORMAL"

    def reset_face_state(self) -> None:
        """
        Reinicia las señales instantáneas cuando
        el rostro desaparece.

        No elimina el puntaje ni los bostezos
        recientes.
        """

        self.previous_yawn_active = False
        self.previous_eye_alert = False