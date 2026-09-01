import mimetypes
import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
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

from alex.esg.domain.attachment import Attachment
from alex.esg.domain.submission import Submission
from alex.esg.services.attachment_service import (
    AttachmentService,
)
from alex.esg.services.question_definition_service import (
    QuestionDefinitionService,
)
from alex.esg.services.submission_service import (
    SubmissionService,
)
from alex.gui.dialogs.attachment_dialog import (
    AttachmentDialog,
)


class AttachmentsView(QWidget):
    def __init__(
        self,
        *,
        submission_service: SubmissionService,
        attachment_service: AttachmentService,
        question_definition_service: QuestionDefinitionService,
        parent=None,
    ) -> None:
        super().__init__(parent)

        if not isinstance(
            submission_service,
            SubmissionService,
        ):
            raise TypeError(
                "submission_service must be a SubmissionService"
            )

        if not isinstance(
            attachment_service,
            AttachmentService,
        ):
            raise TypeError(
                "attachment_service must be an AttachmentService"
            )

        if not isinstance(
            question_definition_service,
            QuestionDefinitionService,
        ):
            raise TypeError(
                "question_definition_service must be a "
                "QuestionDefinitionService"
            )

        self._submission_service = submission_service
        self._attachment_service = attachment_service
        self._question_definition_service = (
            question_definition_service
        )

        self._search_input = QLineEdit()

        self._open_button = QPushButton(
            "Megnyitás"
        )
        self._open_button.setEnabled(False)

        self._delete_button = QPushButton(
            "Törlés"
        )
        self._delete_button.setEnabled(False)

        self._add_button = QPushButton(
            "+ Dokumentum hozzáadása"
        )

        self._table = QTableWidget()

        self._setup_ui()
        self._connect_signals()
        self.refresh()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Dokumentumok"
        )

        font = title.font()
        font.setPointSize(20)
        font.setBold(True)

        title.setFont(
            font
        )

        main_layout.addWidget(
            title
        )

        toolbar_layout = QHBoxLayout()

        self._search_input.setPlaceholderText(
            "Keresés fájlnév, cég, kérdés "
            "vagy időszak alapján..."
        )

        toolbar_layout.addWidget(
            self._search_input,
            1,
        )

        toolbar_layout.addWidget(
            self._open_button
        )

        toolbar_layout.addWidget(
            self._delete_button
        )

        toolbar_layout.addWidget(
            self._add_button
        )

        main_layout.addLayout(
            toolbar_layout
        )

        self._setup_table()

        # EZ FONTOS:
        # maga a dokumentumtábla is bekerül a layoutba
        self._table.setMinimumHeight(
            300
        )

        main_layout.addWidget(
            self._table,
            1,
        )

    def _setup_table(self) -> None:
        self._table.setColumnCount(
            6
        )

        self._table.setHorizontalHeaderLabels(
            [
                "Fájlnév",
                "Kötelezett",
                "Beszállító",
                "Időszak",
                "Kérdés",
                "Tárolási hivatkozás",
            ]
        )

        header = (
            self._table.horizontalHeader()
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
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
            QHeaderView.ResizeMode.Stretch,
        )

        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self._table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

    def _connect_signals(self) -> None:
        self._search_input.textChanged.connect(
            self._filter_attachments
        )

        self._add_button.clicked.connect(
            self._add_attachment
        )

        self._table.itemSelectionChanged.connect(
            self._update_button_state
        )

        self._open_button.clicked.connect(
            self._open_selected_attachment
        )

        self._delete_button.clicked.connect(
            self._delete_selected_attachment
        )

        self._table.cellDoubleClicked.connect(
            self._open_attachment_from_double_click
        )

    def refresh(self) -> None:
        self._table.setRowCount(
            0
        )

        submissions = (
            self._submission_service
            .list_submissions()
        )

        for submission in submissions:
            for attachment in submission.attachments:
                self._add_attachment_to_table(
                    submission=submission,
                    attachment=attachment,
                )

        self._filter_attachments(
            self._search_input.text()
        )

        self._update_button_state()

    def _add_attachment_to_table(
        self,
        *,
        submission: Submission,
        attachment: Attachment,
    ) -> None:
        row = self._table.rowCount()

        self._table.insertRow(
            row
        )

        question_code = "-"

        if (
            attachment.question_definition
            is not None
        ):
            question_code = (
                attachment
                .question_definition
                .question
                .question_code
            )

        file_item = QTableWidgetItem(
            attachment.file_name
        )

        file_item.setData(
            Qt.ItemDataRole.UserRole,
            (
                submission.submission_id,
                attachment.attachment_id,
            ),
        )

        self._table.setItem(
            row,
            0,
            file_item,
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

        self._table.setItem(
            row,
            3,
            QTableWidgetItem(
                submission.period
            ),
        )

        self._table.setItem(
            row,
            4,
            QTableWidgetItem(
                question_code
            ),
        )

        self._table.setItem(
            row,
            5,
            QTableWidgetItem(
                attachment.storage_reference
            ),
        )

    def _add_attachment(self) -> None:
        submissions = (
            self._submission_service
            .list_submissions()
        )

        if not submissions:
            QMessageBox.warning(
                self,
                "Nincs beküldés",
                (
                    "Dokumentum hozzáadásához "
                    "először szükség van "
                    "legalább egy beküldésre."
                ),
            )

            return

        definitions = (
            self._question_definition_service
            .list_definitions()
        )

        dialog = AttachmentDialog(
            submissions=submissions,
            question_definitions=definitions,
            parent=self,
        )

        result = dialog.exec()

        if (
            result
            != QDialog.DialogCode.Accepted
        ):
            return

        submission = dialog.submission

        if submission is None:
            return

        path = Path(
            dialog.file_path
        )

        content_type, _ = (
            mimetypes.guess_type(
                str(path)
            )
        )

        try:
            attachment = (
                self._attachment_service
                .create_attachment(
                    submission=submission,
                    file_name=path.name,
                    storage_reference=str(
                        path.resolve()
                    ),
                    content_type=content_type,
                    file_size=(
                        path.stat().st_size
                    ),
                    question_definition=(
                        dialog.question_definition
                    ),
                )
            )

        except (
            OSError,
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Dokumentum hozzáadási hiba",
                str(error),
            )

            return

        # Fontos:
        # az Attachment ekkor már a Submissionben van
        self.refresh()

        QMessageBox.information(
            self,
            "Dokumentum hozzáadása",
            (
                "A dokumentum sikeresen "
                "hozzá lett kapcsolva a beküldéshez.\n\n"
                f"Fájl: {attachment.file_name}"
            ),
        )

    def _get_selected_attachment(
        self,
    ) -> tuple[
        Submission,
        Attachment,
    ] | None:
        selected_rows = (
            self._table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return None

        row = selected_rows[0].row()

        file_item = self._table.item(
            row,
            0,
        )

        if file_item is None:
            return None

        identifiers = file_item.data(
            Qt.ItemDataRole.UserRole
        )

        if (
            not isinstance(
                identifiers,
                tuple,
            )
            or len(identifiers) != 2
        ):
            return None

        (
            submission_id,
            attachment_id,
        ) = identifiers

        submission = (
            self._submission_service
            .get_by_id(
                submission_id
            )
        )

        if submission is None:
            return None

        attachment = (
            self._attachment_service
            .get_by_id(
                submission=submission,
                attachment_id=attachment_id,
            )
        )

        if attachment is None:
            return None

        return (
            submission,
            attachment,
        )

    def _update_button_state(
        self,
    ) -> None:
        has_selection = (
            self._get_selected_attachment()
            is not None
        )

        self._open_button.setEnabled(
            has_selection
        )

        self._delete_button.setEnabled(
            has_selection
        )

    def _open_selected_attachment(
        self,
    ) -> None:
        selected = (
            self._get_selected_attachment()
        )

        if selected is None:
            return

        _, attachment = selected

        path = Path(
            attachment.storage_reference
        )

        if not path.is_file():
            QMessageBox.warning(
                self,
                "Dokumentum nem található",
                (
                    "A dokumentumhoz tartozó "
                    "fájl nem található:\n\n"
                    f"{attachment.storage_reference}"
                ),
            )

            return

        try:
            os.startfile(
                str(path)
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "Dokumentum megnyitási hiba",
                str(error),
            )

    def _open_attachment_from_double_click(
        self,
        row: int,
        column: int,
    ) -> None:
        self._table.selectRow(
            row
        )

        self._open_selected_attachment()

    def _delete_selected_attachment(
        self,
    ) -> None:
        selected = (
            self._get_selected_attachment()
        )

        if selected is None:
            return

        submission, attachment = (
            selected
        )

        answer = QMessageBox.question(
            self,
            "Dokumentum törlése",
            (
                "Biztosan eltávolítod ezt "
                "a dokumentumot a beküldésből?\n\n"
                f"{attachment.file_name}"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            self._attachment_service.remove_attachment(
                submission=submission,
                attachment_id=(
                    attachment.attachment_id
                ),
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Dokumentum törlési hiba",
                str(error),
            )

            return

        self.refresh()

    def _filter_attachments(
        self,
        text: str,
    ) -> None:
        search_text = (
            text.strip().lower()
        )

        for row in range(
            self._table.rowCount()
        ):
            values = []

            for column in range(
                self._table.columnCount()
            ):
                item = (
                    self._table.item(
                        row,
                        column,
                    )
                )

                if item is not None:
                    values.append(
                        item.text().lower()
                    )

            matches = (
                not search_text
                or any(
                    search_text in value
                    for value in values
                )
            )

            self._table.setRowHidden(
                row,
                not matches,
            )