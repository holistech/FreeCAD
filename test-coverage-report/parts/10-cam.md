# Test Coverage — CAM Workbench

Scope: `src/Mod/CAM/` (formerly the Path workbench) and any C++ tests under
`tests/src/Mod/CAM/`.

> Method note: This is a structural/qualitative assessment. No build was run and
> no line-coverage was measured. Coverage ratings (None/Low/Medium/High) are
> estimates justified by mapping source surface against the existing test suite
> and counted `def test_` / `TEST_F` cases.

---

## 1. Source Surface

CAM is one of the most heavily Python-centric workbenches in FreeCAD. The bulk
of path generation, dressups, post-processing, and the tool/toolbit library is
implemented in Python, with a smaller C++ core (libarea geometry, the simulator,
and `App`/`Gui` binding glue).

Approximate sizes:

- ~320 Python source files (excluding the `CAMTests/` directory).
- ~36 C++ source files in `App/` + `Gui/`, plus ~28 C++ files in the
  `PathSimulator/` (App + AppGL/OpenGL) subtree.

Key functional areas:

| Area | Location | Notable files / count |
|------|----------|-----------------------|
| Operations (App logic) | `Path/Op/` | ~23 op modules: `Profile.py`, `Pocket.py`, `PocketShape.py`, `Drilling.py`, `Adaptive.py`, `Helix.py`, `Vcarve.py`, `ThreadMilling.py`, `Tapping.py`, `Engrave.py`, `Deburr.py`, `Slot.py`, `Surface.py`, `Waterline.py`, `RotarySurface.py`, `Probe.py`, `MillFace.py`, `Custom.py`, `Area.py`, plus `Base.py`/`CircularHoleBase.py`/`PocketBase.py` bases |
| Op GUI panels | `Path/Op/Gui/` | ~30 task-panel modules mirroring the ops |
| Path generators | `Path/Base/Generator/` | ~20 modules: `drill.py`, `helix.py`, `spiral.py`, `linking.py`, `tapping.py`, `threadmilling.py`, `toolchange.py`, `rotation.py`, `dogboneII.py`, facing variants (`bidirectional_facing.py`, `directional_facing.py`, `spiral_facing.py`, `zigzag_facing.py`, `facing_common.py`), rotary variants (`rotary_dropcutter.py`, `rotary_parallel.py`, `rotary_rings.py`, `rotary_spiral.py`, `rotary_wrap.py`) |
| Dressups | `Path/Dressup/` | `DogboneII.py`, `Tags.py` (holding tags), `Array.py`, `Boundary.py`, `Utils.py` + `Gui/` |
| Post-processors | `Path/Post/scripts/` | 39 post scripts: ~13 modern (`linuxcnc_post.py`, `grbl_post.py`, `marlin_post.py`, `fanuc_legacy`→ modern `generic_post.py`, `mach3_mach4_post.py`, `masso_g3_post.py`, `centroid_post.py`, `opensbp_post.py`, `snapmaker_legacy`→ modern, `svg_post.py`, `dxf_post.py`, `smoothie_post.py`, `test_post.py`) plus 22 `*_legacy_post.py` |
| Post-processor engine | `Path/Post/` | `Processor.py`, `Command.py`, `DrillCycleExpander.py`, `GcodeProcessingUtils.py`, `UtilsArguments.py`, `UtilsExport.py`, `UtilsParse.py`, `PostList.py` |
| Tool / ToolBit library | `Path/Tool/` | `Controller.py`, `camassets.py`, `toolbit/`, `shape/`, `library/`, `assets/`, `docobject/`, `migration/` |
| Job / Stock / Sanity | `Path/Main/` | `Job.py`, `Stock.py`, `Sanity/` (incl. `ReportGenerator.py`) |
| Simulator | `PathSimulator/App` + `AppGL` | C++ material-removal simulation (~28 `.cpp`) |
| Geometry core | `libarea/`, `Path/Geom.py` | 2D area/offset engine (C++) used by Area-based ops |

---

## 2. Existing Tests

Test directory: `src/Mod/CAM/CAMTests/`. The suite is registered as a single
Python unit-test module `TestCAMApp` (`src/Mod/CAM/Init.py:51`,
`FreeCAD.__unit_test__ += ["TestCAMApp"]`); `TestCAMApp.py` imports the
individual `CAMTests/Test*` classes. There is also `TestCAMGui.py` for GUI-side
tests.

This is a large, mature suite: **99 test files** containing **~1305
`def test_` methods**, plus fixture documents (`boxtest.fcstd`,
`dressuptest.FCStd`, `Drilling_1.FCStd`, `test_adaptive.fcstd`,
`test_geomop.fcstd`, `test_holes00.fcstd`, `test_profile.fcstd`) and a
`Fixtures/` directory. Helpers: `PathTestUtils.py`, `FilePathTestUtils.py`,
`PostTestMocks.py`.

Representative tests by purpose (case counts from `def test_` per file):

| Test file | Purpose | Cases |
|-----------|---------|------:|
| `TestPostGCodes.py` | G-code word generation correctness | 74 |
| `TestPostOutput.py` | Post-processor output formatting | 57 |
| `TestOpenSBPPost.py` | OpenSBP (ShopBot) post | 55 |
| `TestPathFacingGenerator.py` | Facing path generation | 49 |
| `TestGcodeProcessingUtils.py` | G-code parse/process utilities | 47 |
| `TestPathOpUtil.py` | Op utility helpers | 41 |
| `TestPostProcessor.py` | Post engine core | 41 |
| `TestCAMSanity.py` | End-to-end job sanity checks | 31 |
| `TestTestPost.py` | Reference/diagnostic post | 31 |
| `TestPostCore.py` | Post list build, job property overrides | 28 |
| `TestPathGeom.py` | Path geometry primitives | 27 |
| `TestMachine.py` | Machine model | 26 |
| `TestLinuxCNCPost.py` / `TestLinuxCNCLegacyPost.py` | LinuxCNC post (modern/legacy) | 23 / 25 |
| `TestPathCommandAnnotations.py` | GCode command annotations | 22 |
| `TestPathUtil.py` | Path utilities + compass | 21 |
| `TestPathToolAsset*` (Asset, Cache, Manager, Store, Uri) | Tool asset framework | ~63 total |
| `TestPathToolBit*` / `TestPathToolShape*` / `TestPathToolLibrary*` | Toolbit/shape/library | ~120 total |
| `TestPathProfile.py` / `TestPathPocket.py` / `TestPathAdaptive.py` / `TestPathVcarve.py` / `TestPathHelix.py` / `TestPathThreadMilling.py` | Operation behavior | 6 / 4 / 16 / 15 / 8 / 12 |
| `TestPathDrillGenerator.py` / `TestDrillCycleExpander.py` / `TestPathDrillable.py` | Drilling | 14 / 12 / 3 |
| `TestPathDressupDogboneII.py` / `TestPathDressupHoldingTags.py` / `TestPathDressupArray.py` / `TestDressupPost.py` | Dressups | 16 / 5 / 3 / 3 |
| Per-dialect post tests (Grbl, Marlin, Fanuc, MassoG3, Centroid, Mach3/4, Snapmaker, SVG, Dxf, GenericPlasma, Generic) | Dialect output | ~10-16 each |
| `TestTSPSolver.py` / `TestLinkingGenerator.py` | Travel optimization / linking | 18 / 12 |
| Rotary suite (`TestPathRotary*` ×7) | 4th/5th-axis paths + regression | ~71 total |

C++ tests: **None.** `tests/src/Mod/` contains directories for Assembly,
Material, Measure, Mesh, MeshPart, Part, PartDesign, Points, Sketcher,
Spreadsheet, Start, TechDraw — but **no `CAM/` (or `Path/`) directory**. A search
for CAM/Path C++ test files across `tests/` returns nothing. There is no
`BUILD_CAM`-gated C++ test target. So `libarea`, the `App`/`Gui` C++ binding
layer, and the `PathSimulator` (App/AppGL) have **zero** automated C++ tests; the
simulator is exercised only indirectly, if at all.

---

## 3. Coverage Map

| Source area | Tests present | Est. coverage | Notes |
|-------------|---------------|---------------|-------|
| Post-processor engine (`Path/Post/*.py`) | `TestPostCore/Processor/Output/GCodes/MCodes`, `TestGcodeProcessingUtils`, `TestDrillCycleExpander` | **High** | Engine, G/M-word emission, parsing, drill-cycle expansion all directly tested |
| Modern post dialects (~13) | Per-dialect `Test*Post.py` for LinuxCNC, Grbl, Marlin, Fanuc, MassoG3, Centroid, Mach3/4, OpenSBP, Snapmaker, SVG, Dxf, GenericPlasma, Generic, Test | **High** | Almost all modern posts have dedicated suites |
| Legacy post dialects (22 `*_legacy_post.py`) | Only `centroid_legacy`, `mach3_mach4_legacy`, `linuxcnc_legacy`, `grbl_legacy` have files (two are commented out in `TestCAMApp.py`) | **Low** | ~18 legacy posts (dynapath, estlcam, fablin, fangling, fanuc, heidenhain, jtech, KineticNC, marlin, nccad, opensbp, philips, rml, rrf, snapmaker, uccnc, wedm, smoothie) have no tests |
| Path generators (`Path/Base/Generator/`) | Drill, Helix, Spiral, Facing, Linking, Tap, ThreadMilling, ToolChange, Rotation, DogboneII, Rotary(×5) generators all have `Test*Generator` files | **High** | Strong, focused unit coverage of geometry generation |
| Operations — Profile/Pocket/Drilling/Adaptive/Vcarve/Helix/ThreadMilling/Deburr/RotarySurface | Dedicated op tests + CAMSanity end-to-end | **Medium-High** | Core ops covered; Profile/Pocket case counts modest (6/4) so edge cases lighter |
| Operations — Surface/Waterline/Slot/Engrave/Probe/MillFace/Custom/Tapping | No dedicated `Test*` file (Tapping covered via generator) | **Low-Medium** | Exercised only indirectly via sanity/job tests if at all |
| Dressups (DogboneII, Tags, Array, Boundary) | `TestPathDressup*`, `TestPathGeneratorDogboneII`, `TestDressupPost` | **Medium-High** | DogboneII strongest; Boundary has no dedicated test |
| Tool / ToolBit / Asset library | ~25 `Test*` files (Asset, Cache, Manager, Store, Uri, Bit, Shape, Library, Serializer, Controller, Recompute, widgets) | **High** | Among the best-covered subsystems in CAM |
| Job / Stock / Setup sheet / Property bag | `TestPathStock`, `TestPathSetupSheet`, `TestPathPropertyBag`, `TestCAMSanity` | **Medium** | Job orchestration covered mainly via sanity test |
| Machine model | `TestMachine.py` | **Medium-High** | 26 cases |
| Travel/linking optimization | `TestTSPSolver`, `TestLinkingGenerator` | **Medium-High** | |
| Logging / language / preferences / util | `TestPathLog(New)`, `TestPathLanguage`, `TestPathPreferences`, `TestPathUtil`, `TestPathHelpers` | **Medium-High** | |
| Area engine (`libarea`, C++) | None direct (exercised via Area-based ops) | **Low** | No C++ unit tests; only indirect Python coverage |
| Simulator (`PathSimulator` C++/GL) | None | **None** | No automated tests at all |
| C++ App/Gui binding layer | None | **None** | No `tests/src/Mod/CAM/` |

---

## 4. Gaps & Risks (prioritized)

1. **Legacy post-processors are largely untested (HIGH RISK).** ~18 of 22
   `*_legacy_post.py` dialects have no tests, yet they emit machine-controlling
   G-code. A regression here can crash tools or scrap stock on real hardware.
   These are deprecated but still shipped and selectable; some users depend on
   them (e.g. heidenhain, dynapath, uccnc, smoothie).
2. **Simulator has zero coverage (HIGH RISK for correctness confidence).** The
   C++ material-removal simulator (`PathSimulator/App`+`AppGL`) is the user's
   primary visual safety check before cutting; a silent simulation bug gives
   false confidence. No unit or integration tests exist.
3. **`libarea` C++ geometry engine untested directly (MEDIUM-HIGH).** Offsetting/
   pocketing correctness underpins Area-based ops (Pocket, MillFace). Failures
   surface only as wrong toolpaths through indirect Python tests.
4. **Several operations lack dedicated tests (MEDIUM).** Surface (3D), Waterline,
   Slot, Engrave, Probe, MillFace, Custom have no focused `Test*` file; bugs are
   caught only if `TestCAMSanity` happens to exercise the path.
5. **Thin edge-case coverage on core 2.5D ops (MEDIUM).** Profile (6) and Pocket
   (4) have few cases relative to their option surface (entry/lead-in/out, holes,
   stepover patterns, climb/conventional, multiple passes, compensation side).
6. **Dressup Boundary untested (LOW-MEDIUM).** Boundary clipping affects emitted
   geometry but has no dedicated test.
7. **No C++ test target / `BUILD_CAM` test gating (process risk).** The entire
   suite is Python-only, so any C++ regression in bindings or geometry is
   invisible to CI until it manifests in a Python test.

---

## 5. Recommendations

1. **Backfill golden-output tests for shipped legacy posts.** For each retained
   `*_legacy_post.py`, add a small fixture job and assert against a reviewed
   reference G-code file (the modern posts already follow this pattern in
   `Test*Post.py`). Prioritize the most-used dialects (linuxcnc, grbl, marlin,
   heidenhain) and explicitly retire/remove truly dead ones to shrink the
   untested surface.
2. **Add post-processor differential tests.** Run a fixed job through each post
   and snapshot output; flag any diff in CI so unintended G-code changes are
   caught regardless of dialect.
3. **Introduce C++ tests for `libarea` and the simulator** under a new
   `tests/src/Mod/CAM/` gated by `BUILD_CAM`: offset/area correctness for known
   shapes (libarea), and a simulator volume-removal sanity check (cut a known
   path, assert removed volume/bounding box).
4. **Add dedicated op tests for Surface, Waterline, Slot, Engrave, Probe,
   MillFace** using the existing fcstd-fixture + path-assertion pattern.
5. **Expand Profile/Pocket edge-case matrices** (lead-in/out, stepover types,
   compensation side, multi-pass, open vs closed profiles).
6. **Add a Boundary dressup test** mirroring the DogboneII/Tags structure.
7. **Wire a coverage measurement pass** (e.g. `coverage.py` over `TestCAMApp`) to
   replace this qualitative estimate with measured numbers.

---

## 6. Quick Stats

- Python source files (excl. tests): **~320**
- C++ source files (App/Gui): **~36**; PathSimulator C++: **~28**
- Test directory: `src/Mod/CAM/CAMTests/`
- Test files: **99**; `def test_` methods: **~1305**
- C++ tests: **0** (no `tests/src/Mod/CAM/`)
- Post-processor scripts: **39** (≈13 modern, 22 legacy); legacy with tests: ~4
- Path generators: **~20**; Operations: **~23**; Dressups: 4
- Heaviest test files: `TestPostGCodes` (74), `TestPostOutput` (57),
  `TestOpenSBPPost` (55), `TestPathFacingGenerator` (49), `TestGcodeProcessingUtils` (47)
- Overall estimated coverage: **Medium-High for Python** (posts, generators,
  tool library, core ops strong); **None for C++** (simulator, libarea, bindings)
