from PySide6.QtWidgets import (
    QFileDialog,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from alex.esg.services.question_definition_read_service import QuestionDefinitionReadService
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.services.question_definition_service import QuestionDefinitionService
from alex.esg.services.questionnaire_service import QuestionnaireService
from alex.gui.dialogs.questionnaire_details_dialog import QuestionnaireDetailsDialog
from alex.esg.services.questionnaire_definition_file_import_service import QuestionnaireDefinitionFileImportService

class QuestionnairesView(QWidget):
    def __init__(
            self,
            *,
            questionnaire_service: QuestionnaireService,
            question_definition_service: QuestionDefinitionService,
            definition_file_import_service: (QuestionnaireDefinitionFileImportService),
            question_definition_read_service: (QuestionDefinitionReadService | None) = None,
            read_only: bool = False,
            parent=None,
    ) -> None:
        super().__init__(parent)

        if not isinstance(
                questionnaire_service,
                QuestionnaireService,
        ):
            raise TypeError(
                "questionnaire_service must be a "
                "QuestionnaireService"
            )

        if not isinstance(
                question_definition_service,
                QuestionDefinitionService,
        ):
            raise TypeError(
                "question_definition_service must be a "
                "QuestionDefinitionService"
            )

        if not isinstance(
                definition_file_import_service,
                QuestionnaireDefinitionFileImportService,
        ):
            raise TypeError(
                "definition_file_import_service must be a "
                "QuestionnaireDefinitionFileImportService"
            )

        if (
                question_definition_read_service
                is not None and not isinstance(
            question_definition_read_service,
            QuestionDefinitionReadService,
        )
        ):
            raise TypeError(
                "question_definition_read_service must be a "
                "QuestionDefinitionReadService or None"
            )

        self._questionnaire_service = (questionnaire_service)
        self._question_definition_service = (question_definition_service)
        self._definition_file_import_service = (definition_file_import_service)
        self._question_definition_read_service = (question_definition_read_service)
        self._read_only = read_only
        self._open_button = QPushButton("Megnyitás")
        self._open_button.setEnabled(False)
        self._import_button = QPushButton( "+ Kérdőív importálása")
        if self._read_only:
            self._import_button.setEnabled(False)
            self._import_button.setToolTip(
                "Az MSSQL kérdőív import még "
                "nincs bekötve."
            )

        self._table = QTableWidget()
        self._setup_ui()
        self._connect_signals()
        self.refresh()
        if not isinstance(
                definition_file_import_service,
                QuestionnaireDefinitionFileImportService,
        ):
            raise TypeError(
                "definition_file_import_service must be a "
                "QuestionnaireDefinitionFileImportService"
            )

        self._definition_file_import_service = (definition_file_import_service)
        self._question_definition_read_service = (question_definition_read_service)
        self._read_only = read_only
        if self._read_only:
            self._import_button.setEnabled(False )
            self._import_button.setToolTip(
                "Az MSSQL kérdőív import még "
                "nincs bekötve."
            )

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        title = QLabel("Kérdőívek")
        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self._open_button)
        toolbar_layout.addWidget(self._import_button)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        self._setup_table()
        layout.addWidget(self._table)

    def _setup_table(self) -> None:
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(
            [
                "Kód",
                "Verzió",
                "Nyelv",
                "Kérdések száma",
            ]
        )

        header = (self._table.horizontalHeader())
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
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
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def _connect_signals(self) -> None:
        self._table.itemSelectionChanged.connect(self._update_button_state)
        self._open_button.clicked.connect(self._open_selected_questionnaire)
        self._table.cellDoubleClicked.connect(self._open_questionnaire_from_double_click)
        self._import_button.clicked.connect(self._import_questionnaire_definition)

    def _import_questionnaire_definition(
            self,
    ) -> None:
        if self._read_only:
            return
        definition_file, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Kérdőív-definíció kiválasztása",
                "",
                "JSON fájlok (*.json)",
            )
        )

        if not definition_file:
            return

        try:
            result = (
                self._definition_file_import_service
                .import_file(
                    definition_file=definition_file,
                    questionnaire_code="SZTFH-ESG",
                )
            )

        except (
                FileNotFoundError,
                TypeError,
                ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Kérdőív import hiba",
                str(error),
            )

            return

        self.refresh()

        QMessageBox.information(
            self,
            "Kérdőív import",
            (
                "Kérdőív sikeresen feldolgozva.\n\n"
                f"Kód: "
                f"{result.questionnaire.questionnaire_code}\n"
                f"Verzió: "
                f"{result.questionnaire.spec_version}\n"
                f"Nyelv: "
                f"{result.questionnaire.locale}\n"
                f"Kérdések: "
                f"{result.definition_count}\n"
                f"Új definíciók: "
                f"{result.added_count}\n"
                f"Már létező definíciók: "
                f"{result.reused_count}"
            ),
        )

    def _list_definitions(
            self,
            questionnaire: Questionnaire,
    ):
        if (
                self._question_definition_read_service is not None
        ):
            return (self._question_definition_read_service.list_for_questionnaire(questionnaire))

        return (self._question_definition_service.list_for_questionnaire(questionnaire))

    def refresh(self) -> None:
        self._table.setRowCount(0)
        for questionnaire in (self._questionnaire_service.list_questionnaires()):
            self._add_questionnaire_to_table(questionnaire)

    def _add_questionnaire_to_table(
        self,
        questionnaire: Questionnaire,
    ) -> None:
        definitions = (self._list_definitions(questionnaire))
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(
            row,
            0,
            QTableWidgetItem(questionnaire.questionnaire_code),
        )
        self._table.setItem(
            row,
            1,
            QTableWidgetItem(questionnaire.spec_version),
        )
        self._table.setItem(
            row,
            2,
            QTableWidgetItem(questionnaire.locale),
        )
        self._table.setItem(
            row,
            3,
            QTableWidgetItem(str(len(definitions))),
        )

    def _update_button_state(
        self,
    ) -> None:
        has_selection = bool(
            self._table
            .selectionModel()
            .selectedRows()
        )

        self._open_button.setEnabled(has_selection)

    def _get_selected_questionnaire(
        self,
    ) -> Questionnaire | None:
        selected_rows = (
            self._table
            .selectionModel()
            .selectedRows()
        )

        if not selected_rows:
            return None

        row = selected_rows[0].row()

        code_item = self._table.item(
            row,
            0,
        )

        version_item = self._table.item(
            row,
            1,
        )

        locale_item = self._table.item(
            row,
            2,
        )

        if (
            code_item is None
            or version_item is None
            or locale_item is None
        ):
            return None

        return (
            self._questionnaire_service
            .get_by_identity(questionnaire_code=(code_item.text()),
                spec_version=(version_item.text()),
                locale=(locale_item.text()),
            )
        )

    def _open_selected_questionnaire(
        self,
    ) -> None:
        questionnaire = (self._get_selected_questionnaire())

        if questionnaire is None:
            QMessageBox.warning(
                self,
                "Kérdőív",
                "A kiválasztott kérdőív "
                "nem található.",
            )

            return

        self._open_questionnaire(questionnaire)

    def _open_questionnaire_from_double_click(
        self,
        row: int,
        column: int,
    ) -> None:
        self._table.selectRow(row)

        self._open_selected_questionnaire()

    def _open_questionnaire(
            self,
            questionnaire: Questionnaire,
    ) -> None:
        definitions = (self._list_definitions(questionnaire))
        if not definitions:
            QMessageBox.information(
                self,
                "Nincs kérdésdefiníció",
                (
                    "Ehhez a kérdőívverzióhoz "
                    "nincs betöltött "
                    "kérdésdefiníció.\n\n"
                    f"Kód: "
                    f"{questionnaire.questionnaire_code}\n"
                    f"Verzió: "
                    f"{questionnaire.spec_version}\n"
                    f"Nyelv: "
                    f"{questionnaire.locale}"
                ),
            )
            return

        dialog = QuestionnaireDetailsDialog(
            questionnaire=questionnaire,
            definitions=definitions,
            parent=self,
        )

        dialog.exec()