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
