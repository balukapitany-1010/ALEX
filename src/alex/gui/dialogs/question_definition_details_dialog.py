from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from alex.esg.domain.question_definition import (
    QuestionDefinition,
)


class QuestionDefinitionDetailsDialog(QDialog):
    def __init__(
        self,
        *,
        definition: QuestionDefinition,
        parent=None,
    ) -> None:
        super().__init__(parent)

        if not isinstance(
            definition,
            QuestionDefinition,
        ):
            raise TypeError(
                "definition must be a "
                "QuestionDefinition"
            )

        self._definition = definition

        self.setWindowTitle(
            (
                f"Kérdés - "
                f"{definition.question.question_code}"
            )
        )

        self.resize(
            760,
            620,
        )

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            self._definition.title
        )

        title.setWordWrap(
            True
        )

        font = title.font()
        font.setPointSize(16)
        font.setBold(True)

        title.setFont(
            font
        )

        layout.addWidget(
            title
        )

        form = QFormLayout()

        form.addRow(
            "Technical ID:",
            QLabel(
                self._definition
                .question
                .question_id
            ),
        )

        form.addRow(
            "Kérdéskód:",
            QLabel(
                self._definition
                .question
                .question_code
            ),
        )

        form.addRow(
            "Kategória:",
            QLabel(
                self._enum_text(
                    self._definition.category
                )
            ),
        )

        form.addRow(
            "Típus:",
            QLabel(
                self._enum_text(
                    self._definition.question_type
                )
            ),
        )

        form.addRow(
            "Téma:",
            QLabel(
                self._definition.topic
            ),
        )

        form.addRow(
            "Altéma:",
            QLabel(
                self._definition.subtopic
                or "-"
            ),
        )

        form.addRow(
            "Követelmény:",
            QLabel(
                self._definition.requirement
                or "-"
            ),
        )

        form.addRow(
            "Szervezet:",
            QLabel(
                self._definition.organization
            ),
        )

        layout.addLayout(
            form
        )

        organization_sizes = QTextEdit()
        organization_sizes.setReadOnly(
            True
        )

        organization_sizes.setPlainText(
            "\n".join(
                self._definition.organization_sizes
            )
            or "-"
        )

        layout.addWidget(
            QLabel(
                "Szervezetméretek:"
            )
        )

        layout.addWidget(
            organization_sizes
        )

        geographical = QTextEdit()
        geographical.setReadOnly(
            True
        )

        geographical.setPlainText(
            "\n".join(
                self._definition
                .geographical_relevance
            )
            or "-"
        )

        layout.addWidget(
            QLabel(
                "Földrajzi relevancia:"
            )
        )

        layout.addWidget(
            geographical
        )

        allowed_ids = QTextEdit()
        allowed_ids.setReadOnly(
            True
        )

        allowed_ids.setPlainText(
            "\n".join(
                self._definition.allowed_value_ids
            )
            or "-"
        )

        layout.addWidget(
            QLabel(
                "Engedélyezett value ID-k:"
            )
        )

        layout.addWidget(
            allowed_ids
        )

        close_button = QPushButton(
            "Bezárás"
        )

        close_button.clicked.connect(
            self.accept
        )

        layout.addWidget(
            close_button
        )

    @staticmethod
    def _enum_text(
        value,
    ) -> str:
        if hasattr(
            value,
            "value",
        ):
            return str(
                value.value
            )

        return str(
            value
        )