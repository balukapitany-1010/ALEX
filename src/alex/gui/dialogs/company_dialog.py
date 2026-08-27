from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from alex.esg.domain.company import Company


class CompanyDialog(QDialog):
    def __init__(
        self,
        parent=None,
        company: Company | None = None,
    ) -> None:
        super().__init__(parent)

        self._company = company

        self._name_input = QLineEdit()
        self._tax_number_input = QLineEdit()
        self._country_input = QLineEdit()

        self._setup_ui()
        self._load_company()

    def _setup_ui(self) -> None:
        if self._company is None:
            self.setWindowTitle("Új cég")
        else:
            self.setWindowTitle("Cég szerkesztése")

        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self._name_input.setPlaceholderText(
            "Pl. Minta Kft."
        )

        self._tax_number_input.setPlaceholderText(
            "Pl. 12345678-2-41"
        )

        self._country_input.setPlaceholderText(
            "Pl. HU"
        )

        form_layout.addRow(
            "Cégnév:",
            self._name_input,
        )

        form_layout.addRow(
            "Adószám:",
            self._tax_number_input,
        )

        form_layout.addRow(
            "Ország:",
            self._country_input,
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

    def _load_company(self) -> None:
        if self._company is None:
            return

        self._name_input.setText(
            self._company.name
        )

        self._tax_number_input.setText(
            self._company.tax_number
        )

        self._country_input.setText(
            self._company.country or ""
        )

        self._tax_number_input.setReadOnly(True)

    def _validate_and_accept(self) -> None:
        if not self.company_name:
            QMessageBox.warning(
                self,
                "Hiányzó adat",
                "A cégnév megadása kötelező.",
            )
            return

        if not self.tax_number:
            QMessageBox.warning(
                self,
                "Hiányzó adat",
                "Az adószám megadása kötelező.",
            )
            return

        self.accept()

    @property
    def company_name(self) -> str:
        return self._name_input.text().strip()

    @property
    def tax_number(self) -> str:
        return self._tax_number_input.text().strip()

    @property
    def country(self) -> str | None:
        value = self._country_input.text().strip()

        return value if value else None