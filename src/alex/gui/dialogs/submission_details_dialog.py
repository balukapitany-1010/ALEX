from PySide6.QtWidgets import (
QDialog,
QDialogButtonBox,
QFormLayout,
QLabel,
QVBoxLayout,
QTableWidget,
QTableWidgetItem,
QHeaderView,
)
from alex.esg.domain.submission import Submission

class SubmissionDetailsDialog(QDialog):
    def __init__(
            self,
            submission: Submission,
            parent = None,
    ) -> None:
        super().__init__(parent)
        self._submission = submission
        self._answers_table = QTableWidget()
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Beküldés Részletei")
        self.setMinimumWidth(550)
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()


        form_layout.addRow("Submission ID:",QLabel(str(self._submission.submission_id)),)
        form_layout.addRow("Kötelezett / Cég:", QLabel(self._submission.relation.requester.name),)
        form_layout.addRow("Beküldő:",QLabel(self._submission.submitter.name),)
        form_layout.addRow("Beszállító:",QLabel(self._submission.relation.supplier.name),)

        questionnaire_text = (
            f"{self._submission.questionnaire.questionnaire_code}"
            f"{self._submission.questionnaire.spec_version}"
            f"{self._submission.questionnaire.locale}"
        )

        form_layout.addRow("Kérdőív:",QLabel(questionnaire_text),)
        form_layout.addRow("Vonatkozási időszak:",QLabel(self._submission.period),)
        form_layout.addRow("státusz:",QLabel(str(self._submission.status)),)
        form_layout.addRow("Válaszok száma:",QLabel(str(len(self._submission.answers))),)
        main_layout.addLayout(form_layout)

        answers_title = QLabel("Válaszok")
        answers_font = answers_title.font()
        answers_font.setBold(True)
        answers_font.setPointSize(14)

        answers_title.setFont(answers_font)
        main_layout.addWidget(answers_title)
        self._setup_answers_table()
        main_layout.addWidget(self._answers_table)
        self._load_answers()




        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def _setup_answers_table(self) -> None:
        self._answers_table.setColumnCount(6)

        self._answers_table.setHorizontalHeaderLabels(
            [
                "Kérdéskód",
                "Kategória",
                "Téma",
                "Kérdés",
                "Típus",
                "Válasz",
            ]
        )

        header = self._answers_table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents,)

        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents,)

        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch,)

        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch,)

        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents,)

        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch,)

        self._answers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._answers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

    def _load_answers(self) -> None:
        self._answers_table.setRowCount(0)

        for answer in self._submission.answers:
            row = self._answers_table.rowCount()

            self._answers_table.insertRow(row)

            definition = answer.question_definition
            question = definition.question

            self._answers_table.setItem(row, 0, QTableWidgetItem(question.question_code),)

            self._answers_table.setItem(row, 1, QTableWidgetItem(definition.category.value),)

            self._answers_table.setItem(row, 2, QTableWidgetItem(definition.topic),)

            self._answers_table.setItem(row, 3, QTableWidgetItem(definition.title),)

            self._answers_table.setItem(row, 4, QTableWidgetItem(definition.question_type.value),)

            self._answers_table.setItem(row, 5, QTableWidgetItem(self._format_answer(answer)),)

    @staticmethod
    def _format_answer(answer) -> str:
        values: list[str] = []

        if answer.text_value is not None:
            text = str(answer.text_value).strip()

            if text:
                values.append(text)

        if answer.number_value is not None:
            values.append(str(answer.number_value))

        if answer.selected_options:
            option_values = []

            for option in answer.selected_options:
                if hasattr(option, "label"):
                    option_values.append(str(option.label))
                else:
                    option_values.append(str(option))

            values.extend(option_values)

        if not values:
            return "-"

        return "; ".join(values)
