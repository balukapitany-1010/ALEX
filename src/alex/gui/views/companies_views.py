from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class CompaniesView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._search_input = QLineEdit()
        self._add_button = QPushButton("+ Új cég")
        self._table = QTableWidget()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("Cégek")

        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)

        main_layout.addWidget(title)

        toolbar_layout = QHBoxLayout()

        self._search_input.setPlaceholderText(
            "Keresés cégnév vagy adószám alapján..."
        )

        toolbar_layout.addWidget(self._search_input)
        toolbar_layout.addWidget(self._add_button)

        main_layout.addLayout(toolbar_layout)

        self._setup_table()

        main_layout.addWidget(self._table)

    def _setup_table(self) -> None:
        self._table.setColumnCount(3)

        self._table.setHorizontalHeaderLabels(
            [
                "Cégnév",
                "Adószám",
                "Ország",
            ]
        )

        header = self._table.horizontalHeader()

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
            QTableWidget.SelectionBehavior.SelectRows
        )

        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

    def _connect_signals(self) -> None:
        self._search_input.textChanged.connect(
            self._filter_companies
        )

        self._add_button.clicked.connect(
            self._add_test_company
        )

    def _add_test_company(self) -> None:
        row = self._table.rowCount()

        self._table.insertRow(row)

        self._table.setItem(
            row,
            0,
            QTableWidgetItem("Teszt Kft."),
        )

        self._table.setItem(
            row,
            1,
            QTableWidgetItem("12345678-2-41"),
        )

        self._table.setItem(
            row,
            2,
            QTableWidgetItem("HU"),
        )

    def _filter_companies(self, text: str) -> None:
        search_text = text.strip().lower()

        for row in range(self._table.rowCount()):
            company_name_item = self._table.item(row, 0)
            tax_number_item = self._table.item(row, 1)

            company_name = (
                company_name_item.text().lower()
                if company_name_item
                else ""
            )

            tax_number = (
                tax_number_item.text().lower()
                if tax_number_item
                else ""
            )

            matches = (
                search_text in company_name
                or search_text in tax_number
            )

            self._table.setRowHidden(
                row,
                not matches,
            )