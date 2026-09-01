from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from alex.esg.domain.question_definition import QuestionDefinition
from alex.esg.domain.submission import Submission


class AttachmentDialog(QDialog):
    def __init__(
        self,
        *,
        submissions: tuple[Submission, ...],
        question_definitions: tuple[
            QuestionDefinition,
            ...
        ],
        parent=None,
    ) -> None:
        super().__init__(parent)

        if not isinstance(
            submissions,
            tuple,
        ):
            raise TypeError("submissions must be a tuple")

        if not all(
            isinstance(
                submission,
                Submission,
            )
            for submission in submissions
        ):
            raise TypeError(
                "submissions must contain only "
                "Submission objects"
            )

        if not isinstance(
            question_definitions,
            tuple,
        ):
            raise TypeError("question_definitions must be a tuple")

        if not all(
            isinstance(
                definition,
                QuestionDefinition,
            )
            for definition in question_definitions
        ):
            raise TypeError(
                "question_definitions must contain only "
                "QuestionDefinition objects"
            )

        self._submissions = submissions
        self._question_definitions = ( question_definitions)
        self._submission_combo = QComboBox()
        self._question_combo = QComboBox()
        self._file_input = QLineEdit()
        self._file_input.setReadOnly(True)
        self._browse_button = QPushButton("Tallózás..." )
        self._save_button = QPushButton("Hozzáadás")
        self._cancel_button = QPushButton("Mégse")
        self._save_button.setEnabled(False)
        self.setWindowTitle( "Dokumentum hozzáadása")
        self.resize(
            700,
            220,
        )
        self._setup_ui()
        self._load_submissions()
        self._connect_signals()
        self._refresh_questions()

    @property
    def submission(self) -> Submission | None:
        index = (self._submission_combo.currentIndex())

        if (index < 0 or index >= len(self._submissions)):
            return None

        return self._submissions[index]

    @property
    def question_definition(
        self,
    ) -> QuestionDefinition | None:
        data = (self._question_combo.currentData())

        if isinstance(
            data,
            QuestionDefinition,
        ):
            return data

        return None

    @property
    def file_path(self) -> str:
        return (self._file_input.text().strip())

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        form.addRow(
            "Beküldés:",
            self._submission_combo,
        )

        form.addRow(
            "Kérdés:",
            self._question_combo,
        )

        file_layout = QHBoxLayout()

        file_layout.addWidget(
            self._file_input,
            1,
        )

        file_layout.addWidget(self._browse_button)

        form.addRow(
            "Fájl:",
            file_layout,
        )

        layout.addLayout(form)

        layout.addStretch()

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        button_layout.addWidget(self._cancel_button)

        button_layout.addWidget(self._save_button)

        layout.addLayout(button_layout)

    def _load_submissions(self) -> None:
        self._submission_combo.clear()

        for submission in (self._submissions):
            text = (
                f"{submission.relation.supplier.name} | "
                f"{submission.period} | "
                f"{submission.submission_id}"
            )

            self._submission_combo.addItem(text)

    def _connect_signals(self) -> None:
        self._submission_combo.currentIndexChanged.connect( self._refresh_questions)

        self._browse_button.clicked.connect(self._select_file)

        self._file_input.textChanged.connect(self._update_save_button)

        self._save_button.clicked.connect(self._accept)

        self._cancel_button.clicked.connect(self.reject)

    def _refresh_questions(self) -> None:
        self._question_combo.clear()

        self._question_combo.addItem(
            "Teljes beküldéshez",
            None,
        )

        submission = self.submission

        if submission is None:
            return

        for definition in (self._question_definitions):
            if not self._same_questionnaire(
                definition,
                submission,
            ):
                continue

            text = (
                f"{definition.question.question_code} - "
                f"{definition.title}"
            )

            self._question_combo.addItem(
                text,
                definition,
            )

    def _select_file(self) -> None:
        filename, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Dokumentum kiválasztása",
                "",
                "Minden fájl (*.*)",
            )
        )

        if not filename:
            return

        self._file_input.setText(filename)

    def _update_save_button(self) -> None:
        self._save_button.setEnabled(self.submission is not None and bool(self.file_path))

    def _accept(self) -> None:
        path = Path(self.file_path)

        if not path.is_file():
            QMessageBox.warning(
                self,
                "Fájl nem található",
                "A kiválasztott fájl nem található.",
            )

            return

        if self.submission is None:
            QMessageBox.warning(
                self,
                "Nincs beküldés",
                "Válassz egy beküldést.",
            )

            return

        self.accept()

    @staticmethod
    def _same_questionnaire(
        definition: QuestionDefinition,
        submission: Submission,
    ) -> bool:
        definition_questionnaire = (definition.questionnaire )

        submission_questionnaire = (submission.questionnaire)

        return (
            definition_questionnaire.questionnaire_code == submission_questionnaire.questionnaire_code
            and definition_questionnaire.spec_version == submission_questionnaire.spec_version
            and definition_questionnaire.locale.lower() == submission_questionnaire.locale.lower()
        )