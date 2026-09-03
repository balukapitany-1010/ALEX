from PySide6.QtWidgets import (
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

from alex.esg.domain.supplier import Supplier
from alex.esg.services.supplier_service import SupplierService
from alex.gui.dialogs.supplier_dialog import SupplierDialog
from alex.esg.services.company_service import CompanyService
from alex.esg.services.supply_chain_relation_service import (SupplyChainRelationService,)
from alex.gui.dialogs.supply_chain_relation_dialog import (SupplyChainRelationDialog,)


class SuppliersView(QWidget):
    def __init__(
            self,
            supplier_service: SupplierService,
            company_service: CompanyService,
            relation_service: SupplyChainRelationService,
            read_only: bool = False,
    ) -> None:
        super().__init__()

        self._supplier_service = supplier_service
        self._company_service = company_service
        self._relation_service = relation_service
        self._read_only = read_only

        self._search_input = QLineEdit()
        self._open_button = QPushButton("Megnyitás")
        self._add_button = QPushButton("+ Új beszállító")
        self._add_relation_button = QPushButton(
            "+ Beszállítói kapcsolat"
        )

        self._table = QTableWidget()
        self._relations_table = QTableWidget()

        self._open_button.setEnabled(False)
        if self._read_only:
            self._add_button.setEnabled(False)
            self._add_relation_button.setEnabled(False)

            self._add_button.setToolTip(
                "Az MSSQL beszállító létrehozás "
                "még nincs engedélyezve."
            )

            self._add_relation_button.setToolTip(
                "Az MSSQL kapcsolat létrehozás "
                "még nincs engedélyezve."
            )

        self._setup_ui()
        self._connect_signals()

        self._refresh_table()
        self._refresh_relations_table()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("Beszállítók")

        font = title.font()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)

        main_layout.addWidget(title)

        toolbar_layout = QHBoxLayout()

        toolbar_layout.addWidget(
            self._add_relation_button
        )

        self._search_input.setPlaceholderText(
            "Keresés cégnév vagy adószám alapján..."
        )

        toolbar_layout.addWidget(
            self._search_input
        )

        toolbar_layout.addWidget(
            self._open_button
        )

        toolbar_layout.addWidget(
            self._add_button
        )

        main_layout.addLayout(
            toolbar_layout
        )

        self._setup_table()

        main_layout.addWidget(
            self._table
        )
        relations_title = QLabel(
            "Beszállítói kapcsolatok"
        )

        relations_font = relations_title.font()
        relations_font.setPointSize(14)
        relations_font.setBold(True)

        relations_title.setFont(
            relations_font
        )

        main_layout.addWidget(
            relations_title
        )

        self._setup_relations_table()

        main_layout.addWidget(
            self._relations_table
        )

    def _setup_table(self) -> None:
        self._table.setColumnCount(3)

        self._table.setHorizontalHeaderLabels(
            [
                "Beszállító neve",
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
            self._filter_suppliers
        )

        self._add_button.clicked.connect(
            self._open_add_supplier_dialog
        )

        self._open_button.clicked.connect(
            self._open_selected_supplier
        )

        self._table.itemSelectionChanged.connect(
            self._update_button_state
        )

        self._table.cellDoubleClicked.connect(
            self._open_supplier_from_double_click
        )
        self._add_relation_button.clicked.connect(
            self._open_add_relation_dialog
        )

    def _open_add_relation_dialog(self) -> None:
        companies = (
            self._company_service.list_companies()
        )

        suppliers = (
            self._supplier_service.list_suppliers()
        )

        dialog = SupplyChainRelationDialog(
            companies=companies,
            suppliers=suppliers,
            parent=self,
        )

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            return

        try:
            self._relation_service.create_relation(
                requester=dialog.requester,
                supplier=dialog.supplier,
            )
        except (TypeError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Kapcsolat létrehozási hiba",
                str(error),
            )
            return

        self._refresh_relations_table()

    def _refresh_relations_table(self) -> None:
        self._relations_table.setRowCount(0)

        for relation in (
                self._relation_service.list_relations()
        ):
            row = self._relations_table.rowCount()

            self._relations_table.insertRow(row)

            self._relations_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    relation.requester.name
                ),
            )

            self._relations_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    relation.supplier.name
                ),
            )

            self._relations_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    relation.created_at.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                ),
            )

    def _open_add_supplier_dialog(self) -> None:
        dialog = SupplierDialog(self)

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            return

        try:
            self._supplier_service.create_supplier(
                name=dialog.company_name,
                tax_number=dialog.tax_number,
                country=dialog.country,
            )
        except (TypeError, ValueError) as error:
            QMessageBox.critical(
                self,
                "Hibás beszállítói adat",
                str(error),
            )
            return

        self._refresh_table()

    def _get_selected_supplier(
        self,
    ) -> Supplier | None:
        selected_rows = (
            self._table.selectionModel().selectedRows()
        )

        if not selected_rows:
            return None

        row = selected_rows[0].row()

        tax_number_item = self._table.item(
            row,
            1,
        )

        if tax_number_item is None:
            return None

        return self._supplier_service.get_by_tax_number(
            tax_number_item.text()
        )

    def _open_selected_supplier(self) -> None:
        supplier = self._get_selected_supplier()

        if supplier is None:
            return

        self._show_supplier_details(
            supplier
        )

    def _open_supplier_from_double_click(
        self,
        row: int,
        column: int,
    ) -> None:
        tax_number_item = self._table.item(
            row,
            1,
        )

        if tax_number_item is None:
            return

        supplier = (
            self._supplier_service.get_by_tax_number(
                tax_number_item.text()
            )
        )

        if supplier is None:
            return

        self._show_supplier_details(
            supplier
        )

    def _show_supplier_details(
        self,
        supplier: Supplier,
    ) -> None:
        QMessageBox.information(
            self,
            "Beszállító adatai",
            (
                f"Név: {supplier.name}\n"
                f"Adószám: {supplier.tax_number}\n"
                f"Ország: {supplier.country or '-'}\n"
                f"Company key: {supplier.company_key}"
            ),
        )

    def _update_button_state(self) -> None:
        has_selection = bool(
            self._table.selectionModel().selectedRows()
        )

        self._open_button.setEnabled(
            has_selection
        )

    def refresh(self) -> None:
        self._refresh_table()
        self._refresh_relations_table()

    def _refresh_table(self) -> None:
        self._table.setRowCount(0)

        for supplier in (
                self._supplier_service.list_suppliers()
        ):
            self._add_supplier_to_table(
                supplier
            )

        self._filter_suppliers(
            self._search_input.text()
        )

    def _add_supplier_to_table(
        self,
        supplier: Supplier,
    ) -> None:
        row = self._table.rowCount()

        self._table.insertRow(row)

        self._table.setItem(
            row,
            0,
            QTableWidgetItem(supplier.name),
        )

        self._table.setItem(
            row,
            1,
            QTableWidgetItem(supplier.tax_number),
        )

        self._table.setItem(
            row,
            2,
            QTableWidgetItem(supplier.country or ""),
        )

    def _filter_suppliers(
        self,
        text: str,
    ) -> None:
        search_text = text.strip().lower()

        for row in range(
            self._table.rowCount()
        ):
            name_item = self._table.item(
                row,
                0,
            )

            tax_number_item = self._table.item(
                row,
                1,
            )

            name = (
                name_item.text().lower()
                if name_item
                else ""
            )

            tax_number = (
                tax_number_item.text().lower()
                if tax_number_item
                else ""
            )

            matches = (
                search_text in name
                or search_text in tax_number
            )

            self._table.setRowHidden(
                row,
                not matches,
            )

    def _setup_relations_table(self) -> None:
        self._relations_table.setColumnCount(3)

        self._relations_table.setHorizontalHeaderLabels(
            [
                "Cég / kötelezett",
                "Beszállító",
                "Létrehozva",
            ]
        )

        header = self._relations_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self._relations_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self._relations_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )