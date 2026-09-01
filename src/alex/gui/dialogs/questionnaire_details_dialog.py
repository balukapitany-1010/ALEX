from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from alex.esg.domain.question_definition import (
    QuestionDefinition,
)
from alex.esg.domain.questionnaire import (
    Questionnaire,
)
from alex.gui.dialogs.question_definition_details_dialog import (
    QuestionDefinitionDetailsDialog,
)


class QuestionnaireDetailsDialog(QDialog):
    def __init__(
        self,
        *,
        questionnaire: Questionnaire,
        definitions: tuple[
            QuestionDefinition,
            ...
        ],
        parent=None,
    ) -> None:
        super().__init__(parent)

        if not isinstance(
            questionnaire,
            Questionnaire,
        ):
            raise TypeError(
                "questionnaire must be a Questionnaire"
            )

        if not isinstance(
            definitions,
            tuple,
        ):
            raise TypeError(
                "definitions must be a tuple"
            )

        if not all(
            isinstance(
                definition,
                QuestionDefinition,
            )
            for definition in definitions
        ):
            raise TypeError(
                "definitions must contain only "
                "QuestionDefinition objects"
            )

        self._questionnaire = questionnaire
        self._definitions = definitions

        self.setWindowTitle(
            (
                f"{questionnaire.questionnaire_code} "
                f"{questionnaire.spec_version}"
            )
        )

        self.resize(
            1100,
            700,
        )

        self._table = QTableWidget()
        self._search_input = QLineEdit()
        self._category_filter = QComboBox()
        self._open_question_button = QPushButton("Kérdés megnyitása")

        self._open_question_button.setEnabled(False)

        self._setup_ui()
        self._load_definitions()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            (
                f"{self._questionnaire.questionnaire_code} "
                f"{self._questionnaire.spec_version} "
                f"({self._questionnaire.locale})"
            )
        )

        font = title.font()
        font.setPointSize(18)
        font.setBold(True)

        title.setFont(
            font
        )

        layout.addWidget(
            title
        )

        count_label = QLabel(
            (
                "Kérdésdefiníciók száma: "
                f"{len(self._definitions)}"
            )
        )
        filter_layout = QHBoxLayout()

        self._search_input.setPlaceholderText(
            "Keresés kérdéskód, technical ID, téma vagy kérdésszöveg alapján..."
        )

        self._category_filter.addItems(
            [
                "Összes kategória",
                "E",
                "S",
                "G",
            ]
        )

        filter_layout.addWidget(
            self._search_input,
            1,
        )

        filter_layout.addWidget(
            self._category_filter,
        )

        layout.addLayout(
            filter_layout
        )

        layout.addWidget(
            count_label
        )

        self._setup_table()

        layout.addWidget(
            self._table,
            1,
        )
        layout.addWidget(
            self._open_question_button
        )

        close_button = QPushButton(
            "Bezárás"
        )

        close_button.clicked.connect(
            self.accept
        )
        self._connect_signals()

        layout.addWidget(
            close_button
        )

    def _setup_table(self) -> None:
        self._table.setColumnCount(
            7
        )

        self._table.setHorizontalHeaderLabels(
            [
                "Technical ID",
                "Kérdéskód",
                "Kategória",
                "Téma",
                "Altéma",
                "Típus",
                "Kérdés",
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
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
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

        header.setSectionResizeMode(
            6,
            QHeaderView.ResizeMode.Stretch,
        )

        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

    def _load_definitions(self) -> None:
        self._table.setRowCount(
            len(
                self._definitions
            )
        )

        for row, definition in enumerate(
            self._definitions
        ):
            category = (
                definition.category.value
                if hasattr(
                    definition.category,
                    "value",
                )
                else str(
                    definition.category
                )
            )

            question_type = (
                definition.question_type.value
                if hasattr(
                    definition.question_type,
                    "value",
                )
                else str(
                    definition.question_type
                )
            )

            values = [
                definition.question.question_id,
                definition.question.question_code,
                category,
                definition.topic,
                definition.subtopic or "",
                question_type,
                definition.title,
            ]

            for column, value in enumerate(
                values
            ):
                self._table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    ),
                )

    def _connect_signals(self) -> None:
        self._search_input.textChanged.connect(
            self._apply_filters
        )

        self._category_filter.currentTextChanged.connect(
            self._apply_filters
        )
        self._table.itemSelectionChanged.connect(
            self._update_question_button_state
        )

        self._open_question_button.clicked.connect(
            self._open_selected_question
        )

        self._table.cellDoubleClicked.connect(
            self._open_question_from_double_click
        )

    def _update_question_button_state(
            self,
    ) -> None:
        has_selection = bool(
            self._table
            .selectionModel()
            .selectedRows()
        )

        self._open_question_button.setEnabled(
            has_selection
        )

    def _get_selected_definition(
            self,
    ) -> QuestionDefinition | None:
        selected_rows = (
            self._table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return None

        row = selected_rows[0].row()

        technical_id_item = (
            self._table.item(
                row,
                0,
            )
        )

        if technical_id_item is None:
            return None

        technical_id = (
            technical_id_item.text()
        )

        for definition in (
                self._definitions
        ):
            if (
                    definition
                            .question
                            .question_id
                    == technical_id
            ):
                return definition

        return None

    def _open_selected_question(
            self,
    ) -> None:
        definition = (
            self._get_selected_definition()
        )

        if definition is None:
            return

        dialog = QuestionDefinitionDetailsDialog(
            definition=definition,
            parent=self,
        )

        dialog.exec()

    def _open_question_from_double_click(
            self,
            row: int,
            column: int,
    ) -> None:
        self._table.selectRow(
            row
        )

        self._open_selected_question()

    def _apply_filters(self) -> None:
        search_text = (
            self._search_input
            .text()
            .strip()
            .lower()
        )

        selected_category = (
            self._category_filter
            .currentText()
        )

        for row in range(
                self._table.rowCount()
        ):
            row_values = []

            for column in range(
                    self._table.columnCount()
            ):
                item = self._table.item(
                    row,
                    column,
                )

                if item is not None:
                    row_values.append(
                        item.text().lower()
                    )

            matches_search = (
                    not search_text
                    or any(
                search_text in value
                for value in row_values
            )
            )

            category_item = (
                self._table.item(
                    row,
                    2,
                )
            )

            row_category = (
                category_item.text()
                if category_item is not None
                else ""
            )

            matches_category = (
                    selected_category
                    == "Összes kategória"
                    or row_category
                    == selected_category
            )

            self._table.setRowHidden(
                row,
                not (
                        matches_search
                        and matches_category
                ),
            )