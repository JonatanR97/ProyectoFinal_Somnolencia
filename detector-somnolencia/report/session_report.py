from datetime import datetime
from pathlib import Path
from time import perf_counter

from report.pdf_report import PdfReport


class SessionReport:
    """
    Registra las estadísticas principales de una sesión
    y genera reportes TXT y PDF al finalizar.
    """

    LEVEL_PRIORITY = {
        "NORMAL": 0,
        "ATENCION": 1,
        "ALERTA": 2,
        "CRITICO": 3,
    }

    LEVEL_REPLACEMENTS = {
        "ATENCIÓN": "ATENCION",
        "CRÍTICO": "CRITICO",
    }

    def __init__(self) -> None:
        self.reports_folder = Path("reports")

        self.reports_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.start_datetime = datetime.now()
        self.start_time = perf_counter()

        self.end_datetime = None
        self.end_time = None

        # Eventos detectados.
        self.yawn_events = 0
        self.eye_closed_events = 0
        self.high_fatigue_events = 0

        # Capturas generadas.
        self.yawn_captures = 0
        self.eye_captures = 0
        self.total_captures = 0

        # Valores máximos.
        self.maximum_yawn_count = 0
        self.maximum_level = "NORMAL"

        self.report_generated = False

    def register_yawn(
        self,
        fatigue_level: str,
        yawn_count: int,
        capture_created: bool = True,
    ) -> None:
        """
        Registra un bostezo confirmado.
        """

        self.yawn_events += 1

        if capture_created:
            self.yawn_captures += 1
            self.total_captures += 1

        self.update_status(
            fatigue_level=fatigue_level,
            yawn_count=yawn_count,
        )

    def register_eye_alert(
        self,
        fatigue_level: str,
        yawn_count: int,
        fatigue_elevated: bool,
        capture_created: bool = True,
    ) -> None:
        """
        Registra una alerta de ojos cerrados.

        Una alerta también puede clasificarse como
        fatiga elevada, pero la captura se cuenta
        solamente una vez.
        """

        self.eye_closed_events += 1

        if fatigue_elevated:
            self.high_fatigue_events += 1

        if capture_created:
            self.eye_captures += 1
            self.total_captures += 1

        self.update_status(
            fatigue_level=fatigue_level,
            yawn_count=yawn_count,
        )

    def update_status(
        self,
        fatigue_level: str,
        yawn_count: int,
    ) -> None:
        """
        Actualiza los valores máximos de la sesión.
        """

        normalized_level = (
            self._normalize_level(
                fatigue_level
            )
        )

        self.maximum_yawn_count = max(
            self.maximum_yawn_count,
            int(yawn_count),
        )

        self._update_maximum_level(
            normalized_level
        )

    def _update_maximum_level(
        self,
        fatigue_level: str,
    ) -> None:
        current_priority = (
            self.LEVEL_PRIORITY.get(
                fatigue_level,
                0,
            )
        )

        maximum_priority = (
            self.LEVEL_PRIORITY.get(
                self.maximum_level,
                0,
            )
        )

        if current_priority > maximum_priority:
            self.maximum_level = fatigue_level

    @classmethod
    def _normalize_level(
        cls,
        fatigue_level: str,
    ) -> str:
        normalized_level = (
            str(fatigue_level)
            .strip()
            .upper()
        )

        return cls.LEVEL_REPLACEMENTS.get(
            normalized_level,
            normalized_level,
        )

    def generate_report(
        self,
    ) -> dict | None:
        """
        Finaliza la sesión y genera los reportes
        TXT y PDF.

        Solo se ejecuta una vez.
        """

        if self.report_generated:
            return None

        self.report_generated = True

        self.end_datetime = datetime.now()
        self.end_time = perf_counter()

        duration_seconds = (
            self.end_time
            - self.start_time
        )

        duration_text = (
            self._format_duration(
                duration_seconds
            )
        )

        recommendation = (
            self._get_recommendation()
        )

        report_data = self._build_report_data(
            duration_text=duration_text,
            recommendation=recommendation,
        )

        base_filename = (
            "reporte_sesion_"
            f"{self.start_datetime.strftime('%Y-%m-%d_%H-%M-%S')}"
        )

        txt_path = (
            self.reports_folder
            / f"{base_filename}.txt"
        )

        pdf_path = (
            self.reports_folder
            / f"{base_filename}.pdf"
        )

        report_content = (
            self._build_text_report(
                report_data
            )
        )

        txt_path.write_text(
            report_content,
            encoding="utf-8",
        )

        pdf_report = PdfReport(
            output_path=pdf_path
        )

        pdf_report.generate(
            report_data
        )

        print()
        print(report_content)
        print()
        print(
            "[REPORTE] TXT guardado en:",
            txt_path,
        )
        print(
            "[REPORTE] PDF guardado en:",
            pdf_path,
        )

        return {
            "txt": txt_path,
            "pdf": pdf_path,
        }

    def _build_report_data(
        self,
        duration_text: str,
        recommendation: str,
    ) -> dict:
        """
        Organiza la información compartida por
        los formatos TXT y PDF.
        """

        return {
            "start_datetime": (
                self.start_datetime.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
            ),
            "end_datetime": (
                self.end_datetime.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
            ),
            "duration": duration_text,
            "yawn_events": self.yawn_events,
            "eye_closed_events": (
                self.eye_closed_events
            ),
            "high_fatigue_events": (
                self.high_fatigue_events
            ),
            "yawn_captures": (
                self.yawn_captures
            ),
            "eye_captures": (
                self.eye_captures
            ),
            "total_captures": (
                self.total_captures
            ),
            "maximum_yawn_count": (
                self.maximum_yawn_count
            ),
            "maximum_level": (
                self.maximum_level
            ),
            "recommendation": (
                recommendation
            ),
        }

    @staticmethod
    def _build_text_report(
        report_data: dict,
    ) -> str:
        """
        Construye la versión TXT del reporte.
        """

        separator = "=" * 52

        return (
            f"{separator}\n"
            "REPORTE DE SESIÓN - DETECTOR DE SOMNOLENCIA\n"
            f"{separator}\n\n"

            "INFORMACIÓN GENERAL\n"
            f"- Inicio: "
            f"{report_data['start_datetime']}\n"
            f"- Fin: "
            f"{report_data['end_datetime']}\n"
            f"- Tiempo monitoreado: "
            f"{report_data['duration']}\n\n"

            "EVENTOS DETECTADOS\n"
            f"- Bostezos: "
            f"{report_data['yawn_events']}\n"
            f"- Alertas por ojos cerrados: "
            f"{report_data['eye_closed_events']}\n"
            f"- Alertas con fatiga elevada: "
            f"{report_data['high_fatigue_events']}\n\n"

            "CAPTURAS GENERADAS\n"
            f"- Capturas de bostezos: "
            f"{report_data['yawn_captures']}\n"
            f"- Capturas de ojos cerrados: "
            f"{report_data['eye_captures']}\n"
            f"- Total de capturas: "
            f"{report_data['total_captures']}\n\n"

            "RESULTADOS DE LA SESIÓN\n"
            f"- Máximo de bostezos recientes: "
            f"{report_data['maximum_yawn_count']}\n"
            f"- Nivel máximo alcanzado: "
            f"{report_data['maximum_level']}\n"
            f"- Recomendación: "
            f"{report_data['recommendation']}\n\n"

            "ARCHIVOS RELACIONADOS\n"
            "- Registro detallado: "
            "logs/registro.csv\n"
            "- Evidencias: captures/\n\n"

            f"{separator}"
        )

    def _get_recommendation(self) -> str:
        """
        Genera una recomendación según los
        resultados de la sesión.
        """

        if (
            self.maximum_level == "CRITICO"
            or self.high_fatigue_events > 0
        ):
            return (
                "Se recomienda detenerse y tomar "
                "un descanso antes de continuar."
            )

        if (
            self.maximum_level == "ALERTA"
            or self.eye_closed_events > 0
        ):
            return (
                "Se recomienda realizar una pausa "
                "y evaluar el nivel de cansancio."
            )

        if (
            self.maximum_level == "ATENCION"
            or self.yawn_events >= 3
        ):
            return (
                "Se detectaron señales de cansancio. "
                "Mantener la atención y considerar "
                "una pausa."
            )

        return (
            "No se detectaron señales importantes "
            "de fatiga durante la sesión."
        )

    @staticmethod
    def _format_duration(
        total_seconds: float,
    ) -> str:
        """
        Convierte segundos a un texto legible.
        """

        total_seconds = max(
            0,
            int(total_seconds),
        )

        hours, remaining_seconds = divmod(
            total_seconds,
            3600,
        )

        minutes, seconds = divmod(
            remaining_seconds,
            60,
        )

        if hours > 0:
            return (
                f"{hours} h "
                f"{minutes} min "
                f"{seconds} s"
            )

        if minutes > 0:
            return (
                f"{minutes} min "
                f"{seconds} s"
            )

        return f"{seconds} s"