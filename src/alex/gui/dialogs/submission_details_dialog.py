from PySide6.QtWidgets import (
QDialog,
QDialogButtonBox,
QFormLayout,
QLabel,
QVBoxLayout,
QTableWidget,
QTableWidgetItem,
QHeaderView,
QCheckBox,
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
        self._answered_only_checkbox = QCheckBox("Csak a kitöltött válaszok")
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Beküldés Részletei")
        self.setMinimumWidth(550)
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()


        form_layout.addRow("Submission ID:",QLabel(str(self._submission.submission_id)),)
        form_layout.addRow("Kötelezett / Cég:", QLabel(self._submission.relation.requester.name),)
        submitter_text = (
            self._submission.submitter.name
            if self._submission.submitter
               is not None
            else "-"
        )

        form_layout.addRow("Beküldő:",QLabel(submitter_text),)
        form_layout.addRow("Beszállító:",QLabel(self._submission.relation.supplier.name),)

        questionnaire_text = (
            f"{self._submission.questionnaire.questionnaire_code} "
            f"{self._submission.questionnaire.spec_version} "
            f"{self._submission.questionnaire.locale}"
        )

        form_layout.addRow("Kérdőív:",QLabel(questionnaire_text),)
        form_layout.addRow("Vonatkozási időszak:",QLabel(self._submission.period or "-"),)
        form_layout.addRow("Státusz:",QLabel(self._submission.status.value),)
        form_layout.addRow(
            "Válaszok száma:",
            QLabel(str(len(self._submission.answers))),
        )

        form_layout.addRow(
            "Kitöltött válaszok:",
            QLabel(
                (
                    f"{self._submission.answered_count} / "
                    f"{len(self._submission.answers)}"
                )
            ),
        )
        main_layout.addLayout(
            form_layout
        )

        answers_title = QLabel("Válaszok")
        answers_font = answers_title.font()
        answers_font.setBold(True)
        answers_font.setPointSize(14)
        answers_title.setFont(answers_font)
        main_layout.addWidget(answers_title)
        main_layout.addWidget(self._answered_only_checkbox)
        self._answered_only_checkbox.stateChanged.connect(self._load_answers)
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

    def _load_answers(
            self,
            *_,
    ) -> None:
        self._answers_table.setRowCount(0)
        answered_only = (self._answered_only_checkbox.isChecked())

        for answer in (self._submission.answers
        ):
            if (
                    answered_only and not answer.is_answered
            ):
                continue

            row = (self._answers_table.rowCount())
            self._answers_table.insertRow(row)
            definition = (answer.question_definition)
            question = (definition.question)

            self._answers_table.setItem(
                row,
                0,
                QTableWidgetItem(question.question_code),
            )

            self._answers_table.setItem(
                row,
                1,
                QTableWidgetItem(definition.category.value),
            )

            self._answers_table.setItem(
                row,
                2,
                QTableWidgetItem(definition.topic),
            )

            self._answers_table.setItem(
                row,
                3,
                QTableWidgetItem(definition.title),
            )

            self._answers_table.setItem(
                row,
                4,
                QTableWidgetItem(definition.question_type.value),
            )

            self._answers_table.setItem(
                row,
                5,
                QTableWidgetItem(self._format_answer(answer)),
            )

    @staticmethod
    def _format_answer(
            answer,
    ) -> str:
        values: list[str] = []
        option_labels = {option.option_id: option.label for option in answer.question_definition.options}
        if answer.text_value is not None:
            text = str(answer.text_value).strip()
            if text:
                values.append(text)
        if answer.number_value is not None:
            values.append(str(answer.number_value))
        for option in answer.selected_options:
            values.append(option.label)
        for value in answer.values:
            if value.field_type in {
                "single",
                "multi",
            }:
                if value.selected is not True:
                    continue
                if value.option_id is None:
                    continue
                label = option_labels.get(
                    value.option_id,
                    value.option_id,
                )
                values.append(label)
            elif value.field_type == "text":
                if value.text_value is None:
                    continue
                text = str(value.text_value).strip()
                if text:
                    values.append(text)
            elif value.field_type == "number":
                if value.number_value is None:
                    continue
                number_text = str(value.number_value)
                if value.option_id is not None:
                    label = option_labels.get(value.option_id)
                    if label:
                        number_text = (
                            f"{label}: "
                            f"{number_text}"
                        )
                values.append(number_text)
        if not values:
            return "-"
        unique_values = list(dict.fromkeys(values))
        return "; ".join(unique_values)
