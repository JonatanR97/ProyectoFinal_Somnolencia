from datetime import datetime
from pathlib import Path

import cv2


class CaptureManager:
    def __init__(self) -> None:
        self.capture_folder = Path("captures")
        self.capture_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.event_saved = False

    def update(
        self,
        frame,
        alert_active: bool,
        event_type: str = "ojos-cerrados",
    ) -> str | None:
        """
        Guarda una sola captura por evento.

        Devuelve la ruta de la imagen cuando se guarda.
        Devuelve None cuando no se genera una captura nueva.
        """

        if alert_active and not self.event_saved:
            capture_path = self.save_capture(
                frame,
                event_type,
            )

            self.event_saved = True
            return capture_path

        if not alert_active:
            self.event_saved = False

        return None

    def save_capture(
        self,
        frame,
        event_type: str,
    ) -> str | None:
        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        clean_event_type = (
            event_type.strip()
            .lower()
            .replace(" ", "-")
            .replace("_", "-")
        )

        filename = (
            f"{timestamp}_{clean_event_type}.jpg"
        )

        capture_path = self.capture_folder / filename

        saved = cv2.imwrite(
            str(capture_path),
            frame,
        )

        if not saved:
            print(
                "[CAPTURA] ERROR: No se pudo guardar "
                f"la imagen: {capture_path}"
            )
            return None

        print(
            f"[CAPTURA] Imagen guardada: {capture_path}"
        )

        return str(capture_path)