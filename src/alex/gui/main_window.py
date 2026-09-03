from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from alex.esg.repositories.mssql_supplier_repository import MssqlSupplierRepository
from alex.esg.repositories.mssql_supply_chain_relation_repository import MssqlSupplyChainRelationRepository
from alex.esg.repositories.mssql_company_repository import MssqlCompanyRepository
from alex.infrastructure.database.sql_server_config import SqlServerConfig
from alex.infrastructure.database.sql_server_connection_factory import SqlServerConnectionFactory
from alex.esg.services.attachment_service import AttachmentService
from alex.gui.views.attachments_view import AttachmentsView
from alex.esg.services.questionnaire_definition_file_import_service import QuestionnaireDefinitionFileImportService
from alex.esg.mappers.questionnaire_definition_mapper import QuestionnaireDefinitionMapper
from alex.esg.mappers.submission_header_mapper import SubmissionHeaderMapper
from alex.esg.services.question_definition_service import  QuestionDefinitionService
from alex.esg.services.company_service import CompanyService
from alex.esg.services.json_import_service import  JsonImportService
from alex.esg.services.questionnaire_service import QuestionnaireService
from alex.esg.services.submission_batch_importer import  SubmissionBatchImporter
from alex.esg.services.submission_batch_json_importer import  SubmissionBatchJsonImporter
from alex.esg.services.submission_batch_registration_service import  SubmissionBatchRegistrationService
from alex.esg.services.submission_builder_service import  SubmissionBuilderService
from alex.esg.services.submission_definition_validator import SubmissionDefinitionValidator
from alex.esg.services.submission_file_import_service import  SubmissionFileImportService
from alex.esg.services.submission_import_preview_service import  SubmissionImportPreviewService
from alex.esg.services.submission_import_service import  SubmissionImportService
from alex.esg.services.submission_json_importer import  SubmissionJsonImporter
from alex.esg.services.submission_party_resolver import  SubmissionPartyResolver
from alex.esg.services.submission_relation_resolver import SubmissionRelationResolver
from alex.esg.services.submission_service import SubmissionService
from alex.esg.services.submission_submitter_resolver import SubmissionSubmitterResolver
from alex.esg.services.supplier_service import SupplierService
from alex.esg.services.supply_chain_relation_service import SupplyChainRelationService
from alex.gui.views.questionnaires_view import QuestionnairesView
from alex.gui.views.companies_views import CompaniesView
from alex.gui.views.submissions_view import SubmissionsView
from alex.gui.views.suppliers_view import SuppliersView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        db_config = (SqlServerConfig.from_environment())

        db_connection_factory = (SqlServerConnectionFactory(db_config))

        company_repository = (MssqlCompanyRepository(db_connection_factory))

        self._company_service = (CompanyService(repository=company_repository))

        self._attachment_service = (AttachmentService())

        self._supplier_service = (SupplierService())
        self._relation_service = (SupplyChainRelationService())
        supplier_repository = (MssqlSupplierRepository(db_connection_factory))
        relation_repository = (MssqlSupplyChainRelationRepository(db_connection_factory))
        self._supplier_db_service = (SupplierService(repository=supplier_repository))
        self._relation_db_service = (SupplyChainRelationService(repository=relation_repository))
        self._submission_service = (SubmissionService())
        self._questionnaire_service = (QuestionnaireService())
        self._question_definition_service = (QuestionDefinitionService())

        self._setup_import_services()

        self.setWindowTitle("ALEX")
        self.resize(1200, 750)

        self._navigation = QListWidget()
        self._content = QStackedWidget()

        self._setup_navigation()
        self._setup_content()
        self._setup_layout()
        self._connect_signals()

    def _setup_import_services(
        self,
    ) -> None:
        json_service = JsonImportService()

        definition_mapper = (QuestionnaireDefinitionMapper())

        batch_inspector = (SubmissionBatchImporter())

        definition_validator = (SubmissionDefinitionValidator())

        party_resolver = (SubmissionPartyResolver(company_service=(self._company_service),
                supplier_service=(self._supplier_service),))

        relation_resolver = (SubmissionRelationResolver(relation_service=(self._relation_service),))

        submitter_resolver = (SubmissionSubmitterResolver(company_service=(self._company_service),))

        submission_builder = ( SubmissionBuilderService(
                party_resolver=(party_resolver),
                relation_resolver=(relation_resolver),
                submitter_resolver=(submitter_resolver),
            )
        )

        submission_import_service = (SubmissionImportService())

        single_submission_importer = (SubmissionJsonImporter(
                header_mapper=(SubmissionHeaderMapper()),
                builder=(submission_builder),
                submission_import_service=(submission_import_service),
            )
        )

        batch_json_importer = ( SubmissionBatchJsonImporter(
                batch_inspector=(batch_inspector),
                definition_validator=(definition_validator),
                submission_importer=(single_submission_importer),
            )
        )

        registration_service = (SubmissionBatchRegistrationService(submission_service=(self._submission_service),))

        self._submission_file_import_service = (
            SubmissionFileImportService(
                json_service=json_service,
                definition_mapper=definition_mapper,
                batch_importer=batch_json_importer,
                registration_service=registration_service,
                questionnaire_service=(self._questionnaire_service),
                question_definition_service=(self._question_definition_service),
            )
        )

        self._submission_import_preview_service = (
            SubmissionImportPreviewService(
                json_service=json_service,
                definition_mapper=definition_mapper,
                batch_inspector=batch_inspector,
                definition_validator=(definition_validator),
                questionnaire_service=(self._questionnaire_service),
            )
        )
        self._questionnaire_definition_file_import_service = (
            QuestionnaireDefinitionFileImportService(
                json_service=json_service,
                definition_mapper=definition_mapper,
                questionnaire_service=(self._questionnaire_service),
                question_definition_service=(self._question_definition_service),
            )
        )


    def _setup_navigation(
        self,
    ) -> None:
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

    def _setup_content(
            self,
    ) -> None:
        self._companies_view = CompaniesView(company_service=(self._company_service),)

        self._content.addWidget(self._companies_view)

        self._suppliers_view = SuppliersView(
            supplier_service=(
                self._supplier_db_service
            ),
            company_service=(
                self._company_service
            ),
            relation_service=(
                self._relation_db_service
            ),
            read_only=True,
        )

        self._content.addWidget(self._suppliers_view)

        self._submissions_view = SubmissionsView(
            submission_service=(self._submission_service),
            relation_service=(self._relation_service),
            questionnaire_service=(self._questionnaire_service),
            file_import_service=(self._submission_file_import_service),
            preview_service=(self._submission_import_preview_service),
        )

        self._content.addWidget(self._submissions_view)

        self._questionnaires_view = QuestionnairesView(
            questionnaire_service=(self._questionnaire_service),
            question_definition_service=(self._question_definition_service),
            definition_file_import_service=(self._questionnaire_definition_file_import_service),
        )

        self._content.addWidget(self._questionnaires_view)

        self._attachments_view = AttachmentsView(
            submission_service=(self._submission_service),
            attachment_service=(self._attachment_service),
            question_definition_service=(self._question_definition_service),
        )

        self._content.addWidget(self._attachments_view)
        self._content.addWidget(self._create_placeholder_page("Riportok"))
        self._content.addWidget(self._create_placeholder_page("Adatbázis"))

    def _setup_layout(
        self,
    ) -> None:
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.addWidget(self._navigation)
        layout.addWidget(self._content, 1,)
        self.setCentralWidget(central_widget)

    def _connect_signals(self) -> None:
        self._navigation.currentRowChanged.connect(
            self._content.setCurrentIndex
        )
        self._navigation.currentRowChanged.connect(self._refresh_current_page)

    def _refresh_current_page(
            self,
            index: int,
    ) -> None:
        if index == 0:
            self._companies_view.refresh()

        elif index == 1:
            self._suppliers_view.refresh()

        elif index == 2:
            self._submissions_view.refresh()

        elif index == 3:
            self._questionnaires_view.refresh()

        elif index == 4:
            self._attachments_view.refresh()

    @staticmethod
    def _create_placeholder_page(
        title: str,
    ) -> QWidget:
        page = QWidget()

        layout = QVBoxLayout(page)

        title_label = QLabel(title)

        font = title_label.font()
        font.setPointSize(20)
        font.setBold(True )

        title_label.setFont(font)

        layout.addWidget(title_label)

        layout.addStretch()

        return page