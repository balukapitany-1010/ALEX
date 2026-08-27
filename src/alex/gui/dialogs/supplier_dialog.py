from PySide6.QtWidgets import QWidget

from alex.esg.domain.supplier import Supplier
from alex.gui.dialogs.company_dialog import CompanyDialog


class SupplierDialog(CompanyDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        supplier: Supplier | None = None,
    ) -> None:
        super().__init__(
            parent=parent,
            company=supplier,
        )

        if supplier is None:
            self.setWindowTitle("Új beszállító")
        else:
            self.setWindowTitle("Beszállító szerkesztése")