from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QMessageBox,
    QVBoxLayout,
)

from alex.esg.domain.company import Company
from alex.esg.domain.supplier import Supplier


class SupplyChainRelationDialog(QDialog):
    def __init__(
        self,
        companies: tuple[Company, ...],
        suppliers: tuple[Supplier, ...],
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._companies = companies
        self._suppliers = suppliers

        self._company_combo = QComboBox()
        self._supplier_combo = QComboBox()

        self._setup_ui()
        self._load_items()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Új beszállítói kapcsolat")
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        form_layout.addRow(
            "Cég / kötelezett:",
            self._company_combo,
        )

        form_layout.addRow(
            "Beszállító:",
            self._supplier_combo,
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

    def _load_items(self) -> None:
        for company in self._companies:
            self._company_combo.addItem(
                f"{company.name} ({company.tax_number})"
            )

        for supplier in self._suppliers:
            self._supplier_combo.addItem(
                f"{supplier.name} ({supplier.tax_number})"
            )

    def _validate_and_accept(self) -> None:
        if not self._companies:
            QMessageBox.warning(
                self,
                "Nincs cég",
                "Először legalább egy céget létre kell hozni.",
            )
            return

        if not self._suppliers:
            QMessageBox.warning(
                self,
                "Nincs beszállító",
                "Először legalább egy beszállítót létre kell hozni.",
            )
            return

        self.accept()

    @property
    def requester(self) -> Company:
        index = self._company_combo.currentIndex()

        return self._companies[index]

    @property
    def supplier(self) -> Supplier:
        index = self._supplier_combo.currentIndex()

        return self._suppliers[index]