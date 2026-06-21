# Test Coverage — BIM Workbench

Scope: `/home/soeren/src/FreeCAD/src/Mod/BIM/` (formerly the *Arch* workbench, plus
the *NativeIFC* layer and all geometry/IFC importers/exporters). This is an almost
entirely **Python** workbench: ~223 `.py` source files and **0 C++ files**, so all
testing is Python-side (`unittest`). The qualitative coverage estimates below are
*structural* — no build was run and no measured coverage percentage is implied.

---

## 1. Source surface

The module is large and feature-rich. Major source groups:

### Architectural / Arch objects (workbench root, `Arch*.py`)
Roughly 45 top-level `Arch*.py` files implementing the parametric BIM objects and
their view providers / GUI panels, including (non-exhaustive):

- **Building structure**: `ArchWall.py` (95 KB), `ArchStructure.py` (85 KB),
  `ArchCurtainWall.py`, `ArchBuildingPart.py` (51 KB), `ArchBuilding.py`,
  `ArchFloor.py`, `ArchSite.py` (94 KB), `ArchProject.py`, `ArchSpace.py`.
- **Openings / details**: `ArchWindow.py` (76 KB) + `ArchWindowPresets.py`,
  `ArchRoof.py` (45 KB), `ArchStairs.py` (104 KB), `ArchFence.py`, `ArchFrame.py`,
  `ArchTruss.py`, `ArchPanel.py` (57 KB), `ArchCovering.py`, `ArchPipe.py`,
  `ArchEquipment.py`.
- **Reinforcement / precast**: `ArchRebar.py`, `ArchPrecast.py` (66 KB),
  `ArchProfile.py`, `ArchNesting.py`.
- **Reference / measurement / reporting**: `ArchAxis.py`, `ArchAxisSystem.py`,
  `ArchGrid.py`, `ArchReference.py`, `ArchSchedule.py`, `ArchReport.py` (111 KB),
  `ArchSql.py` (105 KB), `ArchMaterial.py`.
- **2D / section / rendering**: `ArchSectionPlane.py` (66 KB), `ArchCutPlane.py`,
  `ArchVRM.py` (vector rendering), `ArchTessellation.py`, `OfflineRenderingUtils.py`.
- **Shared base / commands**: `ArchComponent.py` (122 KB — base class),
  `ArchCommands.py` (85 KB), `Arch.py` (102 KB — `make*` factory API).
- **IFC schema glue (legacy Arch)**: `ArchIFC.py`, `ArchIFCSchema.py`, `ArchIFCView.py`.

### IFC import/export — two independent stacks
- **Legacy / serializing IFC** (`importers/`): `importIFC.py` (63 KB),
  `exportIFC.py` (120 KB), `importIFCHelper.py`, `exportIFCHelper.py`,
  `importIFClegacy.py` (105 KB), `importIFCmulticore.py`,
  `exportIFCStructuralTools.py`. Built on **ifcopenshell**.
- **NativeIFC** (`nativeifc/`, ~21 files): live IFC-file-backed objects —
  `ifc_tools.py` (71 KB), `ifc_export.py`, `ifc_import.py`, `ifc_geometry.py`,
  `ifc_objects.py`, `ifc_viewproviders.py`, `ifc_materials.py`, `ifc_layers.py`,
  `ifc_psets.py`, `ifc_classification.py`, `ifc_observer.py`, `ifc_generator.py`,
  `ifc_diff.py`, `ifc_openshell.py`, `ifc_status.py`, `ifc_types.py`, `ifc_tree.py`.

### Other importers/exporters (`importers/`)
`importDAE.py`, `import3DS.py` (+ `Dice3DS/`), `importOBJ.py`, `importWebGL.py`,
`importJSON.py`, `importSHP.py`, `importGBXML.py`, `importSH3D.py` +
`importSH3DHelper.py` (145 KB — SweetHome3D), plus the `geometry/` and `utils/`
helper packages and `bimcommands/` (GUI command classes).

> BUILD_BIM also pulls in **Lark** (grammar/parsing used in the IFC tooling).

**Approx. source file count: ~223 Python files; 0 C++ test/source files.**

---

## 2. Existing tests

Tests live in three places. Registration is the key nuance:

- `Init.py` registers **`TestArch`** (console suite).
- `InitGui.py` registers **`TestArchGui`** (GUI suite).
- `InitGui.py` line 853 **deliberately comments out** the NativeIFC self-test:
  `# FreeCAD.__unit_test__ += ["nativeifc.ifc_selftest"]` with the note
  *"The NativeIFC tests require internet connection and file download"*.

### a) `bimtests/` — the main suite (registered)
`TestArch.py` aggregates **27 console test classes**; `TestArchGui.py` aggregates
**9 GUI test classes**. Shared base classes `TestArchBase.py` /
`TestArchBaseGui.py` provide per-test isolated documents (unique doc name, setUp /
tearDown cleanup). Fixtures: `bimtests/fixtures/` (`BimFixtures.py`,
`FC_site_simple-102.FCStd`) and `test_roof_subtraction.brep`.

| Test file | `def test*` | Purpose |
|---|---:|---|
| `TestArchReport.py` | 74 | Reporting / schedule query engine (largest suite) |
| `TestArchCovering.py` | 57 | Covering object behaviour (very detailed) |
| `TestArchStructure.py` | 22 | Structure object creation / properties |
| `TestArchComponent.py` | 18 | Shared component base (additions/subtractions, IFC props) |
| `TestArchWall.py` | 17 | Wall creation, joins, sketch base |
| `TestArchWindow.py` | 16 | Window presets / hosting |
| `TestArchBuildingPart.py` | 14 | BuildingPart/storey + **NativeIFC** level-data round-trip |
| `TestArchRebar.py` | 8 | Rebar generation |
| `TestArchRoof.py` | 7 | Roof (uses `.brep` fixture) |
| `TestArchMaterial.py` | 7 | Material / multimaterial |
| `TestArchAxis.py` | 5 | Axis objects |
| `TestArchSpace.py` | 4 | Space / boundary |
| `TestWebGLExport.py` | 4 | WebGL export |
| `TestArchStairs.py` | 3 | Stairs |
| `TestArchSectionPlane.py` | 3 | Section plane |
| `TestArchPipe.py` | 2 | Pipe |
| `TestArchFrame.py` / `TestArchEquipment.py` | 2 each | smoke creation |
| 11 others (Truss, Schedule, Reference, Project, Profile, Panel, Grid, Fence, CurtainWall, …) | 1 each | minimal smoke creation tests |
| **Console subtotal** | **274** | |

GUI suite (`*Gui.py`, headless GUI objects):

| Test file | `def test*` | Purpose |
|---|---:|---|
| `TestArchWallGui.py` | 15 | Wall view provider / task panel |
| `TestArchCoveringGui.py` | 11 | Covering GUI |
| `TestWebGLExportGui.py` | 4 | WebGL export GUI |
| `TestArchSiteGui.py` | 3 | Site GUI |
| `TestArchReportGui.py` | 2 | Report GUI |
| `TestArchImportersGui.py` | 1 | **SH3D** import only (`import_sh3d_from_string`) |
| `TestArchAxisGui` / `TestArchBuildingPartGui` / `TestArchStairsGui` | 1 each | smoke |
| **GUI subtotal** | **39** | |

### b) `nativeifc/ifc_selftest.py` — **NOT registered (disabled)**
A genuinely substantial round-trip suite (`NativeIFCTest`, **20** test methods):
import to Coin/Shape/FreeCAD, modify objects, change IFC schema, create BIM
objects, change placement/geometry, remove objects, materials, layers, psets,
storey level-data preservation. **However it downloads `IfcOpenHouse_IFC4.ifc`
from the internet at runtime**, so it is excluded from CI and effectively does not
run in normal test runs.

### c) `nativeifc/ifc_performance_test.py` — **NOT registered**
`NativeIFCTest` with ~12 timing methods (`test01..test12_IfcOpenHouse_coin`) — a
benchmark harness, not a correctness gate, also internet-dependent.

**Total authored test methods: ~345** (274 console + 39 GUI registered; 20 + ~12
NativeIFC authored-but-disabled). C++ tests: **0**.

---

## 3. Coverage map

| Area | Representative source | Test(s) | Estimated coverage |
|---|---|---|---|
| Arch base component | `ArchComponent.py` (122 KB) | `TestArchComponent` (18) | **Medium** |
| Wall | `ArchWall.py` (95 KB) | `TestArchWall` (17) + `TestArchWallGui` (15) | **Medium** |
| Structure | `ArchStructure.py` | `TestArchStructure` (22) | **Medium** |
| Covering | `ArchCovering.py` | `TestArchCovering` (57) + Gui (11) | **High** |
| Reporting / SQL | `ArchReport.py`, `ArchSql.py` (105 KB) | `TestArchReport` (74) | **Medium–High** |
| Window | `ArchWindow.py` (76 KB) | `TestArchWindow` (16) | **Medium** |
| Roof / Stairs / Space | `ArchRoof/Stairs/Space.py` | 7 / 3 / 4 | **Low–Medium** |
| BuildingPart / Site / Project / Building | `ArchBuildingPart.py`, `ArchSite.py` | BuildingPart (14, partly NativeIFC), SiteGui (3) | **Low–Medium** |
| Rebar / Precast / Profile / Panel / Nesting | `ArchPrecast.py` (66 KB), `ArchPanel.py` | Rebar 8, others 1 | **Low** (Precast/Nesting: **None**) |
| Smoke-only objects (Truss, Fence, Frame, Pipe, Grid, Axis, Equipment, CurtainWall, Schedule, Reference) | various | 1–5 each | **Low** |
| Section / 2D / VRM rendering | `ArchSectionPlane.py` (66 KB), `ArchVRM.py` | `TestArchSectionPlane` (3) | **Low** |
| Material | `ArchMaterial.py` | `TestArchMaterial` (7) | **Medium** |
| **Legacy IFC import** | `importIFC.py`, `importIFCHelper.py`, `importIFClegacy.py` | none registered | **None** |
| **Legacy IFC export** | `exportIFC.py` (120 KB), `exportIFCHelper.py`, structural tools | none registered | **None** |
| **NativeIFC import/export/round-trip** | `ifc_tools.py`, `ifc_export.py`, `ifc_import.py`, `ifc_geometry.py` | `ifc_selftest` (20, **disabled**) + 3 in `TestArchBuildingPart` | **Low** (effectively None in CI) |
| NativeIFC psets/layers/materials/classification | `ifc_psets.py`, `ifc_layers.py`, … | covered only by disabled selftest | **None (in CI)** |
| Other importers — SH3D | `importSH3DHelper.py` (145 KB) | `TestArchImportersGui` (1) | **Low** |
| Other importers/exporters — DAE, 3DS, OBJ, JSON, SHP, GBXML | `import*.py` | none | **None** |
| WebGL export | `importWebGL.py` | `TestWebGLExport` (4) + Gui (4) | **Medium** |

---

## 4. Gaps & risks (prioritized)

1. **CRITICAL — IFC round-trip correctness is untested in CI.** Both IFC stacks
   are the workbench's flagship interoperability feature and the largest source
   files (`exportIFC.py` 120 KB, `importIFC.py` 63 KB, `ifc_tools.py` 71 KB). The
   only real round-trip suite (`ifc_selftest.py`, 20 tests) is **disabled because
   it downloads a test file over the internet**. Regressions in IFC import/export
   geometry, schema mapping (IFC2X3/IFC4), placements, materials, psets, or
   classifications would pass CI undetected. This is the single highest risk.

2. **HIGH — Legacy IFC importers/exporters have zero registered tests.**
   `importIFClegacy.py`, `importIFCmulticore.py`, `exportIFCStructuralTools.py`
   and the helper modules are completely uncovered; many users still rely on the
   serializing exporter.

3. **MEDIUM–HIGH — Large complex objects are smoke-tested only.** Stairs (104 KB
   source / 3 tests), Precast (66 KB / 0), Panel/Nesting, SectionPlane + VRM 2D
   rendering (the drawing-generation path) have far too few cases for their size
   and geometric complexity.

4. **MEDIUM — Non-IFC importers/exporters uncovered.** DAE, 3DS, OBJ, SHP, GBXML,
   JSON have no tests; SH3D has a single GUI smoke test. Format-parsing code is a
   classic source of silent breakage.

5. **MEDIUM — No CI-runnable IFC fixtures.** There is no small, checked-in `.ifc`
   fixture; tests that need IFC either download (selftest) or build objects
   programmatically (BuildingPart). This is the root enabler of gap #1.

6. **LOW — No C++ tests** (expected: the workbench is pure Python).

7. **LOW — Coverage is heavily skewed**: 2 files (`TestArchReport` 74,
   `TestArchCovering` 57) account for ~48% of all console assertions, while ~15
   object types have a single smoke test.

---

## 5. Recommendations

1. **Make IFC round-trip tests CI-runnable (top priority).** Commit a small
   permissively-licensed `.ifc` fixture (or generate one in `setUp` via
   ifcopenshell/`ifc_generator.py`) and re-enable `nativeifc.ifc_selftest` with
   the network download removed. Re-registering those 20 existing tests would
   immediately convert the highest risk area from None → Medium.
2. **Add an export→import→compare round-trip test** for the legacy
   `exportIFC.py`/`importIFC.py` stack: build a Wall + Structure + Window + Space
   model, export to a temp `.ifc`, re-import, and assert object counts, placements,
   materials and key psets survive — for both IFC2X3 and IFC4 schemas.
3. **Lift smoke-only objects to behavioural tests**, prioritizing Stairs,
   SectionPlane/VRM (2D output), Precast and Panel — assert produced `Shape`
   geometry (volume/bbox/edge counts), not just object creation.
4. **Add minimal parse tests for non-IFC importers** (OBJ/DAE/3DS/SHP/GBXML) using
   tiny inline fixtures, mirroring the existing SH3D string-based approach.
5. **Track measured coverage** by adding `coverage.py` to the BIM test run to
   replace structural estimates with real numbers and pinpoint dead branches in
   the large `Arch*.py` files.
6. **Consolidate the two IFC stacks under one fixture set** so legacy and NativeIFC
   are exercised against the same models.

---

## 6. Quick stats

- **Source**: ~223 Python files, 0 C++ files. Largest: `ArchComponent.py` (122 KB),
  `exportIFC.py` (120 KB), `ArchReport.py` (111 KB), `ArchStairs.py` (104 KB).
- **Registered tests**: `TestArch` = 27 console classes (**274** `test_` methods);
  `TestArchGui` = 9 classes (**39** methods). **Total registered ≈ 313.**
- **Authored-but-disabled**: `nativeifc/ifc_selftest.py` (**20** round-trip tests,
  internet-gated, commented out in `InitGui.py:853`) + `ifc_performance_test.py`
  (~12 benchmark methods, not a unit test).
- **Total authored test methods ≈ 345.**
- **C++ tests: 0.**
- **Coverage concentration**: `TestArchReport` (74) + `TestArchCovering` (57) ≈ 48%
  of all console test methods.
- **Biggest hole**: IFC import/export — the largest, highest-value code path — has
  **no coverage in CI** (None for legacy; Low/None-in-CI for NativeIFC).
