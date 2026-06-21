# Test Coverage — App Core

*Scope: the headless FreeCAD document model. Source in `src/App/`; C++ tests in
`tests/src/App/`; Python-level behaviour in `src/Mod/Test/` (notably
`Document.py`). Coverage is assessed qualitatively (None/Low/Medium/High) — there
is no compiled build and no measured line/branch numbers.*

## 1. Source surface

The App library is the structural heart of FreeCAD: the persistent document, the
object dependency graph, the property/parametric system and the expression
engine. It is large — roughly **95 `.cpp` / 86 `.h` files (~61k lines of `.cpp`)**.

Key classes / algorithms:

- **Document model** — `Document.cpp` (~4.1k lines): object lifecycle, save/
  restore (project XML + zip), transactions/undo-redo, dependency-ordered
  recompute, topological sort, partial/clone restore, recovery snapshots
  (`RecoverySnapshot`, `BackupPolicy`), merge (`MergeDocuments`).
- **DocumentObject graph** — `DocumentObject.cpp`, `DocumentObjectGroup`,
  `GeoFeature`, `Datums`, extension mix-ins (`ExtensionContainer`, `Extension`,
  `GroupExtension`, `GeoFeatureGroupExtension`, `OriginGroupExtension`,
  `SuppressibleExtension`, `LinkBaseExtension`).
- **Property system** — `Property.cpp`, `PropertyContainer`, `PropertyStandard`
  (~3.7k), `PropertyUnits`, `PropertyGeo`, `PropertyLinks` (~6k — the largest and
  most intricate file: link scoping, back-links, label/sub-element tracking),
  `PropertyExpressionEngine`, `PropertyFile`, `PropertyPythonObject`,
  `DynamicProperty`, `Enumeration`.
- **Expression engine** — `Expression.cpp` (~3.8k), generated parser
  (`Expression.y/.l` → `Expression.tab.c`, `Expression.lex.c`),
  `ExpressionParser`, `ExpressionTokenizer`, `ObjectIdentifier` (~2k, variable
  binding/path resolution), `Range`, `ExpressionVisitors`.
- **Link system** — `Link.cpp` (~2.8k), `LinkBaseExtension`.
- **ElementMap / topological naming** — `ElementMap`, `ElementNamingUtils`,
  `MappedName`, `MappedElement`, `IndexedName`, `ComplexGeoData`, `StringHasher`/
  `StringID`.
- **Application & infrastructure** — `Application.cpp` (~3.8k): app singleton,
  document registry, signals, Python bindings; `ApplicationDirectories`,
  `Branding`, `Services`, `SafeMode`, `AutoTransaction`, `Metadata`, `VarSet`,
  `MeasureManager`, `Material`, `Datums`, `Origin`, `Part`.

## 2. Existing C++ tests

All under `tests/src/App/`, each a GoogleTest suite linked into the App test
runner. Approximate `TEST`/`TEST_F` case counts (per file):

| File | Cases | Purpose (one line) |
|------|------:|--------------------|
| `StringHasher.cpp` | ~114 | StringHasher / StringID hashing, persistence, base64, ref-counting (best-covered area) |
| `ApplicationDirectories.cpp` | ~58 | Resolution of config/data/temp/user directory paths and overrides |
| `MappedName.cpp` | ~51 | MappedName construction, comparison, postfix/prefix handling |
| `Expression.cpp` | ~38 | Expression AST evaluation, units, functions, error handling |
| `IndexedName.cpp` | ~37 | IndexedName parsing/formatting of `Type123` element names |
| `Link.cpp` | ~34 | Link/LinkBaseExtension wiring, linked-object resolution |
| `ComplexGeoData.cpp` | ~31 | ComplexGeoData element-map plumbing and bounds |
| `BackupPolicy.cpp` | ~26 | Backup file rotation / naming policy |
| `Metadata.cpp` | ~18 | package.xml metadata parsing |
| `MappedElement.cpp` | ~18 | MappedElement pair (name+index) behaviour |
| `Property.cpp` | ~16 | Base Property semantics, touched/status flags |
| `ElementMap.cpp` | ~16 | ElementMap set/get, child maps, serialization |
| `ExpressionParser.cpp` | ~11 | Grammar/tokenizer parse-tree correctness |
| `ProjectFile.cpp` | ~10 | Project zip/file container read/write |
| `License.cpp` | ~6 | License id/text lookup |
| `Application.cpp` | ~6 | Application-level smoke/registry |
| `DocumentObserver.cpp` | ~4 | DocumentObserver notifications |
| `Document.cpp` | ~3 | Minimal document smoke tests (very thin vs. 4.1k-line source) |
| `VarSet.cpp` | ~2 | VarSet container basics |
| `ElementNamingUtils.cpp` | ~2 | Element naming helper utilities |
| `AsyncRecompute.cpp` | ~2 | Asynchronous recompute path |
| `DocumentObject.cpp` | ~1 | DocumentObject smoke |
| `PropertyExpressionEngine.cpp` | ~1 | Expression-engine property binding smoke |
| `VRMLObject.cpp` | ~1 | VRMLObject smoke |
| `Branding.cpp` | ~1 | Branding parse smoke |

**Total: ~508 C++ test cases across 25 files.** Distribution is heavily skewed —
StringHasher + element-map/naming + directory tests dominate, while the
behaviourally central `Document`, `DocumentObject` and `PropertyExpressionEngine`
have only smoke-level C++ coverage.

## 3. Python-level tests

App-core behaviour is exercised mainly from `src/Mod/Test/`:

- **`Document.py` — ~121 test cases (22 test classes)**, the primary functional
  net for the document model. Classes: `DocumentBasicCases`,
  `DocumentSaveRestoreCases`, `DocumentRecoveryCases`, `DocumentRecomputeCases`,
  `UndoRedoCases`, `DocumentGroupCases`, `DocumentPlatformCases`,
  `DocumentBacklinks`, `DocumentFileIncludeCases`, `DocumentPropertyCases`,
  `DocumentExpressionCases`, `DocumentObserverCases`, `MultiDocumentUndo`,
  `FeatureTest*` (column/row/address/attribute), `DocumentAutoCreatedCases`.
  Covers add/remove/undo, transactions, recompute (incl. cyclic dependency),
  extensions, save/restore, backlinks, dynamic properties, link properties,
  expressions on properties, and observer signals.
- **`BaseTests.py` — ~49 cases**: matrix/placement algebra, units, parameters,
  console, filesystem helpers.
- **`UnitTests.py` — ~12**, **`Metadata.py` — ~12**, **`StringHasher.py` — ~4**,
  **`TestApp.py` — ~3**, **`UnicodeTests.py` — ~2**.

Python tests are registered through `FreeCAD.__unit_test__` (see
`src/App/FreeCADInit.py`, `App.__unit_test__ = []`) and the Test module's
`Init.py`. Python coverage is functional/integration-style and is the dominant
source of real-world App-core exercise — far broader than the C++ Document tests.

## 4. Coverage map

| Component | C++ tests? | Python tests? | Est. coverage | Notes |
|-----------|:---------:|:-------------:|:-------------:|-------|
| Document lifecycle / save / restore | Smoke only (~3) | Yes (Document.py) | **Medium** | Behaviour covered in Python; C++ unit coverage thin for a 4.1k-line file |
| Transactions / Undo-Redo | No | Yes (UndoRedoCases, MultiDocumentUndo) | **Medium** | Python-only; nested/aborted transaction edge cases partial |
| Recompute engine / topo sort | AsyncRecompute (~2) | Yes (DocumentRecomputeCases) | **Medium** | Cyclic dependency tested; ordering/error-propagation under-tested at unit level |
| DocumentObject graph | Smoke (~1) | Indirect | **Low–Med** | Mostly exercised via Document.py, no focused C++ suite |
| Property system (base) | Property.cpp (~16) | DocumentPropertyCases | **Medium** | Base semantics OK; many concrete property types untested |
| PropertyStandard / PropertyUnits | No | Partial (BaseTests units) | **Low** | ~3.7k lines of property types with little direct coverage |
| PropertyLinks (link props) | Via Link.cpp | DocumentBacklinks, link cases | **Low–Med** | Largest file (~6k), scoping/back-link logic under-tested for its complexity |
| Expression engine / parser | Expression(~38)+Parser(~11) | DocumentExpressionCases | **Medium–High** | Best-tested compute area; ObjectIdentifier still light |
| ObjectIdentifier / Range | No direct | Indirect via expressions | **Low** | ~2k lines, no dedicated suite |
| Link / LinkBaseExtension | Link.cpp (~34) | Link-related Document cases | **Medium** | Good for core wiring; advanced link arrays/visibility partial |
| ElementMap / topo naming | Strong (Map/Mapped/Indexed/ElementNaming) | StringHasher.py | **Medium–High** | Naming primitives well covered; integration with recompute less so |
| StringHasher / StringID | Strong (~114) | Yes (~4) | **High** | Best-covered component |
| ComplexGeoData | ComplexGeoData (~31) | No | **Medium** | Element-map plumbing covered; geometry payload less so |
| Extensions (Group/Geo/Origin) | No | Yes (testExtensions etc.) | **Low–Med** | Python smoke only; no C++ unit suites |
| DocumentObserver | DocumentObserver (~4) | DocumentObserverCases | **Medium** | Signal coverage reasonable |
| Metadata (package.xml) | Metadata (~18) | Metadata.py (~12) | **High** | Both layers |
| VarSet | VarSet (~2) | No | **Low** | Minimal |
| Application / registry | Application (~6) | TestApp (~3) | **Low–Med** | Mostly smoke |
| ApplicationDirectories | Strong (~58) | No | **High** | Path logic thoroughly tested |
| Backup / Recovery | BackupPolicy (~26) | DocumentRecoveryCases | **Medium–High** | Both layers |
| MeasureManager / Material / Datums / Origin | No | No | **None–Low** | No dedicated tests found |
| AutoTransaction / SafeMode / Services | No | Indirect | **Low** | No focused tests |

## 5. Gaps & risks (prioritized)

1. **Document.cpp has only smoke-level C++ tests** (~3 cases for ~4.1k lines).
   The most critical state machine (save/restore, transaction boundaries,
   recompute ordering, partial restore, recovery) relies almost entirely on
   Python integration tests, which are coarser and harder to pin failures to.
2. **PropertyLinks (~6k lines) is under-tested for its complexity.** Link
   scoping, back-link bookkeeping, label/sub-element re-resolution and dangling-
   link handling are correctness-critical and a frequent source of regressions;
   no dedicated C++ suite isolates them.
3. **ObjectIdentifier / Range have no dedicated suite** (~2k lines). Path
   resolution and rename propagation underpin every expression; only covered
   transitively.
4. **Concrete property types (`PropertyStandard`, `PropertyUnits`, `PropertyGeo`)
   lack direct unit tests** — serialization round-trip, copy/paste,
   touched/diff semantics per type are largely unverified at unit level.
5. **Extensions and group hierarchies** (`GeoFeatureGroupExtension`,
   `OriginGroupExtension`, `SuppressibleExtension`) have Python smoke coverage
   only; placement-inheritance and containment-chain logic are risk areas.
6. **No tests for MeasureManager, Material, Datums, Origin, AutoTransaction,
   SafeMode** — silent (None/Low) coverage.
7. **Recompute error/exception propagation and skip/touch flag interactions**
   are tested happy-path; failure paths and `mustExecute`/error-marking edges
   are thin.

## 6. Recommendations (concrete)

1. Add a focused `tests/src/App/Document.cpp` expansion: transaction
   open/commit/abort/nesting, undo/redo stack limits, dependency-ordered
   recompute including failure marking, save→restore round-trip of a multi-
   object graph, and partial/clone restore.
2. Create `tests/src/App/PropertyLinks.cpp`: single/list/sub links, scope
   (Global/Child/Hidden), back-link registration/removal on object delete,
   label-based re-resolution after rename, and dangling-link recovery.
3. Add `tests/src/App/ObjectIdentifier.cpp`: path parse/format, binding to
   document objects/properties, rename propagation, and `Range` iteration.
4. Add per-type property suites (`PropertyStandard`/`PropertyUnits`/
   `PropertyGeo`): set/get, `Save`/`Restore` round-trip, `Copy`/`Paste`,
   `isSame`/diff, and notification on change.
5. Add C++ suites for the group/geo/origin extensions covering placement
   inheritance and containment chains (mirror `DocumentGroupCases`).
6. Backfill at least smoke + round-trip tests for MeasureManager, Material,
   Datums, Origin, and AutoTransaction (RAII transaction guard semantics).
7. Strengthen recompute tests for error propagation: object throwing in
   `execute()`, error flags, and downstream skip behaviour.

## 7. Quick stats

- App source: ~**95 `.cpp` / 86 `.h`**, ~**61k lines of `.cpp`**.
- C++ tests: **25 files**, **~508 `TEST`/`TEST_F` cases**; heavily concentrated
  in StringHasher (~114), ApplicationDirectories (~58) and element-map/naming.
- Python (App-core): **~190+ cases** dominated by `Document.py` (**~121**,
  22 classes) plus `BaseTests.py` (~49), `UnitTests.py`/`Metadata.py` (~12 each).
- Best covered: StringHasher/StringID, ApplicationDirectories, element/naming
  primitives, Metadata.
- Weakest covered: Document.cpp (C++), PropertyLinks, ObjectIdentifier, concrete
  property types, extensions, and the un-tested MeasureManager/Material/Datums/
  Origin group.
- Overall App-core C++ unit maturity: **Medium**, propped up substantially by
  Python integration tests; the central document/property/link logic is the
  weakest at the unit-test level relative to its size and importance.
