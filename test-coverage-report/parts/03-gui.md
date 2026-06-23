# Test Coverage — Gui Layer

Scope: the FreeCAD GUI layer. C++ source in `src/Gui/`, C++ tests in
`tests/src/Gui/`, and Python GUI-level tests under `src/Mod/Test/` (the
`Gui/` test-runner subdir plus the visual/selection test modules).

> Method note: there is **no compiled build** available, so all coverage
> figures below are **qualitative estimates** (None / Low / Medium / High)
> derived from reading the source tree and counting `TEST*` macros, Qt test
> slots, and Python `def test_*` methods. No percentages were measured.

---

## 1. Source surface

The Gui layer is one of the largest single modules in FreeCAD. Approximate
size of `src/Gui/`:

- **~212** `.cpp` files at the top level of `src/Gui/`.
- **~727** source files (`.cpp` + `.h`) recursively, **~416** at the top
  level alone.
- Many additional `.ui` Qt Designer forms and Python `.pyi` stubs.

Key subsystems and their approximate footprint:

| Subsystem | Where | Notes |
|-----------|-------|-------|
| Command framework | `Command.cpp`, `CommandDoc/Feat/Link/Macro/Std/Structure/View/Window/Test.cpp`, `CommandPyImp.cpp`, `CommandCompleter.cpp` (~13 `Command*.cpp`) | Action/command dispatch, undo/redo wiring, Python command binding |
| ViewProvider | **~37** `ViewProvider*.cpp` (e.g. `ViewProviderDocumentObject`, `ViewProviderLink`, `ViewProviderGeometryObject`, `ViewProviderExtension`, `ViewProviderFeaturePython`) | Visual representation of document objects; extension mechanism |
| Selection | `src/Gui/Selection/` (`Selection.cpp`, `SelectionFilter.cpp` + lex, `BoxSelection.cpp`, `SelectionFilterPy.cpp`) | Global selection singleton, selection gates, filter language |
| 3D viewer / Quarter | `src/Gui/Quarter/`, `src/Gui/Inventor/`, `View3DInventor*.cpp`, `View3DInventorViewer.cpp` | Coin3D/SoQt integration, scene rendering, navigation |
| Navigation | `src/Gui/Navigation/`, `MouseSelection.cpp` | CAD/Blender/etc. navigation styles, rubberband picking |
| Task panels | `src/Gui/TaskView/` (`TaskDialog.cpp`, `TaskDialogPython.cpp`, `TaskView.cpp`, `TaskEditControl.cpp`) | Right-hand task/dialog docking framework |
| MainWindow | `MainWindow.cpp`, `MainWindowPy.cpp` | Top-level window, MDI, docking, status bar |
| Dialogs | `src/Gui/Dialogs/` (dozens of `Dlg*.cpp`: Customize, Expression input, Version migrator, About, AddProperty, …) | Modal/modeless preference and utility dialogs |
| Document (GUI side) | `Document.cpp`, `DocumentModel.cpp`, `DocumentObserver*.cpp`, `DocumentRecovery.cpp` | GUI document, tree model, observers |
| Property editor | `src/Gui/propertyeditor/` | Property grid widgets and items |
| Style parameters | `src/Gui/StyleParameters/` | YAML-driven style/theme parameter engine (relatively new) |
| Misc widgets / infra | `Application.cpp`, `QuantitySpinBox`, `DAGView`, `PreferencePages`, `QSint`, `3Dconnexion` | Application bootstrap, custom widgets, spaceball |

---

## 2. Existing tests

### 2.1 C++ tests (`tests/src/Gui/`)

Two harnesses coexist: **GoogleTest** (linked into the single
`Gui_tests_run` executable, gated by `BUILD_GUI`) and **Qt Test**
(`QTEST_MAIN`, each built as its own executable via `setup_qt_test`). All run
under `ctest` with `QT_QPA_PLATFORM=offscreen`.

GoogleTest files (in `Gui_tests_run`):

| File | Cases | Purpose |
|------|------:|---------|
| `StyleParameters/ParserTest.cpp` | 64 | Tokenizing/parsing of the style-parameter expression grammar |
| `StyleParameters/ParameterManagerTest.cpp` | 22 | Parameter resolution, overrides, lookup in the style engine |
| `StyleParameters/YamlParameterSourceTest.cpp` | 10 | Loading style parameters from YAML sources |
| `StyleParameters/StyleParametersApplicationTest.cpp` | 4 | Applying resolved parameters to widgets/stylesheets |
| `SelectionTest.cpp` | 7 | Selection gate behavior + single-pick policy (candidate arbitration) |
| `Camera.cpp` | 6 | Camera quaternions & projections (isometric/dimetric/trimetric) |
| `FileDialog.cpp` | 3 | Save-path normalization, filter-string parsing, wildcard handling |
| `InputHintTest.cpp` | 2 | Input-hint lookup for simple/pair key states |
| `Assistant.cpp` | 1 | Smoke/sanity test (`first`) for the assistant infrastructure |

GoogleTest subtotal: **~119** cases — but **100 (84%)** are in
`StyleParameters` alone; only **~19** cover the entire rest of the Gui layer.

Qt Test files (separate executables):

| File | ~Cases | Purpose |
|------|------:|---------|
| `propertyeditor/PropertyItem.cpp` | 7 | camelCase / digit / consecutive-caps splitting of property display names |
| `Dialogs/DlgVersionMigrator.cpp` | ~7 | Preference-path migration between versions (string replace, idempotency, path generation) |
| `QuantitySpinBox.cpp` | 4 | Unit formatting in the quantity spin box (numerator/denominator/keep-format) |
| `Dialogs/DlgExpressionInput.cpp` | 2 | Implicit/implied unit handling for expressions in the input dialog |

Qt Test subtotal: **~20** cases.

> Note: of the four Qt-test files, `CMakeLists.txt` only wires up
> `setup_qt_test(QuantitySpinBox)` at the `tests/src/Gui` level; the `Dialogs`
> and `propertyeditor` subdirs are added via `add_subdirectory` and register
> their own Qt tests.

**C++ total: ~139 cases.**

### 2.2 Python GUI tests (`src/Mod/Test/`)

GUI tests are registered into `FreeCAD.__unit_test__` from
`src/Mod/Test/InitGui.py` (so they run under a real `FreeCADGui` session). The
runner infrastructure lives in `src/Mod/Test/Gui/` (`qtunittest.py`,
`UnitTestImp.cpp`, `unittestgui.py`) — a Qt front-end for the unittest suite,
not tests themselves.

| File | `def test_` | Registered? | Purpose |
|------|------:|:--:|---------|
| `Workbench.py` | 10 | yes | Workbench activation, command registration, navigation-style switching |
| `GuiDocument.py` | 9 | yes | GUI-side document operations (open/close/save, view provider lifecycle) |
| `TestCoinNodeSnapshots.py` | 6 | yes | Offscreen Coin node rendering compared against PNG baselines (visual regression) |
| `TestRubberbandSelection.py` | 6 | yes | Rubberband/box selection across multiple navigation styles |
| `TestViewProviderLink.py` | 5 | yes | `ViewProviderLink` visibility/visual behavior |
| `TestCoinSelectionVisual.py` | 3 | yes | Preselection draws above selection overlays (Coin draw-order regression) |
| `TestTreeSelection.py` | 3 | **no** (standalone only) | Tree "Select all instances" behavior |
| `Menu.py` | 2 | yes | Menu create/delete cases |

`TestGui.py` contains **0** test methods — it only registers the Test
workbench commands and the Qt unittest dialog.

**Python total: ~44 GUI test methods** (~41 auto-registered + 3 standalone in
`TestTreeSelection.py`).

---

## 3. Coverage map

| Component | C++ tests? | Python tests? | Est. coverage | Notes |
|-----------|:----------:|:-------------:|:-------------:|-------|
| StyleParameters engine | Yes (100) | No | **High** | By far the best-tested Gui area; parser/manager/yaml/application all covered |
| Selection core / gates / pick policy | Yes (7) | Partial (rubberband, visual) | **Medium** | Gate + single-pick logic unit-tested; filter language, full selection observer paths largely untested |
| Selection — visual / rubberband | No | Yes (9) | **Medium** | Box selection + Coin overlay ordering exercised through real viewer |
| Camera / projections | Yes (6) | No | **Medium** | Math (quaternions, iso/di/trimetric) covered; viewer integration not |
| File dialog logic | Yes (3) | No | **Low-Medium** | Pure path/filter helpers only; dialog UI flow untested |
| Property editor | Yes (7, name splitting) | No | **Low** | Only `PropertyItem` name formatting; editors/delegates untested |
| Dialogs (Expression input, Version migrator) | Yes (~9) | No | **Low** | Two dialogs partially; the dozens of other `Dlg*` are untested |
| QuantitySpinBox / unit widgets | Yes (4) | No | **Low-Medium** | Formatting paths only |
| Input hints | Yes (2) | No | **Low** | Lookup only |
| ViewProvider framework | No | Partial (Link, snapshots) | **Low** | ~37 providers, only `ViewProviderLink` + generic Coin snapshots tested |
| Command framework | No | Partial (Workbench cmd reg) | **Low** | Command registration touched; dispatch/undo/recompute paths untested |
| 3D viewer / Quarter / Inventor | No | Partial (Coin snapshots) | **Low** | Huge subsystem; only offscreen node rendering sampled |
| Navigation styles | No | Partial (rubberband, Workbench) | **Low** | Style switching + plain-drag rubberband only |
| Task panels (TaskView) | No | No | **None** | Task dialog/docking framework entirely untested |
| MainWindow / MDI / docking | No | No | **None** | No coverage |
| Document GUI / tree model | No | Partial (GuiDocument) | **Low** | Document lifecycle touched; `DocumentModel`/tree largely untested |
| Tree selection ("select all instances") | No | Yes (3, standalone) | **Low** | Not auto-registered, so easily skipped in CI |
| Application bootstrap, preferences, DAGView, spaceball | No | No | **None** | No coverage |

---

## 4. Gaps & risks (prioritized)

GUI code is **notoriously hard to test**: behavior depends on a live event
loop, OpenGL/Coin contexts, window managers, user input, and timing. FreeCAD
mitigates this with `QT_QPA_PLATFORM=offscreen` and offscreen Coin rendering,
but coverage remains thin and concentrated.

1. **Coverage is extremely lopsided.** ~84% of all Gui C++ test cases are in
   the (relatively new and self-contained) StyleParameters engine. The
   classic, high-traffic Gui code — Command framework, ViewProvider hierarchy,
   3D viewer, TaskView, MainWindow — has little to no dedicated C++ coverage.
   Headline test counts overstate real protection of the legacy GUI.

2. **Task panels (TaskView) and MainWindow have zero tests.** These are
   central to nearly every workbench workflow (every Sketcher/PartDesign edit
   goes through a task dialog). Regressions here are high-impact and currently
   undetectable by the suite. The recent fix "some task panels did not
   auto-close on doc close" is exactly the class of bug that lacks a guard.

3. **ViewProvider framework is barely covered.** Only 1 of ~37 providers
   (`ViewProviderLink`) plus generic Coin snapshots are tested. ViewProvider
   lifecycle, extension dispatch, and Python-feature providers are critical and
   fragile.

4. **Visual/snapshot tests are inherently brittle.** `TestCoinNodeSnapshots`
   and `TestCoinSelectionVisual` compare against PNG baselines / draw order,
   which are sensitive to driver, Coin version, font, and platform differences
   — risking flaky failures or, conversely, silent baseline rot.

5. **`TestTreeSelection.py` is not registered** in `InitGui.py`'s
   `__unit_test__`; it only runs when invoked explicitly. It can silently rot
   and won't catch regressions in normal CI runs.

6. **Two parallel C++ harnesses (GoogleTest + Qt Test).** Mixed conventions
   raise the barrier to contributing tests and make aggregate counting/CI
   wiring error-prone (e.g. only some Qt tests are explicitly registered).

7. **Command framework / undo-redo / dispatch** — the backbone of all user
   actions — has no direct unit tests; only indirect coverage via workbench
   command registration in `Workbench.py`.

8. **Dialogs largely untested.** Only 2 of dozens of `Dlg*` classes have any
   tests; preference dialogs and the Customize dialog (shortcuts, toolbars) are
   uncovered despite being frequent regression sources.

---

## 5. Recommendations

1. **Prioritize headless-testable seams, not pixels.** Extract and unit-test
   pure logic (state machines, path/filter helpers, command enable/disable
   predicates, task-dialog open/close state) so coverage doesn't depend on
   rendering. The Selection gate/pick-policy and FileDialog tests are good
   models to replicate.
2. **Add a TaskView/TaskDialog test fixture** (offscreen) covering open,
   accept/reject, and auto-close-on-document-close — directly guarding the
   recently fixed bug class.
3. **Parameterize ViewProvider tests** over the provider hierarchy (attach,
   updateData, visibility, extension dispatch) instead of one-off per-provider
   tests; reuse the existing offscreen Coin harness.
4. **Register and stabilize all Python GUI tests**, including
   `TestTreeSelection.py`, in `__unit_test__` so CI actually runs them.
5. **Make snapshot tests robust**: tolerance-based image comparison, pinned
   software-GL/Coin settings, and a documented baseline-update procedure to
   prevent flakiness and baseline rot.
6. **Consolidate on one C++ test harness** (prefer GoogleTest, the majority)
   or at least document and centralize the Qt-test registration so no test is
   silently unbuilt.
7. **Add Command-framework unit tests** for command lookup, enable state, and
   undo/redo grouping — the highest-leverage untested core.
8. **Track the StyleParameters/everything-else imbalance** explicitly in CI
   reporting so the dominant numbers don't mask legacy-GUI gaps.

---

## 6. Quick stats

- Gui source: **~212** top-level `.cpp`, **~727** total source files
  (`.cpp`+`.h`) under `src/Gui/`.
- C++ test files: **9 GoogleTest** + **4 Qt Test** = 13 files.
- C++ test cases: **~139** total (**~119** GoogleTest, **~20** Qt Test).
  - **~100 (84%)** are in `StyleParameters`; only **~19** GoogleTest cases
    cover the rest of the entire Gui layer.
- Python GUI test files: **8** with tests (+ `TestGui.py` runner/registration,
  + the `src/Mod/Test/Gui/` Qt-unittest front-end).
- Python GUI test methods: **~44** (~41 auto-registered via `InitGui.py`,
  plus 3 standalone in `TestTreeSelection.py`).
- Subsystems with **zero** tests: TaskView, MainWindow, Application bootstrap,
  most Dialogs, DAGView, spaceball/3Dconnexion, preference pages.
- Overall Gui-layer coverage estimate: **Low** (with a single **High** island
  in StyleParameters and **Medium** spots in Selection/Camera).
