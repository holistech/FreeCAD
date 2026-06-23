# Test Coverage — Build & Dev Tooling

*Scope: `src/Tools/` — the pure-Python build/developer tooling that runs outside the
FreeCAD runtime, with focus on the Python-bindings generator (`bindings/`), the
typing/stub generator (`typing/`), and the test directory `src/Tools/tests/`.
This is a structural/qualitative assessment; no build or test execution was performed
and no measured coverage percentages are claimed. Coverage is estimated qualitatively
(None / Low / Medium / High).*

---

## 1. Python Bindings Generator — `src/Tools/bindings/`

### What it does (critical path)

This is the code generator that produces FreeCAD's **entire C++ Python binding layer**.
For each binding class it consumes a model definition plus the hand-written
implementation and emits the generated wrapper that CPython actually loads:

```
*.pyi  (binding spec, new path)   ─┐
*.xml  (binding spec, legacy path)─┤──> generate.py ──> *Py.cpp  (generated wrapper)
*PyImp.cpp (hand-written impl)    ─┘                    *Py.h / *ModulePy.{h,cpp}
```

- `generate.py` (121 lines): CLI entry point. Dispatches on file extension:
  `.xml` → `model.generateModel_Module.parse` (legacy XML path);
  `.pyi` → `model.generateModel_Python.parse` (new Python-spec path). Then routes to
  one of three template emitters: class export, module export, or module skeleton.
  For `.pyi` input it also calls `Export.Compare()` (self-validation against existing
  output).
- `model/generateModel_Python.py` (949 lines): parses the new Python `.pyi`/`.module.pyi`
  binding specs (decorators `@export`, `@constmethod`, `@no_args`, `@sequence_protocol`,
  overload handling, module stubs) into the internal model.
- `model/generateModel_Module.py` (3230 lines) + `model/generateDS.py` (3476 lines,
  auto-generated XSD data binding): the **legacy XML** parsing path.
- `model/generateTools.py`, `model/typedModel.py`: helpers / typed model layer.
- `templates/templateClassPyExport.py` (1588 lines): the core C++ emitter
  (`Generate()` + `Compare()`); plus module/app templates
  (`templateModulePyExport.py` 249, `templateModule*.py`).

Total generator code ≈ **10,400 lines**.

### Test suite — `bindings/tests/`

- One file: `tests/test_generateModel_Python.py` (237 lines).
- `grep -c 'def test_'` → **6 test methods**, in 1 `unittest.TestCase`
  (`GenerateModelPythonTests`):
  1. `test_overload_only_constructor_docs_are_merged_into_class_doc`
  2. `test_existing_class_constructor_docs_are_not_duplicated`
  3. `test_module_stub_parses_to_python_module_export`
  4. `test_module_stub_uses_filename_defaults_without_module_metadata`
  5. `test_module_stub_rejects_bound_method_decorators`
  6. `test_module_stub_generation_writes_module_wrapper_files`

These tests target only the **new Python-spec parsing path**
(`generateModel_Python.parse` / `parse_python_code`) and module-wrapper emission —
mostly constructor-doc merging, module-stub defaults, and decorator validation.

### Coverage assessment (bindings)

- **New `.pyi` parsing path** (`generateModel_Python.py`): **Low–Medium** — a handful of
  focused behavioral tests, but far from exercising the full decorator/overload/attribute
  surface or the generated C++ text.
- **C++ emitters** (`templates/templateClassPyExport.py` and siblings, ~1900 lines): **None**
  — no test asserts the actual generated `*Py.cpp` content. The largest and most
  consequential component is unverified by the unit suite. (The `Compare()` self-check
  provides a weak in-tree guardrail when developers regenerate.)
- **Legacy XML path** (`generateModel_Module.py` + `generateDS.py`, ~6700 lines): **None**.
  `model/generateModel_ModuleTest.xml` exists as a sample model but is **not referenced by
  any test**. Most existing FreeCAD modules still ship XML binding specs, so this untested
  path is on the live critical path.

---

## 2. Typing / Stub Generator — `src/Tools/typing/`

### What it does

A separate, newer pipeline (`stubgen`) that produces import-shaped public `.pyi` type
stubs for the whole FreeCAD Python API (used by Pyright/Pyrefly), independent of the
binding C++ generator.

- `generate_stubs.py` (13 lines): thin entry point delegating to `stubgen.cli`.
- `stubgen/` package (~4,735 lines across 13 modules):
  `cli.py` (286), `discovery.py` (617), `source_inputs.py` (431), `class_merge.py` (782),
  `module_merge.py` (630), `parsing.py` (357), `render.py` (235), `model.py` (237),
  `type_context_rules.py` (211), `generator.py` (182), `doc_lint.py` (146),
  `__init__.py` (24), `naming.py` (16).
- `generated/` is disposable local output (only `.gitignore` is committed).
- `inputs/overlays/` holds hand-written overlays (e.g. `PySide/QtCore.pyi`).
- `smoke/smoke.py` (568 lines): an import- and call-heavy module that Pyright + Pyrefly
  type-check against the generated stubs (`check` mode) — a regression tripwire for moved /
  removed / re-typed symbols.
- `check-stubs.sh`: convenience wrapper running `generate_stubs.py check`.
- `README.md`: thorough documentation of the workflow, overlay rules, `@typing_only`,
  and maintenance direction.

### Test suite — typing

- **No unit tests.** `grep -rl 'def test_|unittest|pytest' typing/` returns nothing.
- Validation is **only indirect**:
  - the **smoke type-check** (`smoke.py` via Pyright/Pyrefly) — exercises generated output,
    not the generator logic, and is not a unit test;
  - the **doc linter** (`doc_lint.py`, invoked via `generate_stubs.py lint-docs`) — checks
    curated source stubs for docstrings, not generator correctness.
- Coverage: **None** for the ~4,700-line `stubgen` package itself.
- Critical caveat: the smoke check and `check-stubs.sh` are **not wired into CI**
  (see §5), so even the indirect safety net is manual-only.

---

## 3. Other Tools Under `src/Tools/`

### `src/Tools/tests/` — `test_sync_version.py` (well covered)

- 452 lines, **42 `def test_`** across 8 `TestCase` classes:
  `TestVersionInfo`, `TestReplaceInTomlSection`, `TestSyncWorkspacePixiToml`,
  `TestSyncRattlerBuildPixiToml`, `TestSyncRecipeYaml`, `TestSyncDeclarationsNsh`,
  `TestSyncFedoraSpec`, `TestRun`.
- Targets `sync_version.py` (version propagation into pixi/rattler/recipe/NSIS/Fedora-spec
  packaging files). Coverage of that script: **High** — version parsing, per-file sync
  logic, and the check/update orchestration are all exercised.
- This is the **only** tool-test directory wired into CI.

### Untested tools

- `params_utils.py` (29,830 bytes): generates parameter-accessor C++/Python code; imported
  by several `*Params.py` files (`src/App/LinkParams.py`, `src/Gui/TreeParams.py`,
  `OverlayParams.py`, `DlgSettingsAdvanced.py`). **No tests**, no self-test block.
- Numerous standalone scripts with **no tests**: `updatets.py`, `updatecrowdin.py`,
  `SubWCRev.py`, `MakeMacBundleRelocatable.py`, `dir2qrc.py`, `makedist.py`,
  `LicenseChecker.py`, `MakeNewBuildNbr.py`, `make_snapshot.py`, `doctools.py`, etc.

---

## 4. Coverage Map

| Tool / module | Has tests? | Est. coverage | Notes |
|---|---|---|---|
| `bindings/generate.py` (entry) | Indirect | Low | Exercised only through `generateModel_Python` tests; CLI/arg handling untested |
| `bindings/model/generateModel_Python.py` (new `.pyi` path) | Yes (6 tests) | Low–Medium | Constructor docs, module stubs, decorator validation only |
| `bindings/templates/templateClassPyExport.py` (C++ emitter) | No | None | Largest emitter; generated `*Py.cpp` text never asserted |
| `bindings/model/generateModel_Module.py` (legacy XML path) | No | None | ~3.2k lines; still used by most modules |
| `bindings/model/generateDS.py` (XSD databinding) | No | None | ~3.5k lines, auto-generated |
| `typing/stubgen/*` (whole package) | No | None | ~4.7k lines; only indirect smoke + doc-lint validation |
| `typing/smoke/smoke.py` | n/a (is a checker input) | — | Type-check tripwire, not in CI |
| `tools/sync_version.py` | Yes (42 tests) | High | The model citizen; runs in CI |
| `params_utils.py` | No | None | Generates parameter accessors; widely imported |
| Misc scripts (`updatets`, `SubWCRev`, `makedist`, …) | No | None | Build/packaging utilities |

---

## 5. Gaps & Risks (prioritized)

1. **CRITICAL — the C++ binding emitter is untested and the legacy XML path has zero
   coverage.** `templateClassPyExport.py` plus `generateModel_Module.py`/`generateDS.py`
   (~8,600 lines combined) generate the wrappers CPython loads. A silent defect here can
   corrupt the entire Python API surface (wrong signatures, refcount/ownership bugs,
   missing slots) and would only surface as runtime crashes or subtle API breakage far
   from the cause. No test asserts the generated source text for either path.

2. **CRITICAL — the bindings tests are not run in CI.** CI (`.github/workflows/
   sub_buildPixi.yml:215`) runs only:
   `python3 -m unittest discover -s src/Tools/tests -p "test_*.py"`.
   That `-s src/Tools/tests` root does **not** include `src/Tools/bindings/tests/`, so the
   6 binding-generator tests never run automatically. They can rot silently.

3. **HIGH — the `stubgen` typing package (~4,700 lines) has no unit tests**, and its only
   safety nets (Pyright/Pyrefly smoke check, doc-lint) are also **not in CI**. Stub
   regressions degrade the IDE/type-checking experience for all downstream users and may go
   unnoticed until a checker run is performed manually.

4. **MEDIUM — `params_utils.py` (another code generator, ~30 KB) is untested** despite
   feeding several runtime `*Params.py` modules.

5. **LOW–MEDIUM — packaging/maintenance scripts** (`updatets`, `updatecrowdin`,
   `MakeMacBundleRelocatable`, `makedist`, `SubWCRev`) are untested; failures here affect
   releases/translations rather than the core API.

---

## 6. Recommendations

1. **Add golden-output (snapshot) tests for the C++ emitters.** Feed a small representative
   `.pyi` and `.xml` model through `generate.py` and assert the generated `*Py.cpp`/`*Py.h`
   against checked-in golden files. This is the single highest-value addition and directly
   guards the API surface. Wire `generateModel_ModuleTest.xml` into a regression test to
   cover the legacy path.
2. **Fix CI discovery** so the binding-generator tests actually run — either change the
   `discover` root to `src/Tools` (recursive) or add an explicit second `discover` step for
   `src/Tools/bindings/tests`.
3. **Add `stubgen` unit tests** for `parsing.py`, `class_merge.py`, `module_merge.py`, and
   `render.py` (parse-fixture → expected model/stub-text), and **run `check-stubs.sh`
   (smoke + lint-docs) in CI** to make the existing indirect checks enforcing.
4. **Add tests for `params_utils.py`** mirroring the `sync_version` snapshot style.
5. Treat `sync_version.py` as the template for tool test quality (small, isolated,
   deterministic, CI-wired) and replicate that pattern across the other generators.

---

## 7. Quick Stats

- Tool test files: **2** (`bindings/tests/test_generateModel_Python.py`,
  `tests/test_sync_version.py`).
- Total tool `def test_`: **48** (6 bindings + 42 sync_version).
- Test files actually run in CI: **1** (`test_sync_version.py`); bindings tests **not** in CI.
- Bindings generator code: ~**10,400** lines; under test: only the `.pyi` parsing path
  (Low–Medium), C++ emitters and full XML path **untested**.
- `stubgen` typing code: ~**4,735** lines across 13 modules; unit tests: **0**.
- Untested major generators: `templateClassPyExport.py` (1588), `generateModel_Module.py`
  (3230), `generateDS.py` (3476), full `typing/stubgen/`, `params_utils.py` (~30 KB).
- Best-covered tool: `sync_version.py` (42 tests, High, CI-wired).
