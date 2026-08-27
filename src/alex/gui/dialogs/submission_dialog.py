from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from alex.esg.domain.company import Company
from alex.esg.domain.questionnaire import Questionnaire
from alex.esg.domain.supply_chain_relation import SupplyChainRelation


class SubmissionDialog(QDialog):
    def __init__(
        self,
        relations: tuple[SupplyChainRelation, ...],
        questionnaires: tuple[Questionnaire, ...],
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._relations = relations
        self._questionnaires = questionnaires

        self._relation_combo = QComboBox()
        self._submitter_combo = QComboBox()
        self._questionnaire_combo = QComboBox()
        self._period_input = QLineEdit()

        self._setup_ui()
        self._load_relations()
        self._load_questionnaires()
        self._update_submitters()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Új tesztbeküldés")
        self.setMinimumWidth(500)

        main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        form_layout.addRow(
            "Beszállítói kapcsolat:",
            self._relation_combo,
        )

        form_layout.addRow(
            "Beküldő:",
            self._submitter_combo,
        )

        form_layout.addRow(
            "Kérdőív:",
            self._questionnaire_combo,
        )

        self._period_input.setPlaceholderText(
            "Pl. 2026-Q2"
        )

        form_layout.addRow(
            "Vonatkozási időszak:",
            self._period_input,
        )

        main_layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self._validate_and_accept
        )

        buttons.rejected.connect(
            self.reject
        )

        main_layout.addWidget(buttons)

        self._relation_combo.currentIndexChanged.connect(
            self._update_submitters
        )

    def _load_relations(self) -> None:
        for relation in self._relations:
            self._relation_combo.addItem(
                (
                    f"{relation.requester.name}"
                    f" → "
                    f"{relation.supplier.name}"
                )
            )

    def _load_questionnaires(self) -> None:
        for questionnaire in self._questionnaires:
            self._questionnaire_combo.addItem(
                (
                    f"{questionnaire.questionnaire_code} "
                    f"{questionnaire.spec_version} "
                    f"({questionnaire.locale})"
                )
            )

    def _update_submitters(self) -> None:
        self._submitter_combo.clear()

        if not self._relations:
            return

        index = self._relation_combo.currentIndex()

        if index < 0:
            return

        relation = self._relations[index]

        self._submitter_combo.addItem(
            (
                f"{relation.requester.name} "
                f"({relation.requester.tax_number})"
            )
        )

        self._submitter_combo.addItem(
            (
                f"{relation.supplier.name} "
                f"({relation.supplier.tax_number})"
            )
        )

    def _validate_and_accept(self) -> None:
        if not self._relations:
            QMessageBox.warning(
                self,
                "Nincs beszállítói kapcsolat",
                (
                    "Először legalább egy "
                    "beszállítói kapcsolatot létre kell hozni."
                ),
            )
            return

        if not self._questionnaires:
            QMessageBox.warning(
                self,
                "Nincs kérdőív",
                "Először legalább egy kérdőív szükséges.",
            )
            return

        if not self.period:
            QMessageBox.warning(
                self,
                "Hiányzó időszak",
                "A vonatkozási időszak megadása kötelező.",
            )
            return

        self.accept()

    @property
    def relation(self) -> SupplyChainRelation:
        return self._relations[
            self._relation_combo.currentIndex()
        ]

    @property
    def questionnaire(self) -> Questionnaire:
        return self._questionnaires[
            self._questionnaire_combo.currentIndex()
        ]

    @property
    def submitter(self) -> Company:
        relation = self.relation

        if self._submitter_combo.currentIndex() == 0:
            return relation.requester

        return relation.supplier

    @property
    def period(self) -> str:
        return self._period_input.text().strip()