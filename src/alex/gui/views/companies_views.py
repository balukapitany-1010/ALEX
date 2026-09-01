from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from alex.esg.domain.company import Company
from alex.esg.services.company_service import CompanyService
from alex.gui.dialogs.company_dialog import CompanyDialog


class CompaniesView(QWidget):
    def __init__(
        self,
        company_service: CompanyService,
    ) -> None:
        super().__init__()

        self._company_service = company_service

        self._search_input = QLineEdit()

        self._add_button = QPushButton(
            "+ Új cég"
        )

        self._open_button = QPushButton(
            "Megnyitás"
        )
        self._open_button.setEnabled(
            False
        )

        self._edit_button = QPushButton(
            "Szerkesztés"
        )
        self._edit_button.setEnabled(
            False
        )

        self._table = QTableWidget()

        self._setup_ui()
        self._connect_signals()
        self._refresh_table()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Cégek"
        )

        font = title.font()
        font.setPointSize(
            20
        )
        font.setBold(
            True
        )

        title.setFont(
            font
        )

        main_layout.addWidget(
            title
        )

        toolbar_layout = QHBoxLayout()

        self._search_input.setPlaceholderText(
            "Keresés cégnév vagy adószám alapján..."
        )

        toolbar_layout.addWidget(
            self._search_input,
            1,
        )

        toolbar_layout.addWidget(
            self._add_button
        )

        toolbar_layout.addWidget(
            self._open_button
        )

        toolbar_layout.addWidget(
            self._edit_button
        )

        main_layout.addLayout(
            toolbar_layout
        )

        self._setup_table()

        main_layout.addWidget(
            self._table
        )

    def _setup_table(self) -> None:
        self._table.setColumnCount(
            3
        )

        self._table.setHorizontalHeaderLabels(
            [
                "Cégnév",
                "Adószám",
                "Ország",
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
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self._table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

    def _connect_signals(self) -> None:
        self._search_input.textChanged.connect(
            self._filter_companies
        )

        self._add_button.clicked.connect(
            self._open_add_company_dialog
        )

        self._table.itemSelectionChanged.connect(
            self._update_button_state
        )

        self._open_button.clicked.connect(
            self._open_selected_company
        )

        self._edit_button.clicked.connect(
            self._edit_selected_company
        )

        self._table.cellDoubleClicked.connect(
            self._open_company_from_double_click
        )

    def _open_add_company_dialog(
        self,
    ) -> None:
        dialog = CompanyDialog(
            self
        )

        result = dialog.exec()

        if (
            result
            != QDialog.DialogCode.Accepted
        ):
            return

        try:
            self._company_service.create_company(
                name=dialog.company_name,
                tax_number=dialog.tax_number,
                country=dialog.country,
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Hibás cégadat",
                str(error),
            )
            return

        self._refresh_table()

    def _add_company_to_table(
        self,
        company: Company,
    ) -> None:
        row = self._table.rowCount()

        self._table.insertRow(
            row
        )

        self._table.setItem(
            row,
            0,
            QTableWidgetItem(
                company.name
            ),
        )

        self._table.setItem(
            row,
            1,
            QTableWidgetItem(
                company.tax_number
            ),
        )

        self._table.setItem(
            row,
            2,
            QTableWidgetItem(
                company.country or ""
            ),
        )

    def refresh(self) -> None:
        self._refresh_table()

    def _refresh_table(self) -> None:
        self._table.setRowCount(
            0
        )

        companies = (
            self._company_service
            .list_companies()
        )

        for company in companies:
            self._add_company_to_table(
                company
            )

        self._filter_companies(
            self._search_input.text()
        )

        self._table.clearSelection()

        self._update_button_state()

    def _filter_companies(
        self,
        text: str,
    ) -> None:
        search_text = (
            text.strip().lower()
        )

        for row in range(
            self._table.rowCount()
        ):
            company_name_item = (
                self._table.item(
                    row,
                    0,
                )
            )

            tax_number_item = (
                self._table.item(
                    row,
                    1,
                )
            )

            company_name = (
                company_name_item
                .text()
                .lower()
                if company_name_item
                is not None
                else ""
            )

            tax_number = (
                tax_number_item
                .text()
                .lower()
                if tax_number_item
                is not None
                else ""
            )

            matches = (
                not search_text
                or search_text
                in company_name
                or search_text
                in tax_number
            )

            self._table.setRowHidden(
                row,
                not matches,
            )

    def _update_button_state(
        self,
    ) -> None:
        selection_model = (
            self._table.selectionModel()
        )

        if selection_model is None:
            self._open_button.setEnabled(
                False
            )
            self._edit_button.setEnabled(
                False
            )
            return

        selected_rows = (
            selection_model.selectedRows()
        )

        has_selection = bool(
            selected_rows
        )

        self._open_button.setEnabled(
            has_selection
        )

        self._edit_button.setEnabled(
            has_selection
        )

    def _get_selected_company(
        self,
    ) -> Company | None:
        selection_model = (
            self._table.selectionModel()
        )

        if selection_model is None:
            return None

        selected_rows = (
            selection_model.selectedRows()
        )

        if not selected_rows:
            return None

        row = (
            selected_rows[0].row()
        )

        tax_number_item = (
            self._table.item(
                row,
                1,
            )
        )

        if tax_number_item is None:
            return None

        return (
            self._company_service
            .get_by_tax_number(
                tax_number_item.text()
            )
        )

    def _open_selected_company(
        self,
    ) -> None:
        company = (
            self._get_selected_company()
        )

        if company is None:
            return

        self._show_company_details(
            company
        )

    def _open_company_from_double_click(
        self,
        row: int,
        _column: int,
    ) -> None:
        tax_number_item = (
            self._table.item(
                row,
                1,
            )
        )

        if tax_number_item is None:
            return

        company = (
            self._company_service
            .get_by_tax_number(
                tax_number_item.text()
            )
        )

        if company is None:
            return

        self._show_company_details(
            company
        )

    def _show_company_details(
        self,
        company: Company,
    ) -> None:
        QMessageBox.information(
            self,
            "Cég adatai",
            (
                f"Cégnév: "
                f"{company.name}\n"
                f"Adószám: "
                f"{company.tax_number}\n"
                f"Ország: "
                f"{company.country or '-'}\n"
                f"Company key: "
                f"{company.company_key}"
            ),
        )

    def _edit_selected_company(
        self,
    ) -> None:
        company = (
            self._get_selected_company()
        )

        if company is None:
            return

        dialog = CompanyDialog(
            self,
            company=company,
        )

        result = dialog.exec()

        if (
            result
            != QDialog.DialogCode.Accepted
        ):
            return

        try:
            self._company_service.update_company(
                company.tax_number,
                name=dialog.company_name,
                country=dialog.country,
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            QMessageBox.critical(
                self,
                "Hibás cégadat",
                str(error),
            )
            return

        self._refresh_table()