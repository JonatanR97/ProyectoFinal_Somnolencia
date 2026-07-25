from pathlib import Path
import csv
from datetime import datetime


class LogManager:
    def __init__(self):
        self.logs_folder = Path("logs")
        self.logs_folder.mkdir(exist_ok=True)

        self.csv_path = self.logs_folder / "registro.csv"

        if not self.csv_path.exists():
            with open(
                self.csv_path,
                "w",
                newline="",
                encoding="utf-8",
            ) as file:

                writer = csv.writer(
                    file,
                    delimiter=";"
                )

                writer.writerow(
                    [
                        "Fecha",
                        "Hora",
                        "Tipo",
                        "Duracion (s)",
                        "EAR",
                        "MAR",
                        "Nivel",
                        "Bostezos",
                        "Captura",
                    ]
                )

    def save_event(
        self,
        event_type,
        duration,
        ear,
        mar,
        capture_path,
        fatigue_level="NORMAL",
        yawn_counter="0/3",
    ):
        now = datetime.now()

        with open(
            self.csv_path,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(
                file,
                delimiter=";"
            )

            writer.writerow(
                [
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    event_type,
                    round(duration, 2),
                    round(ear, 3),
                    round(mar, 3),
                    fatigue_level,
                    yawn_counter,
                    Path(capture_path).name,
                ]
            )

        print(
            "[REGISTRO] Evento guardado en",
            self.csv_path,
        )