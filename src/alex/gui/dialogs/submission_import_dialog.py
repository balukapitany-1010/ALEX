from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from alex.esg.services.submission_import_preview_service import (
    SubmissionImportPreviewService,
)


class SubmissionImportDialog(QDialog):
    def __init__(
        self,
        *,
        preview_service: SubmissionImportPreviewService,
        parent=None,
    ) -> None:
        super().__init__(parent)

        if not isinstance(
            preview_service,
            SubmissionImportPreviewService,
        ):
            raise TypeError(
                "preview_service must be a "
                "SubmissionImportPreviewService"
            )

        self._preview_service = preview_service
        self._preview = None

        self.setWindowTitle(
            "JSON import"
        )

        self.resize(
            760,
            520,
        )

        self._definition_input = QLineEdit()
        self._submission_input = QLineEdit()

        self._definition_input.setReadOnly(
            True
        )

        self._submission_input.setReadOnly(
            True
        )

        self._definition_button = QPushButton(
            "Tallózás..."
        )

        self._submission_button = QPushButton(
            "Tallózás..."
        )

        self._definition_version_label = QLabel(
            "-"
        )

        self._submission_version_label = QLabel(
            "-"
        )

        self._definition_count_label = QLabel(
            "-"
        )

        self._submission_count_label = QLabel(
            "-"
        )

        self._response_question_count_label = QLabel(
            "-"
        )

        self._matched_question_count_label = QLabel(
            "-"
        )

        self._error_count_label = QLabel(
            "-"
        )

        self._warning_count_label = QLabel(
            "-"
        )

        self._status_label = QLabel(
            "Válaszd ki a két JSON fájlt."
        )

        self._issues_text = QTextEdit()
        self._issues_text.setReadOnly(
            True
        )

        self._import_button = QPushButton(
            "Importálás"
        )

        self._cancel_button = QPushButton(
            "Mégse"
        )

        self._import_button.setEnabled(
            False
        )

        self._setup_ui()
        self._connect_signals()

    @property
    def definition_file(self) -> str:
        return (
            self._definition_input
            .text()
            .strip()
        )

    @property
    def submission_file(self) -> str:
        return (
            self._submission_input
            .text()
            .strip()
        )

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(
            self
        )

        description = QLabel(
            "Válaszd ki a kérdőív-definíciót "
            "és a hozzá tartozó beküldési JSON fájlt. "
            "ALEX importálás előtt automatikusan "
            "ellenőrzi a fájlokat."
        )

        description.setWordWrap(
            True
        )

        main_layout.addWidget(
            description
        )

        file_form = QFormLayout()

        definition_layout = QHBoxLayout()

        definition_layout.addWidget(
            self._definition_input,
            1,
        )

        definition_layout.addWidget(
            self._definition_button
        )

        submission_layout = QHBoxLayout()

        submission_layout.addWidget(
            self._submission_input,
            1,
        )

        submission_layout.addWidget(
            self._submission_button
        )

        file_form.addRow(
            "Kérdőív-definíció:",
            definition_layout,
        )

        file_form.addRow(
            "Beküldési JSON:",
            submission_layout,
        )

        main_layout.addLayout(
            file_form
        )

        preview_title = QLabel(
            "Import előellenőrzés"
        )

        preview_font = preview_title.font()
        preview_font.setBold(True)

        preview_title.setFont(
            preview_font
        )

        main_layout.addWidget(
            preview_title
        )

        preview_form = QFormLayout()

        preview_form.addRow(
            "Definíció verzió:",
            self._definition_version_label,
        )

        preview_form.addRow(
            "Beküldés verzió:",
            self._submission_version_label,
        )

        preview_form.addRow(
            "Definíciók száma:",
            self._definition_count_label,
        )

        preview_form.addRow(
            "Beküldések száma:",
            self._submission_count_label,
        )

        preview_form.addRow(
            "Beküldött kérdések:",
            self._response_question_count_label,
        )

        preview_form.addRow(
            "Technical ID egyezés:",
            self._matched_question_count_label,
        )

        preview_form.addRow(
            "Hibák:",
            self._error_count_label,
        )

        preview_form.addRow(
            "Figyelmeztetések:",
            self._warning_count_label,
        )

        preview_form.addRow(
            "Állapot:",
            self._status_label,
        )

        main_layout.addLayout(
            preview_form
        )

        main_layout.addWidget(
            QLabel(
                "Ellenőrzési részletek:"
            )
        )

        main_layout.addWidget(
            self._issues_text,
            1,
        )

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        button_layout.addWidget(
            self._cancel_button
        )

        button_layout.addWidget(
            self._import_button
        )

        main_layout.addLayout(
            button_layout
        )

    def _connect_signals(self) -> None:
        self._definition_button.clicked.connect(
            self._select_definition_file
        )

        self._submission_button.clicked.connect(
            self._select_submission_file
        )

        self._cancel_button.clicked.connect(
            self.reject
        )

        self._import_button.clicked.connect(
            self._accept_import
        )

    def _select_definition_file(
        self,
    ) -> None:
        filename, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Kérdőív-definíció kiválasztása",
                "",
                "JSON fájlok (*.json)",
            )
        )

        if not filename:
            return

        self._definition_input.setText(
            filename
        )

        self._try_preview()

    def _select_submission_file(
        self,
    ) -> None:
        filename, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Beküldési JSON kiválasztása",
                "",
                "JSON fájlok (*.json)",
            )
        )

        if not filename:
            return

        self._submission_input.setText(
            filename
        )

        self._try_preview()

    def _try_preview(self) -> None:
        self._preview = None

        self._import_button.setEnabled(
            False
        )

        if (
            not self.definition_file
            or not self.submission_file
        ):
            self._status_label.setText(
                "Válaszd ki a két JSON fájlt."
            )

            return

        try:
            preview = (
                self._preview_service.preview_files(
                    definition_file=(
                        self.definition_file
                    ),
                    submission_file=(
                        self.submission_file
                    ),
                    questionnaire_code=(
                        "SZTFH-ESG"
                    ),
                )
            )

        except (
            FileNotFoundError,
            TypeError,
            ValueError,
        ) as error:
            self._clear_preview()

            self._status_label.setText(
                "ELLENŐRZÉSI HIBA"
            )

            self._issues_text.setPlainText(
                str(error)
            )

            return

        self._preview = preview

        self._show_preview(
            preview
        )

    def _show_preview(
        self,
        preview,
    ) -> None:
        self._definition_version_label.setText(
            preview.definition_version
        )

        self._submission_version_label.setText(
            preview.submission_version
        )

        self._definition_count_label.setText(
            str(
                preview.definition_count
            )
        )

        self._submission_count_label.setText(
            str(
                preview.submission_count
            )
        )

        self._response_question_count_label.setText(
            str(
                preview.response_question_count
            )
        )

        self._matched_question_count_label.setText(
            (
                f"{preview.matched_question_count} / "
                f"{preview.response_question_count}"
            )
        )

        self._error_count_label.setText(
            str(
                len(
                    preview.errors
                )
            )
        )

        self._warning_count_label.setText(
            str(
                len(
                    preview.warnings
                )
            )
        )

        if preview.can_import:
            self._status_label.setText(
                "IMPORTÁLHATÓ"
            )

        else:
            self._status_label.setText(
                "NEM IMPORTÁLHATÓ"
            )

        lines = []

        if preview.errors:
            lines.append(
                "Hibák:"
            )

            for issue in preview.errors:
                lines.append(
                    f"[{issue.code}] "
                    f"{issue.message}"
                )

        if preview.warnings:
            if lines:
                lines.append("")

            lines.append(
                "Figyelmeztetések:"
            )

            for issue in preview.warnings:
                lines.append(
                    f"[{issue.code}] "
                    f"{issue.message}"
                )

        if not lines:
            lines.append(
                "Az ellenőrzés nem talált "
                "hibát vagy figyelmeztetést."
            )

        self._issues_text.setPlainText(
            "\n".join(
                lines
            )
        )

        self._import_button.setEnabled(
            preview.can_import
        )

    def _clear_preview(self) -> None:
        self._definition_version_label.setText(
            "-"
        )

        self._submission_version_label.setText(
            "-"
        )

        self._definition_count_label.setText(
            "-"
        )

        self._submission_count_label.setText(
            "-"
        )

        self._response_question_count_label.setText(
            "-"
        )

        self._matched_question_count_label.setText(
            "-"
        )

        self._error_count_label.setText(
            "-"
        )

        self._warning_count_label.setText(
            "-"
        )

        self._issues_text.clear()

        self._import_button.setEnabled(
            False
        )

    def _accept_import(
        self,
    ) -> None:
        definition_path = Path(
            self.definition_file
        )

        submission_path = Path(
            self.submission_file
        )

        if not definition_path.is_file():
            QMessageBox.warning(
                self,
                "Hiányzó fájl",
                "A kérdőív-definíció "
                "nem található.",
            )

            return

        if not submission_path.is_file():
            QMessageBox.warning(
                self,
                "Hiányzó fájl",
                "A beküldési JSON "
                "nem található.",
            )

            return

        if (
            self._preview is None
            or not self._preview.can_import
        ):
            QMessageBox.warning(
                self,
                "Nem importálható",
                "A kiválasztott fájlok "
                "nem importálhatók.",
            )

            return

        self.accept()