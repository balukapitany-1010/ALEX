from alex.gui.views.companies_views import CompaniesView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("ALEX")
        self.resize(1200, 750)

        self._navigation = QListWidget()
        self._content = QStackedWidget()

        self._setup_navigation()
        self._setup_content()
        self._setup_layout()
        self._connect_signals()

    def _setup_navigation(self) -> None:
        self._navigation.addItems(
            [
                "Cégek",
                "Beszállítók",
                "Beküldések",
                "Kérdőívek",
                "Dokumentumok",
                "Riportok",
                "Adatbázis",
            ]
        )

        self._navigation.setFixedWidth(200)
        self._navigation.setCurrentRow(0)

    def _setup_content(self) -> None:
        self._content.addWidget(
            CompaniesView()
        )
        self._content.addWidget(
            self._create_placeholder_page("Beszállítók")
        )
        self._content.addWidget(
            self._create_placeholder_page("Beküldések")
        )
        self._content.addWidget(
            self._create_placeholder_page("Kérdőívek")
        )
        self._content.addWidget(
            self._create_placeholder_page("Dokumentumok")
        )
        self._content.addWidget(
            self._create_placeholder_page("Riportok")
        )
        self._content.addWidget(
            self._create_placeholder_page("Adatbázis")
        )

    def _setup_layout(self) -> None:
        central_widget = QWidget()

        layout = QHBoxLayout(central_widget)

        layout.addWidget(self._navigation)
        layout.addWidget(self._content, 1)

        self.setCentralWidget(central_widget)

    def _connect_signals(self) -> None:
        self._navigation.currentRowChanged.connect(
            self._content.setCurrentIndex
        )

    @staticmethod
    def _create_placeholder_page(title: str) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)

        title_label = QLabel(title)

        font = title_label.font()
        font.setPointSize(20)
        font.setBold(True)

        title_label.setFont(font)

        layout.addWidget(title_label)
        layout.addStretch()

        return page