# Test Coverage — Material Workbench

Scope: `src/Mod/Material/` (App + Gui) and the C++ unit tests in
`tests/src/Mod/Material/`. This is a structural/qualitative assessment.
No build was run; coverage levels (None/Low/Medium/High) are estimates
justified by source-vs-test mapping, not measured percentages.

## 1. Source Surface

The Material module is split into the non-GUI `App` library (the `Materials`
target) and the `Gui` layer. There is also a Python layer at the module root.

### App layer (`src/Mod/Material/App/`) — ~58 files (34 `.cpp`, 24 `.h`)
The App layer is the substantive, testable core. Main concerns:

- **Material model / property system**: `Model.cpp`, `ModelProperty*`,
  `ModelLibrary.cpp`, `ModelLoader.cpp`, `ModelManager*` (Local/External),
  `ModelUuids.cpp`. Defines the "model" abstraction (groups of properties,
  e.g. physical/appearance) that materials reference.
- **Material cards & values**: `Materials.cpp` (the `Material` object),
  `MaterialProperty`, `MaterialValue.cpp` (typed values: None/String/Bool/
  Int/Float/Quantity/List/2D-array/3D-array), `PropertyMaterial.cpp`.
- **Library & card management**: `Library.cpp`, `MaterialLibrary.cpp`,
  `MaterialLoader.cpp`, `MaterialConfigLoader.cpp` (legacy `.FCMat`/card
  parsing), `MaterialManager*` (Local/External façade for lookup by
  name/UUID/path).
- **Filtering**: `MaterialFilter.cpp`, `MaterialFilterOptions`.
- **External providers**: `ExternalManager.cpp`,
  `Material/ModelManagerExternal.cpp` (pluggable external material sources).
- **Python bindings**: 12 `*PyImp.cpp` + matching `.pyi` (Material, Model,
  MaterialManager, ModelManager, MaterialLibrary, MaterialFilter, Array2D/3D,
  properties, UUIDs).
- **Bundled data**: `Resources/Materials/` ~215 `.FCMat` cards,
  `Resources/Models/` ~55 model definitions (≈276 YAML/FCMat data files total
  across the module).

### Gui layer (`src/Mod/Material/Gui/`) — ~56 files (29 `.cpp`)
Editors and dialogs: `MaterialsEditor`, `MaterialDelegate`, `MaterialSave`,
`MaterialTreeWidget`, `DlgInspectMaterial`, `DlgInspectAppearance`,
`DlgDisplayProperties`, `DlgSettings*` (Material/External/DefaultMaterial),
`AppearancePreview`, array/list editors (`Array2D`, `Array3D`, `ListEdit`,
`ImageEdit`, `TextEdit`), `TaskMigrateExternal`, `Command.cpp`, `Workbench`,
`WorkbenchManipulator`. Almost entirely Qt widget / interaction code.

### Python layer (module root)
`MaterialEditor.py`, `importFCMat.py`, `materialtools/`, `Init.py`
(registers `TestMaterialsApp` into `FreeCAD.__unit_test__`), `InitGui.py`.

## 2. Existing Tests

### C++ (GoogleTest, `tests/src/Mod/Material/App/`)
Built as `Material_tests_run` (gated by `BUILD_MATERIAL`, linked against the
`Materials` target). **7 test files, 35 `TEST_F` cases** (all fixture-based):

| File | Cases | Purpose |
|------|------:|---------|
| `TestMaterialValue.cpp` | 9 | Round-trips every value type: None, String, Bool, Int, Float, Quantity, List, Array2D, Array3D. |
| `TestMaterialProperties.cpp` | 8 | Property container: empty, single value, 2D/3D arrays incl. copy & assignment semantics. |
| `TestMaterials.cpp` | 7 | `Material` object: installation/registry, materials-with-model, lookup by path, add physical/appearance model, CalculiX steel sample, columns. |
| `TestModel.cpp` | 5 | Model subsystem: application/resources/installation, model load, lookup by path. |
| `TestModelProperties.cpp` | 3 | Model property container: empty, basic, add columns. |
| `TestMaterialCards.cpp` | 2 | Card copy and column handling. |
| `TestMaterialFilter.cpp` | 1 | Filter behavior. |

Dedicated test data lives in `tests/src/Mod/Material/App/Materials/`
(e.g. `TestAluminumPhysical.FCMat`, appearance/mixed/legacy variants).

### Python (`unittest`)
Entry modules at module root; real cases live in `materialtests/`.
**18 test methods total** (camelCase `testXxx` convention, not `test_`).

- **App suite — `TestMaterialsApp.py`** (registered in `Init.py`): imports
  `materialtests/`:
  - `TestModels.py` (5): `testModelManager`, `testUUIDs`, `testModelLoad`,
    `testTestModelCompleteness`, `testModelInheritance`.
  - `TestMaterials.py` (7): `testMaterialManager`, `testCalculiXSteel`,
    `testMaterialsWithModel`, `testMaterialByPath`, `testLists`,
    `test2DArray`, `test3DArray`.
  - `TestMaterialCreation.py` (1): `testCreateMaterial`.
  - `TestMaterialFilter.py` (2): `testFilter`, `testErrorInput`.
- **Gui suite — `TestMaterialsGui.py`** (NOT registered in `Init.py`):
  imports `TestMaterialDocument.py` (3): `testApplyDiffuseColorCheck...`,
  `testApplyShapeAppearanceCheckDiffuseColor`,
  `testApplyNoAppearanceThenAppearanceMaterial`. Exercises appearance/
  diffuse-color application on shapes.

Python test data: `materialtests/Materials/` (`Test*.FCMat` fixtures).

## 3. Coverage Map

| Source area | Tests touching it | Est. coverage | Notes |
|-------------|-------------------|:-------------:|-------|
| `MaterialValue` typed values | C++ TestMaterialValue (9), py testLists/2D/3D | **High** | All 9 value types incl. arrays covered both layers. |
| `MaterialProperty` container | C++ TestMaterialProperties (8) | **High** | Copy/assignment of 2D/3D arrays explicitly tested. |
| `Materials`/`Material` object | C++ TestMaterials (7), py TestMaterials (7) | **Medium–High** | Lookup, model add, sample cards; mutation/save paths thin. |
| Model / ModelProperty system | C++ TestModel (5)+TestModelProperties (3), py TestModels (5) | **Medium–High** | Load, inheritance, UUIDs, completeness covered. |
| MaterialManagerLocal (lookup) | C++ TestMaterials path tests, py testMaterialByPath/Manager | **Medium** | Local by-path/by-name tested; by-UUID & cache/edge thin. |
| Card parsing — legacy `MaterialConfigLoader` | Indirect via `*Legacy.FCMat` fixtures | **Low–Medium** | No direct unit test of legacy parser branches/errors. |
| Card parsing — `MaterialLoader` (current FCMat/YAML) | C++ TestMaterialCards (2), implicit installation | **Medium** | Happy-path; malformed-file handling untested. |
| MaterialFilter / FilterOptions | C++ TestMaterialFilter (1), py TestMaterialFilter (2) | **Medium** | Basic filter + error input; option combinations sparse. |
| Library management (`Library`, `MaterialLibrary`, `ModelLibrary`) | Indirect via installation/load tests | **Low–Medium** | No direct add/remove/enumerate library tests. |
| ExternalManager / *ManagerExternal | none | **None** | External provider path entirely untested. |
| Python bindings (`*PyImp`) | Exercised via py suites | **Medium** | Reached through Python tests, not exhaustively. |
| Gui (editors, dialogs, delegates, preview) | TestMaterialsGui (3, App-side appearance only) | **Low** | No widget/dialog tests; suite not even registered. |
| `importFCMat.py`, `materialtools/` | none | **None** | Untested. |
| Bundled data integrity (~215 cards, ~55 models) | py testTestModelCompleteness (models only) | **Low** | Model completeness checked; material cards not validated en masse. |

## 4. Gaps & Risks (prioritized)

1. **Card parsing robustness (HIGH).** `MaterialConfigLoader` (legacy) and
   `MaterialLoader` (current FCMat/YAML) are core to data ingestion, yet only
   happy-path fixtures exist. No tests for malformed YAML, missing required
   keys, bad UUIDs, encoding, or version/migration edge cases. A parser
   regression silently corrupts/skips materials across ~215 shipped cards.
2. **Library lookup & management (HIGH).** `MaterialManagerLocal` /
   `MaterialLibrary` / `ModelLibrary` add/remove/enumerate and by-UUID lookup
   are only indirectly exercised. Caching, duplicate-UUID collisions, and
   library precedence are untested risk areas.
3. **External providers (MEDIUM-HIGH).** `ExternalManager`,
   `MaterialManagerExternal`, `ModelManagerExternal`, `TaskMigrateExternal`
   have zero coverage — an entire feature path with no safety net.
4. **Gui layer (MEDIUM).** 29 Gui `.cpp` files, only 3 appearance-application
   tests (which are App-side behavior). `MaterialsEditor`, save dialog, tree
   widget, array/list editors untested. `TestMaterialsGui.py` is not even
   registered in `Init.py`, so it likely does not run in CI.
5. **Filter option matrix (MEDIUM).** Single C++ filter test + 2 Python tests;
   combinations of `MaterialFilterOptions` and inheritance-aware filtering are
   under-covered.
6. **Bundled material-data validation (MEDIUM).** Model completeness is
   checked but the ~215 `.FCMat` material cards are not schema-validated as a
   batch, so a malformed shipped card would not be caught by tests.
7. **Python `importFCMat`/`materialtools` (LOW-MEDIUM).** No coverage.

## 5. Recommendations

1. Add focused C++ tests for `MaterialConfigLoader` and `MaterialLoader`
   covering malformed/partial/legacy cards and explicit error/exception paths
   (use crafted bad fixtures alongside the existing `Materials/` test data).
2. Add direct `MaterialManagerLocal`/`MaterialLibrary` tests: lookup by UUID,
   duplicate-UUID handling, add/remove/enumerate, and library precedence.
3. Introduce a data-integrity test that loads every shipped `.FCMat` card and
   `Model` and asserts they parse and reference valid model UUIDs (extends the
   existing `testTestModelCompleteness` idea to materials).
4. Register `TestMaterialsGui` in `Init.py` (or document why excluded) so the
   3 existing GUI tests actually run; then grow appearance/save round-trip
   tests for `MaterialsEditor`/`MaterialSave`.
5. Add at least smoke-level tests for the External provider managers (mock
   provider) to lock down the API surface.
6. Expand `MaterialFilter` tests to cover option combinations and
   inheritance-aware filtering.

## 6. Quick Stats

- App source: ~58 files (34 `.cpp` / 24 `.h`); 12 Python-binding `*PyImp.cpp`.
- Gui source: ~56 files (29 `.cpp`).
- Bundled data: ~215 material `.FCMat` cards, ~55 model definitions
  (≈276 YAML/FCMat files module-wide).
- C++ tests: 7 files, **35 `TEST_F` cases** (`Material_tests_run`, `BUILD_MATERIAL`).
- Python tests: **18 methods** — 15 App-side (registered) + 3 Gui-side
  (TestMaterialsGui, not registered in `Init.py`).
- Strongest coverage: value types & property containers (High).
- Weakest/zero coverage: External providers, GUI widgets, `importFCMat`/
  `materialtools`, malformed-card parsing.
