from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from alex.gui.dialogs.submission_import_dialog import SubmissionImportDialog
from alex.esg.services.submission_import_preview_service import (
    SubmissionImportPreviewService,
)
from alex.esg.domain.submission import Submission
from alex.esg.services.questionnaire_service import (
    QuestionnaireService,
)
from alex.esg.services.submission_file_import_service import (
    SubmissionFileImportService,
)
from alex.esg.services.submission_service import (
    SubmissionService,
)
from alex.esg.services.supply_chain_relation_service import (
    SupplyChainRelationService,
)
from alex.esg.services.test_data_service import (
    add_test_answers,
)

from alex.gui.dialogs.submission_details_dialog import (
    SubmissionDetailsDialog,
)
from alex.gui.dialogs.submission_dialog import (
    SubmissionDialog,
)


class SubmissionsView(QWidget):
    def __init__(
        self,
        submission_service: SubmissionService,
        relation_service: SupplyChainRelationService,
        questionnaire_service: QuestionnaireService,
        file_import_service: SubmissionFileImportService,
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

        self._preview_service = (
            preview_service
        )
        if not isinstance(
            file_import_service,
            SubmissionFileImportService,
        ):
            raise TypeError(
                "file_import_service must be a "
                "SubmissionFileImportService"
            )

        self._submission_service = (
            submission_service
        )
        self._relation_service = (
            relation_service
        )
        self._questionnaire_service = (
            questionnaire_service
        )
        self._file_import_service = (
            file_import_service
        )

        self._open_button = QPushButton(
            "Megnyitás"
        )
        self._open_button.setEnabled(False)

        self._add_button = QPushButton(
            "+ Új tesztbeküldés"
        )

        self._import_button = QPushButton(
            "JSON import"
        )

        self._search_input = QLineEdit()
        self._table = QTableWidget()

        self._setup_ui()
        self._connect_signals()
        self._refresh_table()
        self._preview_service = preview_service

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel(
            "Beküldések"
        )

        font = title.font()
        font.setPointSize(20)
        font.setBold(True)

        title.setFont(font)

        main_layout.addWidget(
            title
        )

        toolbar_layout = QHBoxLayout()

        self._search_input.setPlaceholderText(
            "Keresés beszállító, kötelezett "
            "vagy időszak alapján..."
        )

        toolbar_layout.addWidget(
            self._open_button
        )

        toolbar_layout.addWidget(
            self._search_input,
            1,
        )

        toolbar_layout.addWidget(
            self._add_button
        )

        toolbar_layout.addWidget(
            self._import_button
        )

        main_layout.addLayout(
            toolbar_layout
        )

        self._setup_table()

        main_layout.addWidget(
            self._table
        )

    def _setup_table(self) -> None:
        self._table.setColumnCount(6)

        self._table.setHorizontalHeaderLabels(
            [
                "Submission ID",
                "Kötelezett",
                "Beszállító",
                "Kérdőív",
                "Időszak",
                "Státusz",
            ]
        )

        header = (
            self._table.horizontalHeader()
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

    def _connect_signals(self) -> None:
        self._search_input.textChanged.connect(
            self._filter_submissions
        )

        self._add_button.clicked.connect(
            self._open_add_submission_dialog
        )

        self._import_button.clicked.connect(
            self._import_json
        )

        self._table.itemSelectionChanged.connect(
            self._update_button_state
        )

        self._open_button.clicked.connect(
            self._open_selected_submission
        )

        self._table.cellDoubleClicked.connect(
            self._open_submission_from_double_click
        )

    def _update_button_state(self) -> None:
        has_selection = bool(
            self._table
            .selectionModel()
            .selectedRows()
        )

        self._open_button.setEnabled(
            has_selection
        )

    def _get_selected_submission(
        self,
    ) -> Submission | None:
        selected_rows = (
            self._table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return None

        row = selected_rows[0].row()

        submission_id_item = (
            self._table.item(
                row,
                0,
            )
        )

        if submission_id_item is None:
            return None

        return self._submission_service.get_by_id(
            submission_id_item.text()
        )

    def _open_selected_submission(
        self,
    ) -> None:
        submission = (
            self._get_selected_submission()
        )

        if submission is None:
            return

        dialog = SubmissionDetailsDialog(
            submission=submission,
            parent=self,
        )

        dialog.exec()

    def _open_submission_from_double_click(
        self,
        row: int,
        column: int,
    ) -> None:
        submission_id_item = (
            self._table.item(
                row,
                0,
            )
        )

        if submission_id_item is None:
            return

        submission = (
            self._submission_service.get_by_id(
                submission_id_item.text()
            )
        )

        if submission is None:
            return

        dialog = SubmissionDetailsDialog(
            submission=submission,
            parent=self,
        )

        dialog.exec()

    def _open_add_submission_dialog(
        self,
    ) -> None:
        relations = (
            self._relation_service
            .list_relations()
        )

        questionnaires = (
            self._questionnaire_service
            .list_questionnaires()
        )

        dialog = SubmissionDialog(
            relations=relations,
            questionnaires=questionnaires,
            parent=self,
        )

        result = dialog.exec()

        if (
            result
            != QDialog.DialogCode.Accepted
        ):
            return

        try:
            submission = (
                self._submission_service
                .create_submission(
                    relation=dialog.relation,
                    submitter=dialog.submitter,
                    questionnaire=dialog.questionnaire,
                    period=dialog.period,
                )
            )

            add_test_answers(
                submission
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Beküldés létrehozási hiba",
                str(error),
            )

            return

        self._refresh_table()

    def _import_json(self) -> None:
        dialog = SubmissionImportDialog(
            preview_service=self._preview_service,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        result_code = dialog.exec()

        if (
                result_code
                != QDialog.DialogCode.Accepted
        ):
            return

        try:
            result = (
                self._file_import_service
                .import_files(
                    definition_file=(
                        dialog.definition_file
                    ),
                    submission_file=(
                        dialog.submission_file
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
            QMessageBox.critical(
                self,
                "JSON import hiba",
                str(error),
            )

            return

        self._show_import_result(
            result
        )

        self._refresh_table()

    def _show_import_result(
        self,
        result,
    ) -> None:
        lines = [
            (
                "Importált beküldések: "
                f"{result.imported_count}"
            ),
            (
                "Sikertelen beküldések: "
                f"{result.failed_count}"
            ),
        ]

        errors = (
            result.batch_result.errors
        )

        warnings = (
            result.batch_result.warnings
        )

        if errors:
            lines.append("")
            lines.append("Hibák:")

            for issue in errors:
                lines.append(
                    f"- [{issue.code}] "
                    f"{issue.message}"
                )

        if warnings:
            lines.append("")
            lines.append(
                "Figyelmeztetések:"
            )

            for issue in warnings:
                lines.append(
                    f"- [{issue.code}] "
                    f"{issue.message}"
                )

        message = "\n".join(
            lines
        )

        if errors:
            QMessageBox.warning(
                self,
                "JSON import eredménye",
                message,
            )

            return

        QMessageBox.information(
            self,
            "JSON import eredménye",
            message,
        )

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)

        for submission in (
            self._submission_service
            .list_submissions()
        ):
            self._add_submission_to_table(
                submission
            )

        self._filter_submissions(
            self._search_input.text()
        )

    def _add_submission_to_table(
        self,
        submission: Submission,
    ) -> None:
        row = self._table.rowCount()

        self._table.insertRow(
            row
        )

        self._table.setItem(
            row,
            0,
            QTableWidgetItem(
                str(
                    submission.submission_id
                )
            ),
        )

        self._table.setItem(
            row,
            1,
            QTableWidgetItem(
                submission
                .relation
                .requester
                .name
            ),
        )

        self._table.setItem(
            row,
            2,
            QTableWidgetItem(
                submission
                .relation
                .supplier
                .name
            ),
        )

        questionnaire_text = (
            f"{submission.questionnaire.questionnaire_code} "
            f"{submission.questionnaire.spec_version}"
        )

        self._table.setItem(
            row,
            3,
            QTableWidgetItem(
                questionnaire_text
            ),
        )

        self._table.setItem(
            row,
            4,
            QTableWidgetItem(
                submission.period
            ),
        )

        status_text = (
            submission.status.value
            if hasattr(
                submission.status,
                "value",
            )
            else str(
                submission.status
            )
        )

        self._table.setItem(
            row,
            5,
            QTableWidgetItem(
                status_text
            ),
        )

    def _filter_submissions(
        self,
        text: str,
    ) -> None:
        search_text = (
            text.strip().lower()
        )

        for row in range(
            self._table.rowCount()
        ):
            searchable_values = []

            for column in range(
                self._table.columnCount()
            ):
                item = self._table.item(
                    row,
                    column,
                )

                if item is not None:
                    searchable_values.append(
                        item.text().lower()
                    )

            matches = any(
                search_text in value
                for value in searchable_values
            )

            self._table.setRowHidden(
                row,
                not matches,
            )