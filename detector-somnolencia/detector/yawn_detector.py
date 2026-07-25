from time import perf_counter


class YawnDetector:
    def __init__(
        self,
        mar_threshold: float,
        yawn_time_seconds: float,
    ) -> None:
        self.mar_threshold = mar_threshold
        self.yawn_time_seconds = yawn_time_seconds

        self.open_start_time = None
        self.yawn_active = False

    def update(
        self,
        mar: float,
    ) -> dict:
        mouth_open = mar >= self.mar_threshold

        if mouth_open:
            if self.open_start_time is None:
                self.open_start_time = perf_counter()

            open_duration = (
                perf_counter()
                - self.open_start_time
            )

            self.yawn_active = (
                open_duration
                >= self.yawn_time_seconds
            )

        else:
            open_duration = 0.0
            self.open_start_time = None
            self.yawn_active = False

        if self.yawn_active:
            state = "BOSTEZO DETECTADO"
        elif mouth_open:
            state = "BOCA ABIERTA"
        else:
            state = "BOCA CERRADA"

        return {
            "state": state,
            "mouth_open": mouth_open,
            "open_duration": open_duration,
            "yawn_active": self.yawn_active,
        }

    def reset(self) -> None:
        self.open_start_time = None
        self.yawn_active = False