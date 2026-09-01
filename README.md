# ALEX

**ALEX** egy Python alapú desktop alkalmazás az ESG kérdőívek, vállalatok, beszállítók, beküldések és kapcsolódó dokumentumok kezelésére.

A projekt célja egy jól tesztelhető, rétegekre bontott alkalmazás kialakítása, amely képes az SZTFH ESG kérdőív-definíciók és beküldések feldolgozására, validálására, megjelenítésére és később adatbázisban történő tárolására.

## Fő technológiák

* Python 3.13
* PySide6
* pytest
* Objektumorientált domain modell
* Service réteg
* Mapper réteg
* JSON import
* Desktop GUI

## Projektstruktúra

```text
ALEX/
├── src/
│   └── alex/
│       ├── main.py
│       ├── esg/
│       │   ├── domain/
│       │   ├── mappers/
│       │   └── services/
│       └── gui/
│           ├── dialogs/
│           └── views/
├── tests/
├── pyproject.toml
└── README.md
```

A projekt `src` layoutot használ.

---

# Architektúra

Az alkalmazás több, egymástól elkülönített rétegre épül.

```text
GUI
 │
 ▼
Services
 │
 ├────────► Mappers
 │
 ▼
Domain
 │
 ▼
Storage / Database
```

A cél, hogy a GUI ne tartalmazza közvetlenül az üzleti logikát.

## Domain réteg

A domain réteg tartalmazza az ESG rendszer alapvető üzleti objektumait.

### Company

Egy vállalatot reprezentál.

Főbb mezők:

* `company_key`
* `name`
* `tax_number`
* `country`
* `created_at`
* `updated_at`

A `tax_number` kötelező, és a vállalat létrehozása után nem módosítható.

### Supplier

A `Company` specializációja.

A beszállító továbbra is vállalat, ezért a különálló, duplikált cégmodell helyett öröklést használunk.

### SupplyChainRelation

Két vállalat közötti beszállítói kapcsolatot reprezentál.

```text
requester ─────► supplier
```

Főbb kapcsolatok:

* requester vállalat
* supplier vállalat

A kapcsolat nem tartalmazza a kérdőív vonatkozási időszakát. Az időszak a `Submission` objektumhoz tartozik.

### Questionnaire

Egy kérdőívverziót reprezentál.

Főbb mezők:

* `questionnaire_code`
* `spec_version`
* `locale`

### Question

A kérdés alapazonosítóit tartalmazza.

Főbb mezők:

* `question_id`
* `question_code`

### QuestionDefinition

A kérdés adott kérdőívverzióban érvényes definícióját tartalmazza.

Többek között:

* kérdés
* kérdőív
* cím
* ESG kategória
* subject
* organization
* organization sizes
* geographical relevance
* topic
* question type
* választható opciók

### QuestionType

Jelenleg támogatott kérdéstípusok:

```text
RADIO
CHECKBOX
DROPDOWN
TEXT
COMMENT
NUMBER
MIXED
TABLE
```

### Option

Egy kérdés választható opcióját reprezentálja.

Főbb mezők:

* `option_id`
* `label`

### Submission

Egy konkrét ESG kérdőívbeküldést reprezentál.

Főbb adatok:

* `submission_id`
* beszállítói kapcsolat
* kérdőív
* `period`
* státusz
* beküldési idő
* válaszok
* csatolmányok

A vonatkozási időszak (`period`) a beküldés tulajdonsága.

### Answer

Egy kérdéshez tartozó választ reprezentál.

Támogatott értékek:

* kiválasztott opciók
* szöveges érték
* numerikus érték

A megengedett értékeket a kérdés típusa határozza meg.

Például:

```text
RADIO
  └── pontosan legfeljebb egy Option

CHECKBOX
  └── több Option

TEXT
  └── text_value

NUMBER
  └── number_value

MIXED
  ├── Option
  ├── text_value
  └── number_value
```

Az `Answer` validálja azt is, hogy a kiválasztott opció valóban az adott kérdéshez tartozik-e.

### Attachment

Beküldéshez vagy konkrét kérdéshez kapcsolódó dokumentumot reprezentál.

A tárolási helyet általános:

```text
storage_reference
```

azonosító reprezentálja.

Ez lehetővé teszi, hogy később a dokumentum:

* fájlrendszerben,
* adatbázisban,
* fájlszerveren,
* object storage-ban

is tárolható legyen anélkül, hogy a domain modellt módosítani kellene.

---

# Service réteg

Az üzleti műveleteket service objektumok kezelik.

Jelenlegi főbb service-ek:

* `CompanyService`
* `SupplierService`
* `SupplyChainRelationService`
* `SubmissionService`
* `QuestionnaireService`

Az importfolyamathoz külön service-ek tartoznak, többek között:

* `JsonImportService`
* `SubmissionImportService`
* `SubmissionFileImportService`
* `SubmissionImportPreviewService`
* `SubmissionBuilderService`
* `SubmissionDefinitionValidator`
* `SubmissionBatchImporter`
* `SubmissionBatchJsonImporter`
* `SubmissionBatchRegistrationService`

A GUI ezeket dependency injection segítségével kapja meg.

---

# Mapper réteg

A mapper réteg feladata a külső reprezentációk és a domain objektumok közötti átalakítás.

Fontosabb mapper-ek:

* `QuestionnaireDefinitionMapper`
* `SubmissionHeaderMapper`

A `QuestionnaireDefinitionMapper` az SZTFH kérdőív JSON definícióját alakítja domain objektumokká.

---

# JSON import

Az alkalmazás célja az SZTFH ESG JSON formátumok feldolgozása.

Az importfolyamat főbb lépései:

```text
JSON fájl
   │
   ▼
JsonImportService
   │
   ▼
Submission import / preview
   │
   ▼
Definition validation
   │
   ▼
Mapper
   │
   ▼
Domain objektumok
   │
   ▼
Submission
```

Az importálás során többek között ellenőrizhető:

* JSON formátum
* kérdőívverzió
* kérdésazonosítók
* kérdésdefiníciók
* válaszok
* opcióazonosítók
* beküldési fejléc
* beszállító és requester adatok

---

# Grafikus felület

A desktop GUI PySide6 használatával készül.

A főablak bal oldali navigációt és jobb oldali tartalomterületet használ.

Jelenlegi fő nézetek:

```text
Cégek
Beszállítók
Beküldések
Kérdőívek
Dokumentumok
Riportok
Adatbázis
```

A főablak a nézeteket `QStackedWidget` segítségével kezeli.

## Cégek

A `CompaniesView` támogatja többek között:

* cégek listázását
* keresést
* új cég létrehozását
* meglévő cég megnyitását
* szerkesztést

## Beszállítók

A `SuppliersView` a beszállítók kezelésére szolgál.

## Beküldések

A `SubmissionsView` kezeli a kérdőívbeküldéseket.

A fejlesztés alatt álló funkciók között szerepel:

* beküldések listázása
* keresés
* tesztbeküldés létrehozása
* JSON import
* import előnézet
* validálás

## Kérdőívek

A `QuestionnaireView` a kérdőívdefiníciók megjelenítésére szolgál.

## Dokumentumok

Az `AttachmentsView` a beküldésekhez és kérdésekhez tartozó dokumentumok kezelését készíti elő.

---

# Fejlesztői környezet

## Repository klónozása

```powershell
git clone <repository-url>
cd ALEX
```

## Virtuális környezet létrehozása

Windows PowerShell:

```powershell
python -m venv .venv
```

Aktiválás:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Projekt telepítése

```powershell
python -m pip install --upgrade pip
pip install -e .
```

Ha a fejlesztői függőségek külön extra-ként vannak definiálva:

```powershell
pip install -e ".[dev]"
```

---

# Alkalmazás indítása

A projekt gyökérkönyvtárából:

```powershell
python -m alex.main
```

---

# Tesztek

A teljes tesztkészlet futtatása:

```powershell
python -m pytest
```

Részletes kimenettel:

```powershell
python -m pytest -v
```

Egy konkrét tesztfájl:

```powershell
python -m pytest tests/test_answer.py -v
```

Egy konkrét teszt:

```powershell
python -m pytest tests/test_answer.py::test_name -v
```

A projekt fejlesztése során minden új domain szabályhoz lehetőség szerint külön unit teszt készül.

---

# Fejlesztési elvek

## Domain-first

Az üzleti szabályokat elsődlegesen a domain objektumokban vagy a service rétegben implementáljuk.

Nem a GUI felelőssége például annak eldöntése, hogy:

* egy válasz érvényes-e;
* egy kérdéshez megengedett-e egy adott opció;
* egy vállalat adatai megfelelőek-e;
* egy beküldés megfelel-e a kérdőív definíciójának.

## Dependency Injection

A GUI nézetek nem hozzák létre saját service példányaikat.

A szükséges service-eket konstruktoron keresztül kapják meg.

Példa:

```python
view = SubmissionsView(
    submission_service=submission_service,
    relation_service=relation_service,
    questionnaire_service=questionnaire_service,
)
```

Ez csökkenti a rétegek közötti függőséget és egyszerűbbé teszi a tesztelést.

## Validáció

A hibás állapot lehetőség szerint már az objektum létrehozásakor vagy módosításakor legyen elutasítva.

Például:

```python
Answer(...)
```

nem hozható létre olyan kiválasztott opcióval, amely nem tartozik az adott kérdéshez.

## Tesztvezérelt fejlesztés

Az új funkciókhoz és hibajavításokhoz automatikus teszteket használunk.

Általános munkafolyamat:

```text
domain szabály
      │
      ▼
pytest teszt
      │
      ▼
implementáció
      │
      ▼
service
      │
      ▼
GUI integráció
```

---

# Aktuális fejlesztési területek

A projekt jelenleg aktív fejlesztés alatt áll.

A következő főbb területeken folyik munka:

* JSON importfolyamat stabilizálása
* import előnézet
* kérdőív-definíciók teljes körű feldolgozása
* valós SZTFH JSON fájlok kezelése
* GUI és service réteg további szétválasztása
* beküldések kezelése
* csatolmánykezelés
* adatbázis persistence réteg
* riportok
* integrációs tesztek

---

# Ismert adatminőségi esetek

A valós kérdőívdefiníciók feldolgozásánál előfordulhatnak olyan forrásadatok, amelyek technikailag eltérnek a szigorú domain validációtól.

Ilyen például az üres option label.

Ezeket nem a domain szabályok fellazításával, hanem az import-/mapper rétegben szükséges megfelelően kezelni.

---

# Git munkafolyamat

Módosítások ellenőrzése:

```powershell
git status
git diff
```

Fájlok hozzáadása:

```powershell
git add src tests README.md
```

Commit:

```powershell
git commit -m "Update project documentation"
```

Push:

```powershell
git push origin main
```

---

# Projekt státusz

**Státusz:** aktív fejlesztés

Jelenlegi fókusz:

```text
Domain modell
     ↓
Service réteg
     ↓
JSON import
     ↓
Validáció
     ↓
PySide6 GUI
     ↓
Persistence / MSSQL
```

A hosszú távú cél egy olyan desktop alkalmazás létrehozása, amely az ESG kérdőívek teljes életciklusát képes kezelni a beérkező JSON fájltól a validált, kereshető és riportálható adatokig.





# Adatbázis

Az ALEX adatbázisának feladata az ESG kérdőívekhez kapcsolódó teljes üzleti adatkör tartós tárolása.

A tervezett és részben már korábban használt adatbázis-platform:

```text
Microsoft SQL Server
```

Az adatmodell célja, hogy elkülönítse egymástól:

* a vállalatokat;
* a vállalatok közötti beszállítói kapcsolatokat;
* a kérdőív-definíciókat;
* a konkrét kérdőívbeküldéseket;
* a válaszokat;
* a dokumentumokat;
* az importfolyamat naplózását;
* a validációs eredményeket;
* az audit információkat.

Az adatbázis szerkezete a Python domain modellhez igazodik, de a domain objektumok és az SQL táblák között nem szükséges minden esetben 1:1 megfeleltetés.

---

## Adatmodell áttekintése

A fő entitások közötti kapcsolat:

```text
COMPANY
   │
   ├──────────────┐
   │              │
   ▼              ▼
requester       supplier
   │              │
   └──────┬───────┘
          │
          ▼
SUPPLY_CHAIN_RELATION
          │
          ▼
SUBMISSION_BATCH
          │
          ▼
SUBMISSION
          │
          ├──────────────► ATTACHMENT
          │
          ▼
ANSWER_VALUE
          │
          ▼
QUESTION
          │
          ▼
QUESTIONNAIRE
```

A modell egyik fontos alapelve, hogy egy vállalat csak egyszer szerepeljen a `COMPANY` táblában.

Ha ugyanaz a beszállító több kötelezett vállalatnak is beszállítója, akkor nem új `COMPANY` rekord jön létre, hanem több `SUPPLY_CHAIN_RELATION` rekord kapcsolja össze a vállalatokat.

---

# COMPANY

A `COMPANY` tábla tartalmazza a rendszerben ismert vállalatokat.

Tervezett fő mezők:

```text
company_key
name
tax_number
country
created_at
updated_at
```

## company_key

A vállalat belső technikai azonosítója.

A `company_key` elsődleges kulcsként használható.

Nem szükséges, hogy üzleti jelentése legyen.

Például:

```text
COMPANY
--------------------------------------------
company_key     96DD7F...
name            Példa Kft.
tax_number      12345678-2-41
country         HU
```

## tax_number

A vállalat adószáma.

Ez az egyik legfontosabb üzleti azonosító.

A rendszer célja, hogy ugyanaz a vállalat ne jöhessen létre többször ugyanazzal az adószámmal.

Ezért az adatbázisban egyedi index vagy constraint használható:

```sql
UNIQUE (tax_number)
```

A Python domain modellben a `tax_number` kötelező adat, és a létrehozás után nem módosítható.

## name

A vállalat neve.

A név önmagában nem használható egyedi azonosítóként, mivel:

* a cégnév változhat;
* előfordulhatnak hasonló cégnevek;
* eltérő írásmódok lehetnek;
* ugyanaz a vállalat több forrásban eltérő névformátumban szerepelhet.

Az elsődleges üzleti azonosítás ezért az adószámra épül.

## country

A vállalat országa.

Opcionális adat.

## created_at / updated_at

Technikai időbélyegek.

```text
created_at
```

a rekord létrejöttének ideje.

```text
updated_at
```

az utolsó módosítás ideje.

---

# COMPANY_CONTACT

A vállalathoz kapcsolódó kapcsolattartók külön táblában tárolhatók.

Fő mezők:

```text
contact_id
company_key
name
email
phone
role
```

Kapcsolat:

```text
COMPANY
   │
   │ 1
   │
   └──────────── *
             COMPANY_CONTACT
```

Egy vállalathoz több kapcsolattartó tartozhat.

Például:

```text
Company
 ├── ESG kapcsolattartó
 ├── pénzügyi kapcsolattartó
 └── adminisztratív kapcsolattartó
```

A `company_key` idegen kulcs a `COMPANY` táblára.

---

# SUPPLY_CHAIN_RELATION

A `SUPPLY_CHAIN_RELATION` tábla írja le két vállalat beszállítói kapcsolatát.

Fő mezők:

```text
relation_id
requester_company_key
supplier_company_key
relation_status
created_at
updated_at
```

A kapcsolat irányított.

```text
requester
    │
    ▼
supplier
```

Példa:

```text
Nagyvállalat Zrt.
        │
        │ beszállítói kapcsolat
        ▼
Alkatrész Kft.
```

Adatbázisban:

```text
requester_company_key = Nagyvállalat Zrt.
supplier_company_key  = Alkatrész Kft.
```

Mindkét mező a `COMPANY.company_key` mezőre mutat.

---

## Miért külön tábla?

A beszállítói kapcsolat nem a `COMPANY` attribútuma.

Ugyanaz a vállalat például lehet egyszerre több vállalat beszállítója:

```text
              ┌──► Nagyvállalat A
Beszállító Kft.
              ├──► Nagyvállalat B
              │
              └──► Nagyvállalat C
```

Ezért a kapcsolat külön entitás.

Adatbázisban:

```text
requester | supplier
----------+----------------
A         | Beszállító Kft.
B         | Beszállító Kft.
C         | Beszállító Kft.
```

A beszállító ettől továbbra is csak egyszer szerepel a `COMPANY` táblában.

---

# QUESTIONNAIRE

A `QUESTIONNAIRE` tábla tartalmazza a rendszer által ismert kérdőívverziókat.

Fő mezők:

```text
questionnaire_code
spec_version
locale
created_at
```

Példa:

```text
questionnaire_code = SZTFH_ESG
spec_version       = 2.1
locale             = hu-HU
```

A rendszernek több kérdőívverzió egyidejű kezelésére kell képesnek lennie.

Például:

```text
1.1
1.2
2.0
2.1
2.2
```

Ez azért fontos, mert a korábbi beküldéseknek a beküldés időpontjában érvényes definíció alapján továbbra is értelmezhetőnek kell maradniuk.

---

# QUESTION

A `QUESTION` tábla tartalmazza az ESG kérdőívek kérdéseit.

Fő mezők:

```text
question_id
questionnaire_code
spec_version
requirement
topic
subtopic
title
category
type
question_code
visible_if
status
```

## question_id

A kérdés technikai vagy specifikáció szerinti egyedi azonosítója.

Ez biztosítja, hogy a válasz egyértelműen összekapcsolható legyen az adott kérdéssel.

## question_code

Ember számára könnyebben értelmezhető kérdéskód.

Például:

```text
E1
E6
S12
G4
```

## category

Az ESG kategória.

Lehetséges értékek például:

```text
E
S
G
```

ahol:

```text
E = Environmental
S = Social
G = Governance
```

## type

A kérdés válaszmezőjének típusa.

A Python domain modell jelenleg az alábbi típusokat támogatja:

```text
RADIO
CHECKBOX
DROPDOWN
TEXT
COMMENT
NUMBER
MIXED
TABLE
```

## visible_if

Feltételes megjelenítési szabály.

Segítségével olyan kérdések modellezhetők, amelyek csak egy korábbi válasz függvényében jelennek meg.

---

# SUBMISSION_BATCH

A `SUBMISSION_BATCH` egy importálási vagy beküldési csoportot reprezentál.

Fő mezők:

```text
batch_id
questionnaire_code
created_at
```

Egy batch több submissiont tartalmazhat.

```text
SUBMISSION_BATCH
       │
       ├── Submission 1
       ├── Submission 2
       ├── Submission 3
       └── Submission N
```

Ez különösen fontos olyan JSON fájlok esetén, amelyek egyetlen fájlban több beszállító kérdőívbeküldését tartalmazzák.

---

# SUBMISSION

A `SUBMISSION` tábla egy konkrét kérdőívbeküldést reprezentál.

Fő mezők:

```text
submission_id
batch_id
relation_id
supplier_key
respondent_id
respondent_mp_id
org_size
submitted_at
status
raw_payload
created_at
updated_at
```

A Python domain modellben ehhez kapcsolódik a kérdőív vonatkozási időszaka is:

```text
period
```

Például:

```text
2026-Q1
2026-Q2
```

---

## submission_id

A beküldés egyedi technikai azonosítója.

Egy adott kérdőívbeküldés minden válasza ezen keresztül kapcsolódik a submissionhöz.

---

## batch_id

Idegen kulcs:

```text
SUBMISSION_BATCH.batch_id
```

Megmutatja, hogy a beküldés mely importálási batch része volt.

---

## relation_id

Idegen kulcs:

```text
SUPPLY_CHAIN_RELATION.relation_id
```

Ez határozza meg:

* ki a requester;
* ki a supplier.

Így a `SUBMISSION` rekordnak nem szükséges külön tárolnia mindkét vállalat teljes adatát.

---

## supplier_key

A beszállító közvetlen technikai referenciája.

A végleges adatmodellben érdemes eldönteni, hogy szükséges-e egyszerre tárolni:

```text
relation_id
```

és

```text
supplier_key
```

mivel a supplier a relationből is meghatározható.

A redundancia csak akkor indokolt, ha teljesítmény, történeti adatok vagy importálási kompatibilitás miatt szükséges.

---

## respondent_id

A beküldőhöz tartozó forrásoldali azonosító.

---

## respondent_mp_id

A Management Platformhoz vagy más külső rendszerhez kapcsolódó azonosító.

---

## org_size

A kérdőívet kitöltő szervezet méretkategóriája.

---

## submitted_at

A kérdőív tényleges beküldési ideje.

Ez különbözik a rekord adatbázisba történő bekerülésének időpontjától.

Például:

```text
submitted_at = 2026-08-04 08:46
created_at   = 2026-08-06 12:28
```

---

## status

A beküldés aktuális állapotát tárolja.

A Python oldalon ezt `SubmissionStatus` reprezentálja.

Az állapotkezelést célszerű egyszerűen tartani, és csak valóban szükséges üzleti státuszokat létrehozni.

---

## raw_payload

Az eredeti JSON payload eltárolható audit és hibakeresési célból.

Ez lehetővé teszi, hogy később vissza lehessen nézni:

* pontosan milyen adat érkezett;
* milyen kérdőívverzióból;
* milyen mezőkkel;
* milyen importhiba történt.

A `raw_payload` nem helyettesíti a normalizált adatmodellt.

A normál lekérdezéseknek továbbra is a strukturált táblákból kell működniük.

---

# ANSWER_VALUE

Az `ANSWER_VALUE` tábla tartalmazza a kérdőív konkrét válaszait.

Fő mezők:

```text
answer_id
submission_id
question_id
field_type
number_value
text_value
selected
created_at
```

Kapcsolatok:

```text
SUBMISSION
    │
    │ 1
    │
    └──────────── *
              ANSWER_VALUE
                    │
                    ▼
                 QUESTION
```

Egy submission több választ tartalmaz.

Egy válasz pedig egy adott kérdéshez tartozik.

---

## Miért több értékmező?

Az ESG kérdések különböző típusú válaszokat tartalmazhatnak.

Például:

```text
TEXT
NUMBER
RADIO
CHECKBOX
MIXED
```

Ezért külön mezők állnak rendelkezésre.

### Szöveges válasz

```text
text_value
```

Példa:

```text
"A vállalat rendelkezik környezetirányítási rendszerrel."
```

### Numerikus válasz

```text
number_value
```

Példa:

```text
1532.75
```

### Kiválasztott érték

```text
selected
```

Használható választási típusú válaszoknál.

A végleges persistence modellben a többértékű checkbox és mixed típusokhoz külön answer option kapcsolótábla kialakítása is indokolt lehet.

Például:

```text
ANSWER
  │
  └── ANSWER_SELECTED_OPTION
          ├── OPTION A
          ├── OPTION B
          └── OPTION C
```

Ez normalizáltabb megoldás, mint több option egyetlen mezőbe történő tárolása.

---

# ATTACHMENT

Az `ATTACHMENT` tábla a kérdőívhez kapcsolódó dokumentumokat kezeli.

Egy dokumentum tartozhat:

* teljes submissionhöz;
* konkrét kérdéshez.

Tervezett logikai mezők:

```text
attachment_id
submission_id
question_id
file_name
content_type
storage_reference
created_at
```

A `question_id` opcionális.

Ha nincs megadva:

```text
Submission
   └── Attachment
```

Ha meg van adva:

```text
Submission
   └── Question
          └── Attachment
```

---

## storage_reference

Az ALEX domain modell nem akarja kikényszeríteni, hogy a fájl fizikailag hol legyen tárolva.

Ezért általános:

```text
storage_reference
```

mezőt használ.

Ez hivatkozhat például:

```text
helyi fájlra
hálózati megosztásra
adatbázis blob rekordra
object storage objektumra
dokumentumkezelő rendszerre
```

Például:

```text
file://attachments/2026/abc.pdf
```

vagy:

```text
s3://alex-esg/attachments/abc.pdf
```

vagy:

```text
db://attachments/73F...
```

A domain modell így nem függ az infrastruktúrától.

---

# IFORM_605

Az ESG adatfeldolgozás során az IFORM 605 adatok külön táblában kezelhetők.

Főbb mezők:

```text
iform_605_id
batch_id
form_identifier
form_version
form_last_modified
```

Példa:

```text
form_identifier = SZTFH 605
```

A kapcsolat:

```text
SUBMISSION_BATCH
      │
      └────────── IFORM_605
```

Ez lehetővé teszi, hogy egy adott importbatchhez az eredeti kísérő IFORM adat is hozzárendelhető legyen.

A modell később további formátumokkal, például `IFORM_606` támogatással is bővíthető.

---

# IMPORT_LOG

Az `IMPORT_LOG` tábla az importálási folyamat technikai naplózására szolgál.

Segítségével nyomon követhető például:

```text
melyik fájl került importálásra
mikor történt az import
sikeres volt-e
hány submission került feldolgozásra
milyen hiba történt
```

Lehetséges mezők:

```text
import_log_id
batch_id
file_name
started_at
finished_at
status
message
created_at
```

Például:

```text
SUCCESS
VALIDATION_ERROR
DUPLICATE
FAILED
USER_CANCELLED
```

A technikai importstátusz nem feltétlenül azonos a `SUBMISSION.status` üzleti státuszával.

---

# VALIDATION_RESULT

A `VALIDATION_RESULT` tábla tárolhatja az importálás és kérdőívfeldolgozás során keletkezett validációs eredményeket.

Például:

```text
validation_result_id
submission_id
question_id
validation_code
severity
message
created_at
```

Lehetséges severity:

```text
INFO
WARNING
ERROR
```

Példa:

```text
submission_id: abc...
question_id: E20b
severity: ERROR
message: Selected option does not belong to question.
```

Ez különösen hasznos import preview esetén.

Az alkalmazás így még az adat végleges mentése előtt képes megmutatni a problémákat.

---

# AUDIT_LOG

Az `AUDIT_LOG` a fontos adatváltozások történetének tárolására szolgálhat.

Tipikus események:

```text
Company létrehozása
Company módosítása
Submission importálása
Submission törlése
Attachment hozzáadása
Attachment törlése
Import megismétlése
```

Lehetséges mezők:

```text
audit_id
entity_type
entity_id
action
old_value
new_value
user_identifier
created_at
```

Az audit log különösen fontos akkor, ha az alkalmazás később többfelhasználós vagy hatósági környezetben működik.

---

# Fő kapcsolatok

Az egyszerűsített relációs modell:

```text
COMPANY
 ├──< COMPANY_CONTACT
 │
 ├──< SUPPLY_CHAIN_RELATION >── COMPANY
 │
 │
 └──── requester             supplier
              │
              ▼
          SUBMISSION
              │
              ├──< ANSWER_VALUE >── QUESTION
              │
              └──< ATTACHMENT
```

A kérdőív oldal:

```text
QUESTIONNAIRE
      │
      └──< QUESTION
              │
              └──< ANSWER_VALUE
```

Batch oldal:

```text
SUBMISSION_BATCH
      │
      ├──< SUBMISSION
      │
      ├──< IFORM_605
      │
      └──< IMPORT_LOG
```

---

# Kulcsok és azonosítók

Az adatmodellben célszerű elkülöníteni:

```text
technikai kulcs
```

és

```text
üzleti azonosító
```

fogalmát.

Például:

| Entitás             | Technikai kulcs            | Üzleti azonosító                             |
| ------------------- | -------------------------- | -------------------------------------------- |
| Company             | `company_key`              | `tax_number`                                 |
| Submission          | `submission_id`            | külső submission/respondent azonosítók       |
| Questionnaire       | belső vagy összetett kulcs | `questionnaire_code + spec_version + locale` |
| Question            | `question_id`              | `question_code`                              |
| SupplyChainRelation | `relation_id`              | requester + supplier kapcsolat               |

A technikai kulcsokhoz GUID/UUID használható.

---

# Duplikációkezelés

Az ESG adatfeldolgozás egyik fontos része a duplikációk elkerülése.

## Company duplikáció

Nem jöhet létre két külön vállalat ugyanazzal az adószámmal.

Logikailag:

```sql
UNIQUE (tax_number)
```

## SupplyChainRelation duplikáció

Ugyanaz a requester–supplier kapcsolat lehetőség szerint ne jöjjön létre többször.

Például logikai unique constraint:

```text
requester_company_key
+
supplier_company_key
```

## Submission duplikáció

A submission duplikáció ennél összetettebb.

Ugyanaz a beszállító ugyanis szerepelhet:

* több requester vállalatnál;
* több kérdőívverzióban;
* több időszakban;
* akár ugyanazon időszak újraküldéseként is.

Ezért a `supplier_key` önmagában nem lehet unique.

A duplikációs szabályt üzleti kulcs alapján kell kialakítani, például:

```text
relation
+
questionnaire
+
period
+
külső submission azonosító
```

A tényleges szabályt a forrásrendszer működéséhez kell igazítani.

---

# Időbeliség

Fontos tervezési döntés, hogy a kérdőív vonatkozási időszaka nem a vállalat tulajdonsága.

Hibás modell lenne:

```text
Company
 └── period = 2026-Q2
```

mert ugyanaz a vállalat több időszakban is szerepelhet.

A helyes kapcsolat:

```text
Company
   │
   └── SupplyChainRelation
              │
              ├── Submission 2026-Q1
              ├── Submission 2026-Q2
              ├── Submission 2026-Q3
              └── Submission 2026-Q4
```

Tehát:

```text
period → Submission
```

A `SupplyChainRelation` csak akkor kap külön érvényességi időszakot, ha később üzleti igény lesz arra, hogy magának a beszállítói kapcsolatnak a fennállását is időben nyilvántartsuk.

---

# Normalizálás

Az adatmodell célja a fölösleges adatismétlés csökkentése.

Például a cég nevét és adószámát nem szükséges minden submission rekordba bemásolni.

Ehelyett:

```text
SUBMISSION
   │
   ▼
SUPPLY_CHAIN_RELATION
   │
   ├── requester_company_key
   └── supplier_company_key
```

és:

```text
COMPANY
   ├── name
   └── tax_number
```

Ez biztosítja, hogy ugyanaz a vállalat ne több száz submission rekordban külön példányként létezzen.

---

# Domain és adatbázis kapcsolata

Az ALEX Python domain modellje nem közvetlenül SQL rekordokkal dolgozik.

Tervezett rétegzés:

```text
GUI
 │
 ▼
Service
 │
 ▼
Domain
 │
 ▼
Repository
 │
 ▼
MSSQL
```

A repository/persistence réteg feladata lesz:

```text
SQL rekord → domain objektum
domain objektum → SQL rekord
```

Például:

```python
company = company_repository.get_by_tax_number(
    "12345678-2-41"
)
```

vagy:

```python
submission_repository.save(submission)
```

A domain objektum így nem tartalmaz SQL utasításokat és nem függ közvetlenül az MSSQL-től.

---

# Tranzakciókezelés

Egy komplett submission import több táblát is érinthet.

Például:

```text
COMPANY
SUPPLY_CHAIN_RELATION
SUBMISSION_BATCH
SUBMISSION
ANSWER_VALUE
ATTACHMENT
IMPORT_LOG
```

Ezért az importot tranzakcióban célszerű végrehajtani.

Logikailag:

```sql
BEGIN TRANSACTION

    company létrehozása / keresése
    relation létrehozása / keresése
    batch létrehozása
    submission létrehozása
    answers mentése
    attachments mentése

COMMIT
```

Hiba esetén:

```sql
ROLLBACK
```

Így nem marad félkész submission az adatbázisban.

---

# Indexelés

A várható lekérdezések miatt különösen fontos indexelési mezők:

```text
COMPANY.tax_number
COMPANY.name

SUPPLY_CHAIN_RELATION.requester_company_key
SUPPLY_CHAIN_RELATION.supplier_company_key

SUBMISSION.batch_id
SUBMISSION.relation_id
SUBMISSION.supplier_key
SUBMISSION.submitted_at

ANSWER_VALUE.submission_id
ANSWER_VALUE.question_id

QUESTION.question_code
QUESTION.questionnaire_code
QUESTION.spec_version
```

Az indexeket azonban a tényleges lekérdezési minták és adatméret alapján kell véglegesíteni.

---

# Adatbázis integritás

Az alkalmazás két szinten védi az adatminőséget.

## Domain szint

Python objektumok validációja.

Például:

```text
Company tax_number nem lehet üres
RADIO válasznál csak egy opció lehet
NUMBER kérdéshez nem adható text_value
Option csak a saját kérdéséhez használható
```

## Adatbázis szint

SQL constraint-ek és foreign key-k.

Például:

```text
PRIMARY KEY
FOREIGN KEY
NOT NULL
UNIQUE
CHECK
```

A két szint együtt biztosítja, hogy hibás adat akkor se kerülhessen tartósan az adatbázisba, ha valamilyen alkalmazásoldali ellenőrzés kimarad.

---

# Adatbázis-fejlesztési irány

A következő fontos lépés a Python alkalmazásban egy külön persistence réteg létrehozása.

Javasolt szerkezet:

```text
src/alex/esg/
├── domain/
├── services/
├── mappers/
└── persistence/
    ├── company_repository.py
    ├── supplier_repository.py
    ├── supply_chain_relation_repository.py
    ├── submission_repository.py
    ├── questionnaire_repository.py
    └── attachment_repository.py
```

A GUI továbbra sem kommunikál közvetlenül az adatbázissal.

A végleges adatút:

```text
PySide6 GUI
     │
     ▼
Service
     │
     ▼
Domain
     │
     ▼
Repository
     │
     ▼
Microsoft SQL Server
```

Ez a felépítés lehetővé teszi, hogy az alkalmazás üzleti logikája független maradjon az adatbázis-technológiától, miközben az MSSQL biztosítja a tartós, konzisztens és lekérdezhető adattárolást.
