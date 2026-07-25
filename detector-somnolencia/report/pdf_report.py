from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PdfReport:
    """
    Genera el reporte PDF de una sesión.

    Esta clase solamente se encarga de la
    presentación visual de la información.
    """

    def __init__(
        self,
        output_path: Path,
    ) -> None:
        self.output_path = output_path

    def generate(
        self,
        report_data: dict,
    ) -> Path:
        """
        Crea el archivo PDF utilizando los datos
        recibidos desde SessionReport.
        """

        document = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=1.8 * cm,
            leftMargin=1.8 * cm,
            topMargin=1.6 * cm,
            bottomMargin=1.6 * cm,
            title=(
                "Reporte de sesión - "
                "Detector de somnolencia"
            ),
            author="Detector de somnolencia",
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            leading=22,
            textColor=colors.HexColor(
                "#1F2937"
            ),
            spaceAfter=6,
        )

        subtitle_style = ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor(
                "#4B5563"
            ),
            spaceAfter=16,
        )

        section_style = ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor(
                "#111827"
            ),
            spaceBefore=12,
            spaceAfter=7,
        )

        normal_style = ParagraphStyle(
            name="ReportText",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            textColor=colors.HexColor(
                "#374151"
            ),
        )

        story = []

        story.append(
            Paragraph(
                "REPORTE DE SESIÓN",
                title_style,
            )
        )

        story.append(
            Paragraph(
                "Detector de somnolencia",
                subtitle_style,
            )
        )

        story.append(
            self._create_status_banner(
                level=report_data[
                    "maximum_level"
                ],
                recommendation=report_data[
                    "recommendation"
                ],
                normal_style=normal_style,
            )
        )

        story.append(
            Spacer(1, 0.3 * cm)
        )

        story.append(
            Paragraph(
                "Información general",
                section_style,
            )
        )

        general_rows = [
            [
                "Inicio",
                report_data["start_datetime"],
            ],
            [
                "Fin",
                report_data["end_datetime"],
            ],
            [
                "Tiempo monitoreado",
                report_data["duration"],
            ],
        ]

        story.append(
            self._create_table(
                general_rows
            )
        )

        story.append(
            Paragraph(
                "Eventos detectados",
                section_style,
            )
        )

        event_rows = [
            [
                "Bostezos",
                str(
                    report_data[
                        "yawn_events"
                    ]
                ),
            ],
            [
                "Alertas por ojos cerrados",
                str(
                    report_data[
                        "eye_closed_events"
                    ]
                ),
            ],
            [
                "Alertas con fatiga elevada",
                str(
                    report_data[
                        "high_fatigue_events"
                    ]
                ),
            ],
        ]

        story.append(
            self._create_table(
                event_rows
            )
        )

        story.append(
            Paragraph(
                "Capturas generadas",
                section_style,
            )
        )

        capture_rows = [
            [
                "Capturas de bostezos",
                str(
                    report_data[
                        "yawn_captures"
                    ]
                ),
            ],
            [
                "Capturas de ojos cerrados",
                str(
                    report_data[
                        "eye_captures"
                    ]
                ),
            ],
            [
                "Total de capturas",
                str(
                    report_data[
                        "total_captures"
                    ]
                ),
            ],
        ]

        story.append(
            self._create_table(
                capture_rows
            )
        )

        story.append(
            Paragraph(
                "Resultados de la sesión",
                section_style,
            )
        )

        result_rows = [
            [
                "Máximo de bostezos recientes",
                str(
                    report_data[
                        "maximum_yawn_count"
                    ]
                ),
            ],
            [
                "Nivel máximo alcanzado",
                report_data[
                    "maximum_level"
                ],
            ],
        ]

        story.append(
            self._create_table(
                result_rows
            )
        )

        story.append(
            Paragraph(
                "Recomendación",
                section_style,
            )
        )

        story.append(
            self._create_recommendation_box(
                report_data[
                    "recommendation"
                ],
                normal_style,
            )
        )

        story.append(
            Paragraph(
                "Archivos relacionados",
                section_style,
            )
        )

        file_rows = [
            [
                "Registro detallado",
                "logs/registro.csv",
            ],
            [
                "Evidencias",
                "captures/",
            ],
        ]

        story.append(
            self._create_table(
                file_rows
            )
        )

        story.append(
            Spacer(1, 0.5 * cm)
        )

        story.append(
            Paragraph(
                (
                    "Reporte generado "
                    "automáticamente al finalizar "
                    "la sesión."
                ),
                subtitle_style,
            )
        )

        document.build(story)

        return self.output_path

    @staticmethod
    def _create_table(
        rows: list[list[str]],
    ) -> Table:
        """
        Construye una tabla sencilla de dos columnas.
        """

        table = Table(
            rows,
            colWidths=[
                8.5 * cm,
                8.5 * cm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor(
                            "#F3F4F6"
                        ),
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold",
                    ),
                    (
                        "FONTNAME",
                        (1, 0),
                        (1, -1),
                        "Helvetica",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        9.5,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(
                            "#1F2937"
                        ),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor(
                            "#D1D5DB"
                        ),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        return table

    @staticmethod
    def _create_status_banner(
        level: str,
        recommendation: str,
        normal_style: ParagraphStyle,
    ) -> Table:
        """
        Crea el bloque principal con el nivel máximo.
        """

        background_color = colors.HexColor(
            "#DCFCE7"
        )

        border_color = colors.HexColor(
            "#166534"
        )

        if level == "ATENCION":
            background_color = colors.HexColor(
                "#FEF3C7"
            )

            border_color = colors.HexColor(
                "#92400E"
            )

        elif level == "ALERTA":
            background_color = colors.HexColor(
                "#FED7AA"
            )

            border_color = colors.HexColor(
                "#9A3412"
            )

        elif level == "CRITICO":
            background_color = colors.HexColor(
                "#FEE2E2"
            )

            border_color = colors.HexColor(
                "#991B1B"
            )

        banner_style = ParagraphStyle(
            name="StatusBanner",
            parent=normal_style,
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=17,
            textColor=border_color,
        )

        content = Paragraph(
            (
                f"Nivel máximo alcanzado: {level}"
                f"<br/>{recommendation}"
            ),
            banner_style,
        )

        banner = Table(
            [[content]],
            colWidths=[17 * cm],
        )

        banner.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        background_color,
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        1,
                        border_color,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                ]
            )
        )

        return banner

    @staticmethod
    def _create_recommendation_box(
        recommendation: str,
        normal_style: ParagraphStyle,
    ) -> Table:
        """
        Presenta la recomendación dentro
        de un bloque destacado.
        """

        content = Paragraph(
            recommendation,
            normal_style,
        )

        box = Table(
            [[content]],
            colWidths=[17 * cm],
        )

        box.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor(
                            "#F9FAFB"
                        ),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        colors.HexColor(
                            "#D1D5DB"
                        ),
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                ]
            )
        )

        return box