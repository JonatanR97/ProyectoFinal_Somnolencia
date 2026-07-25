import threading
import time
import winsound


class SoundAlarm:
    def __init__(
        self,
        frequency: int = 2000,
        duration_ms: int = 500,
        pause_seconds: float = 0.15,
    ) -> None:
        self.frequency = frequency
        self.duration_ms = duration_ms
        self.pause_seconds = pause_seconds

        self._active = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._active:
            return

        self._active = True

        self._thread = threading.Thread(
            target=self._play_loop,
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._active = False

    def _play_loop(self) -> None:
        while self._active:
            winsound.Beep(
                self.frequency,
                self.duration_ms,
            )

            time.sleep(self.pause_seconds)