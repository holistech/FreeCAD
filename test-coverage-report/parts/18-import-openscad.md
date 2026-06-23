# Test Coverage — Import & OpenSCAD (Data Exchange)

*Scope:* `src/Mod/Import/` and `src/Mod/OpenSCAD/`, plus any C++ tests under `tests/src/Mod/`.
*Method:* Structural/qualitative analysis of source vs. test surface. No build was performed; coverage is estimated (None/Low/Medium/High) with justification. Percentages are deliberately **not** invented.

---

## 1. Source Surface

### 1.1 Import module (`src/Mod/Import/`)

The Import workbench is the central CAD data-exchange hub. It is overwhelmingly **C++** (OCCT-backed) with a thin Python init layer.

| Area | Key files | ~LOC | Notes |
|------|-----------|------|-------|
| STEP read/write | `App/ReaderStep.cpp` (67), `App/WriterStep.cpp` (74) | ~140 | Thin wrappers over OCAF import/export pipeline |
| IGES read/write | `App/ReaderIges.cpp` (74), `App/WriterIges.cpp` (61) | ~135 | OCCT IGES translators |
| glTF read/write | `App/ReaderGltf.cpp` (167), `App/WriterGltf.cpp` (59) | ~226 | OCCT RWGltf-based |
| OCAF import core | `App/ImportOCAF.cpp` (625), `App/ImportOCAF2.cpp` (888), `App/ImportOCAFAssembly.cpp` (302) | ~1815 | Shape/color/assembly/label hierarchy reconstruction — **highest complexity** |
| OCAF export core | `App/ExportOCAF.cpp` (482), `App/ExportOCAF2.cpp` (656) | ~1138 | Shape/color/assembly export, per-face color |
| STEP shape py | `App/StepShape.cpp` (83), `App/StepShapePyImp.cpp` | ~120 | Python-exposed STEP shape access |
| DXF import/export | `App/dxf/dxf.cpp` (3259), `App/dxf/ImpExpDxf.cpp` (2367) | **~5626** | Largest single reader/writer; bespoke parser, not OCCT |
| Sketch export helper | `App/SketchExportHelper.cpp` | — | DXF/sketch geometry export |
| PLMXML assembly | `App/PlmXmlParser.py` (211) | 211 | Python PLMXML parser |
| Module / Python API | `App/AppImport.cpp`, `App/AppImportPy.cpp`, `Gui/*` | — | Exposes `open`, `insert`, `export`, `readDXF`, `writeDXFShape`, `writeDXFObject` |
| GUI | `Gui/` (12 cpp/h: Command, OCAFBrowser, Import/ExportOCAFGui, Workbench) | — | GUI commands + OCAF tree browser |

- C++ source files: **32** in `App/`, **12** in `Gui/` (+ 4 in `App/dxf/`, 2 in `Gui/dxf/`).
- Python files in module: **5** (`Init.py`, `InitGui.py`, `TestImportGui.py`, `PlmXmlParser.py`, `stepZ.py`, `DxfPlate`).
- Python entry points: `open` / `insert` / `export` (format dispatch by extension), plus DXF-specific methods.
- **OBJ / DAE(Collada)**: there is **no** OBJ or Collada reader/writer in the Import module itself. Mesh-based formats (OBJ, DAE/Collada, PLY, AMF, OFF, STL) are handled by the **Mesh** module (`tests/src/Mod/Mesh/App/Importer.cpp` exists there, out of this scope). The Import module's references to `.obj`/`info.obj` are to DocumentObject pointers, not Wavefront OBJ.
- **IFC**: not present in this module — IFC import/export is handled by the BIM / NativeIFC workbench (out of scope). No `ifc` references found in `src/Mod/Import/`.
- **ScheduleImport**: no such file or symbol found in `src/Mod/Import/`; not part of this module's surface.

### 1.2 OpenSCAD module (`src/Mod/OpenSCAD/`)

Pure-Python workbench (~5,549 LOC) for CSG/SCAD interchange and CSG feature modeling.

| Area | File | ~LOC | Notes |
|------|------|------|-------|
| CSG/SCAD import | `importCSG.py` | **1392** | PLY-based parser (`tokrules.py`) for `.csg`/`.scad`; builds FreeCAD geometry & boolean tree |
| CSG export | `exportCSG.py` | 274 | Emits `.csg` from FreeCAD objects |
| 2D geometry utils | `OpenSCAD2Dgeom.py` | 471 | 2D face/edge → polygon conversion for extrudes |
| CSG features | `OpenSCADFeatures.py` | 700 | Custom parametric feature objects (Twist, Matrix, etc.) |
| Utilities | `OpenSCADUtils.py` | 700 | Binary invocation, mesh helpers, transforms |
| Commands / GUI | `OpenSCADCommands.py` (604), `InitGui.py` (172) | ~776 | Workbench commands; some require external `openscad` binary |
| Lexer rules | `tokrules.py` | 142 | PLY token rules |
| Other | `prototype.py` (678), `expandplacements.py`, `replaceobj.py`, `colorcodeshapes.py` | — | Helpers/experimental |

---

## 2. Existing Tests

### 2.1 Import

| Test file | Registration | Cases | Purpose |
|-----------|--------------|-------|---------|
| `TestImportGui.py` | `InitGui.py`: `App.__unit_test__ += ["TestImportGui"]` — **GUI-gated only** | **1** (`testSaveLoadStepFile`) | Round-trip a `Part::Box` to STEP with **per-face color**, re-import, and assert DiffuseColor (6 faces) and Coin scene-graph material binding (`PER_PART`, 6 materials). |

- There is **no App-level (headless) test registration** for Import. The single test is registered only via `InitGui.py`, so it runs under a GUI/`ImportGui` context (it imports `ImportGui` and `pivy.coin`).
- C++ tests: **none.** No `TEST`/`TEST_F` files exist under `tests/src/Mod/Import/` (no such directory). `grep` for GoogleTest macros across `tests/src/Mod/` returns no Import/OpenSCAD targets.

### 2.2 OpenSCAD

Tests live under `src/Mod/OpenSCAD/OpenSCADTest/` (FEM-style layout), surfaced via thin shims:
- `TestOpenSCADApp.py` → imports `OpenSCADTest.app.test_importCSG` (registered in `Init.py`: `FreeCAD.__unit_test__ += ["TestOpenSCADApp"]`, **App-level / headless**).
- `TestOpenSCADGui.py` → imports `OpenSCADTest.gui.test_dummy` (registered in `InitGui.py`).

| Test file | Cases | Purpose |
|-----------|-------|---------|
| `OpenSCADTest/app/test_importCSG.py` | **27** (`def test_`) | CSG/SCAD **import** verification: primitives (sphere/cylinder/cube/circle/square radius & dims), text, polygon (path/nopath, area), polyhedron (volume), booleans (union/intersection/difference volumes), `rotate_extrude`, `linear_extrude` (incl. twist/scale volume checks), open `.csg` and `.scad` files. Uses geometric assertions (`assertAlmostEqual` on Volume/Area). |
| `OpenSCADTest/gui/test_dummy.py` | 1 | Placeholder/dummy GUI test — **no real coverage**. |

Test data (`OpenSCADTest/data/`): `CSG.csg`, `CSG.scad`, `Cube.stl`, `Square.dxf`, `Surface*.dat`, `Surface.png`.

- Notable: **CSG/SCAD export (`exportCSG.py`) is not tested.** One DXF-import test is present but **commented out** (`#test_import_import_dxf`). Tests requiring the external `openscad` binary are largely absent (import path is binary-free and is what gets tested).

---

## 3. Coverage Map

| Format / Feature | Source | Test? | Est. Coverage | Justification |
|------------------|--------|-------|---------------|---------------|
| **STEP** import/export | C++ (OCAF) | `testSaveLoadStepFile` (1, GUI-gated) | **Low** | Only one round-trip path exercised, focused on per-face color; no geometry-fidelity, units, assembly hierarchy, names, or multi-shape cases. Headless STEP path untested. |
| **STEP** per-face color | C++ ExportOCAF/ImportOCAF | yes (the 1 test) | **Medium** | This specific feature is genuinely asserted (colors + scene graph). |
| **IGES** import/export | C++ (OCCT) | none | **None** | No test references IGES. |
| **glTF** read/write | C++ (RWGltf) | none | **None** | No test references glTF. |
| **DXF** import/export | C++ (`dxf/`, 5626 LOC) | none in Import module | **None** | Largest reader, zero direct tests here. (A DXF datum exists in OpenSCAD test data; the DXF-import test is commented out.) |
| **PLMXML** assembly | `PlmXmlParser.py` | none | **None** | Untested. |
| OCAF assembly/label hierarchy | `ImportOCAF*/ExportOCAF*` (~2950 LOC) | none directly | **None–Low** | Core, high-complexity code only indirectly touched via the single color test. |
| OBJ / DAE / STL / PLY (mesh) | Mesh module (out of scope) | — | n/a | Not in Import module; covered (if at all) under Mesh. |
| IFC | BIM/NativeIFC (out of scope) | — | n/a | Not in this module. |
| **OpenSCAD CSG/SCAD import** — primitives | `importCSG.py` | 27 cases | **Medium–High** | Primitives, booleans, extrudes, polygons, polyhedra all asserted with geometric checks. |
| OpenSCAD `.scad` vs `.csg` open | `importCSG.py` | yes (both) | **Medium** | Both entry files opened and validated. |
| **OpenSCAD CSG export** | `exportCSG.py` | none | **None** | No export/round-trip test. |
| OpenSCAD 2D geom helpers | `OpenSCAD2Dgeom.py` | indirect via extrude tests | **Low** | Exercised only as a side effect. |
| OpenSCAD features / commands | `OpenSCADFeatures.py`, `OpenSCADCommands.py` | none | **None** | GUI test is a dummy. |
| OpenSCAD external-binary workflows | `OpenSCADUtils.py` | none | **None** | Binary-dependent paths untested. |

---

## 4. Gaps & Risks (prioritized)

1. **CRITICAL — CAD exchange round-trip fidelity barely tested.** STEP has a single, color-focused, GUI-gated test; **IGES and glTF have zero tests.** These are the primary interoperability formats; regressions in geometry/topology, units, precision, or color/assembly metadata would pass CI silently. Round-trip fidelity (geometry hash, volume/area, face/edge counts, units mm-vs-m) is the highest-value missing coverage.
2. **HIGH — No headless Import test.** The only Import test is registered solely in `InitGui.py` and depends on `ImportGui`/`pivy.coin`, so it cannot run in a headless/App-only test run. The bulk of import/export logic is GUI-independent and should be testable without a display.
3. **HIGH — DXF (largest reader, ~5,626 LOC) is completely untested** in the Import module, and the one OpenSCAD DXF test is commented out. DXF is a bespoke parser (no OCCT safety net), making it especially regression-prone.
4. **HIGH — OCAF assembly/hierarchy/naming/color export (~2,950 LOC of the most complex C++) is only indirectly touched.** Assembly trees, link groups, instance names, multi-body documents, and unit handling are not asserted.
5. **MEDIUM — OpenSCAD CSG export and round-trip untested.** Import is well-covered but `exportCSG.py` has no test, so import↔export symmetry is unverified.
6. **MEDIUM — No malformed/edge-case input tests.** No tests for corrupt files, empty files, unsupported entities, large assemblies, or error/exception paths (`ignore_errors` flag in `readDXF`).
7. **LOW — GUI tests are placeholders.** `test_dummy.py` and the OCAF browser GUI provide no real coverage.

---

## 5. Recommendations

1. **Add a headless `TestImportApp`** registered in `Init.py` (App-level) covering STEP/IGES/glTF round-trips using the Python `Import.export`/`Import.open` API without GUI/coin dependencies. Split the GUI-specific color/scene-graph assertions into the GUI test.
2. **Add round-trip fidelity assertions** for each format: export a known solid (box + cylinder + boolean), re-import, and assert volume, surface area, bounding box, face/edge/solid counts, and units. Treat geometric equality (within tolerance) as the contract.
3. **Create C++ GoogleTest targets** under `tests/src/Mod/Import/` for the OCAF import/export core (`ImportOCAF2`/`ExportOCAF2`) and the DXF parser (`dxf/`), since these are pure C++ with no Python wrapper and carry the most logic.
4. **Add DXF tests** (reuse `OpenSCADTest/data/Square.dxf` and add solids): import → geometry assertions, and export → re-import round-trip. Re-enable the commented-out OpenSCAD DXF test.
5. **Add OpenSCAD `exportCSG` and round-trip tests** to mirror the strong import suite, plus negative-path tests for malformed `.scad`.
6. **Add error-handling tests** for corrupt/empty/unsupported files and the `ignore_errors` path.
7. **Cover assembly/color/label preservation** explicitly (multi-part STEP/glTF, link groups, per-face colors across formats).

---

## 6. Quick Stats

| Metric | Value |
|--------|-------|
| Import C++ source files (App + Gui) | ~50 (32 App, 12 Gui, +6 dxf) |
| Import largest reader | DXF `dxf/` ≈ 5,626 LOC; OCAF import/export ≈ 4,070 LOC |
| Import Python test cases (`def test_`) | **1** (`testSaveLoadStepFile`, GUI-gated) |
| Import C++ tests (`TEST`/`TEST_F`) | **0** |
| Import headless/App test registration | **None** (GUI-gated only) |
| OpenSCAD module LOC (Python) | ~5,549 |
| OpenSCAD test cases (`def test_`) | **28** total = 27 import (`test_importCSG.py`) + 1 dummy GUI |
| OpenSCAD export (`exportCSG`) tests | **0** |
| Formats with **zero** tests | IGES, glTF, DXF (in Import), PLMXML |
| Formats with **some** tests | STEP (1, color-focused), OpenSCAD CSG/SCAD import (27) |
| Out-of-scope (other modules) | OBJ/DAE/STL/PLY → Mesh; IFC → BIM/NativeIFC |
| Overall data-exchange coverage estimate | **Low** for Import (STEP only, thin; IGES/glTF/DXF none), **Medium** for OpenSCAD import, **None** for OpenSCAD export |
