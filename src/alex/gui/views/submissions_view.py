from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QDialog,
)

from alex.esg.domain.submission import Submission
from alex.gui.dialogs.submission_details_dialog import SubmissionDetailsDialog
from alex.esg.services.submission_service import SubmissionService
from alex.gui.dialogs.submission_dialog import SubmissionDialog
from alex.esg.services.questionnaire_service import QuestionnaireService
from alex.esg.services.submission_service import SubmissionService
from alex.esg.services.supply_chain_relation_service import (SupplyChainRelationService,)
from alex.esg.services.test_data_service import add_test_answers


class SubmissionsView(QWidget):
    def __init__(
        self,
        submission_service: SubmissionService,
        relation_service: SupplyChainRelationService,
        questionnaire_service: QuestionnaireService,
    ) -> None:
        super().__init__()
        self._open_button = QPushButton("Megnyitás")
        self._open_button.setEnabled(False)

        self._submission_service = submission_service
        self._relation_service = relation_service
        self._questionnaire_service = questionnaire_service

        self._add_button = QPushButton("+ Új tesztbeküldés")

        self._search_input = QLineEdit()
        self._table = QTableWidget()

        self._setup_ui()
        self._connect_signals()
        self._refresh_table()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("Beküldések")

        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)

        main_layout.addWidget(title)


        toolbar_layout = QHBoxLayout()


        self._search_input.setPlaceholderText(
            "Keresés beszállító, kötelezett vagy időszak alapján..."
        )

        toolbar_layout.addWidget(
            self._open_button
        )

        toolbar_layout.addWidget(
            self._search_input
        )

        toolbar_layout.addWidget(
            self._add_button
        )

        main_layout.addLayout(
            toolbar_layout
        )

        main_layout.addWidget(
            self._search_input
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

        header = self._table.horizontalHeader()

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
        has_selection = bool(self._table.selectionModel().selectedRows())
        self._open_button.setEnabled(has_selection)

    def _get_selected_submission(self) -> Submission | None:
        selected_rows = (self._table.selectionModel().selectedRows())
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        submission_id_item = self._table.item(row, 0,)
        if submission_id_item is None:
            return None
        return self._submission_service.get_by_id(submission_id_item.text())

    def _open_selected_submission(self) -> None:
        submission = self._get_selected_submission()
        if submission is None:
            return
        dialog = SubmissionDetailsDialog(
            submission = submission,
            parent = self,
        )
        dialog.exec()

    def _open_submission_from_double_click(
            self,
            row: int,
            column: int,
    ) -> None:
        submission_id_item = self._table.item(row, 0,)
        if submission_id_item is None:
            return
        submission = self._submission_service.get_by_id(submission_id_item.text())
        if submission is None:
            return
        dialog = SubmissionDetailsDialog(
            submission = submission,
            parent = self,
        )
        dialog.exec()


    def _open_add_submission_dialog(self) -> None:
        relations = (
            self._relation_service.list_relations()
        )

        questionnaires = (
            self._questionnaire_service.list_questionnaires()
        )

        dialog = SubmissionDialog(
            relations=relations,
            questionnaires=questionnaires,
            parent=self,
        )

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            return

        try:
            submission = self._submission_service.create_submission(
                relation=dialog.relation,
                submitter=dialog.submitter,
                questionnaire=dialog.questionnaire,
                period=dialog.period,
            )

            add_test_answers(submission)

        except (TypeError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Beküldés létrehozási hiba",
                str(error),
            )
            return

        self._refresh_table()

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)

        for submission in (
            self._submission_service.list_submissions()
        ):
            self._add_submission_to_table(
                submission
            )

        self._filter_submissions(
            self._search_input.text()
        )

    def _add_submission_to_table(
        self,
        submission,
    ) -> None:
        row = self._table.rowCount()

        self._table.insertRow(row)

        self._table.setItem(
            row,
            0,
            QTableWidgetItem(
                str(submission.submission_id)
            ),
        )

        self._table.setItem(
            row,
            1,
            QTableWidgetItem(
                submission.relation.requester.name
            ),
        )

        self._table.setItem(
            row,
            2,
            QTableWidgetItem(
                submission.relation.supplier.name
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

        self._table.setItem(
            row,
            5,
            QTableWidgetItem(
                str(submission.status)
            ),
        )

    def _filter_submissions(
        self,
        text: str,
    ) -> None:
        search_text = text.strip().lower()

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