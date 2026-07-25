from time import monotonic


class DrowsinessDetector:
    def __init__(
        self,
        ear_threshold: float,
        alert_time_seconds: float,
    ) -> None:
        self.ear_threshold = ear_threshold
        self.alert_time_seconds = alert_time_seconds

        self.closed_eyes_start_time: float | None = None
        self.closed_eyes_duration = 0.0
        self.alert_active = False

    def update(self, ear: float) -> dict:
        current_time = monotonic()
        eyes_closed = ear < self.ear_threshold

        if eyes_closed:
            if self.closed_eyes_start_time is None:
                self.closed_eyes_start_time = current_time

            self.closed_eyes_duration = (
                current_time - self.closed_eyes_start_time
            )

            self.alert_active = (
                self.closed_eyes_duration >= self.alert_time_seconds
            )

            if self.alert_active:
                state = "ALERTA"
            else:
                state = "OJOS CERRADOS"

        else:
            self.reset()
            state = "DESPIERTO"

        return {
            "state": state,
            "eyes_closed": eyes_closed,
            "closed_duration": self.closed_eyes_duration,
            "alert_active": self.alert_active,
        }

    def reset(self) -> None:
        self.closed_eyes_start_time = None
        self.closed_eyes_duration = 0.0
        self.alert_active = False