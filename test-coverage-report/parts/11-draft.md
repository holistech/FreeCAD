# Test Coverage — Draft Workbench

Scope: `/home/soeren/src/FreeCAD/src/Mod/Draft/`

Draft is the 2D drafting workbench. It is **pure Python** (no compiled C++
module of its own; it relies on the OCC/Part kernel through Python). All tests
are therefore Python `unittest` cases. There are essentially **no C++ unit
tests** for Draft, which is expected for a Python module.

Tests are registered in:
- `src/Mod/Draft/Init.py` line 40: `App.__unit_test__ += ["TestDraft"]`
  (non-GUI tests)
- `src/Mod/Draft/InitGui.py` line 264: `FreeCAD.__unit_test__ += ["TestDraftGui"]`
  (GUI-only tests)

The two entry modules `TestDraft.py` and `TestDraftGui.py` import test classes
from the `drafttests/` package and expose them for the FreeCAD test runner
(`FreeCAD -t TestDraft`).

---

## 1. Source Surface

Draft was historically a few very large monolithic modules and has been
progressively refactored into focused sub-packages. Both layers still coexist.

### Refactored sub-packages (modern code)

| Sub-package | Files (excl. `__init__`/README) | Responsibility |
|---|---:|---|
| `draftobjects/` | 28 | Scripted-object proxy classes (data) — Wire, Circle, Arc, Ellipse, Polygon, Rectangle, BSpline, BezCurve, Dimension, Text, Label, Layer, Hatch, Clone, Array family (ortho/polar/circular/path/point/twisted), Facebinder, Fillet, Shape2DView, ShapeString, Point, Block, WPProxy, Base/Annotation/DraftLink mixins |
| `draftmake/` | 31 | `make_*` factory functions that create the scripted objects (the public scripting API: `make_line`, `make_circle`, `make_array`, `make_dimension`, `make_sketch`, …) |
| `draftfunctions/` | 20 | Modification operations: move, rotate, scale, mirror, offset, array, cut, fuse, join, split, upgrade, downgrade, draftify, extrude, heal, and SVG generation (`svg.py`, `svgshapes.py`, `svgtext.py`, `dxf.py`) |
| `draftgeoutils/` | 18 | Geometry helpers: arcs, circles, Apollonius circles, circle inversion, edges, faces, fillets, intersections, offsets, sort_edges, wires, linear_algebra, geometry, cuboids, geo_arrays |
| `draftguitools/` | 66 | GUI command classes (`gui_*`), the snapper, trackers, edit/snap framework, tool utils — the interactive command layer |
| `draftviewproviders/` | 23 | `ViewProvider*` classes (visual representation / GUI properties) |
| `drafttaskpanels/` | 7 | Qt task-panel dialogs (arrays, scale, shapestring, selectplane) |
| `draftutils/` | 12 | Utilities: utils, gui_utils, groups, params, units, messages, translate, todo, init_tools, init_draft_statusbar, grid_observer |

Sub-package total: **≈ 205 Python files**.

### Legacy top-level modules (still load-bearing)

These large files at the package root carry a lot of behaviour and remain in
active use:

- `importDXF.py` (**~5,119 lines**) — DXF import/export (the single largest and
  riskiest file)
- `importSVG.py` (~1,541 lines) — SVG import
- `importDWG.py`, `importOCA.py`, `importAirfoilDAT.py` — additional importers
- `Draft.py`, `DraftGeomUtils.py`, `DraftVecUtils.py` — backward-compat shims /
  vector + geometry math
- `WorkingPlane.py`, `DraftTools.py`, `DraftGui.py`, `DxfImportDialog.py`,
  `SVGPath.py`

Grand total source surface: **≈ 220 Python files** (sub-packages + legacy
top-level), dominated in size by the DXF/SVG import code.

---

## 2. Existing Tests (`drafttests/`)

19 files in `drafttests/`. Two are infrastructure (`test_base.py` provides
base `TestCase` classes; `draft_test_objects.py` is a shared object-creation
helper, ~21 KB, used to populate a document with one of every Draft object),
plus `auxiliary.py` and the `Issue24314.dxf` fixture.

`def test_` counts per file:

| Test module | `def test_` | Purpose | In active suite? |
|---|---:|---|---|
| `test_creation.py` | 25 | Create every Draft primitive (line, polyline, fillet, circle, arc, arc-3pt, ellipse, polygon, rectangle, text, dimensions linear/radial/angular, bspline, point, shapestring, facebinder, bezcurve, label, layer, WP proxy, hatch) | Yes (TestDraft) |
| `test_modification.py` | 31 | move, copy, rotate, offset (open/closed/face), trim, extend, join, split, upgrade, downgrade, wire→bspline, shape2dview, draft→sketch, arrays (rect/polar/circular/path/point), clone, draft→techdraw, mirror, stretch, scale (part-feature arcs/lines, rectangle, spline, wire) | Yes (TestDraft) |
| `test_draftgeomutils.py` | 9 | `get_extended_wire` (8 variants) + `make_segment_face` repair of crossed connectors | Yes (TestDraft) |
| `test_svg.py` | 7 | SVG read + export regressions (arch space zero-vector, circular-island faces, TechDraw path, compactness) | Yes (TestDraft) |
| `test_dxf.py` | 2 | DXF read (Issue24314 fixture) + export | Yes (TestDraft) |
| `test_import.py` | 4 | Smoke import of `Draft`, `DraftGeomUtils`, `DraftVecUtils`, SVG modules | Yes (TestDraft) |
| `test_array.py` | 1 | Array regression | Yes (TestDraft) |
| `test_import_gui.py` | 4 | GUI import smoke | Yes (TestDraftGui) |
| `test_import_tools.py` | 3 | GUI tool import | Yes (TestDraftGui) |
| `test_pivy.py` | 2 | Coin/pivy tracker availability | Yes (TestDraftGui) |
| `test_dimension_gui.py` | 2 | Dimension GUI command behaviour | Yes (TestDraftGui) |
| `test_manual_input_gui.py` | 23 | Manual coordinate-entry workflow for GUI commands | Yes (TestDraftGui) |
| `test_dwg.py` | 2 | DWG import/export | **No — commented out** in TestDraft |
| `test_oca.py` | 2 | OCA import/export | **No — commented out** |
| `test_airfoildat.py` | 2 | Airfoil .dat import | **No — commented out** |
| `test_base.py` | 0 | Base TestCase classes (doc / no-doc setUp/tearDown) | infra |
| `draft_test_objects.py` | 0 | Helper: build a document of all object types | infra |

**Totals:** ~119 `def test_` across all files; **~113 active** (DWG/OCA/Airfoil,
6 cases, are disabled in the registered suites). Active split ≈ 79 non-GUI
(TestDraft) + 34 GUI (TestDraftGui).

---

## 3. Coverage Map

| Sub-package | What is tested | Direct test module(s) | Estimated coverage |
|---|---|---|---|
| `draftmake/` (creation API) | Almost every `make_*` exercised via `test_creation` / `test_modification` (lines, arcs, circles, ellipses, polygons, rectangles, splines, beziers, dimensions, text, label, layer, hatch, arrays, clone, shapestring, facebinder) | `test_creation`, `test_modification`, `draft_test_objects` | **Medium-High** |
| `draftobjects/` (proxy classes) | Indirectly covered through creation/modification (object is built and basic properties checked). `recompute`/edge cases lightly hit. `block`, `pathtwistedarray`, `wpproxy` thin | same as above | **Medium** |
| `draftfunctions/` (modify ops) | Good breadth: move, rotate, scale, mirror, offset, join, split, up/downgrade, draftify; SVG export tested via `test_svg`; DXF export via `test_dxf` | `test_modification`, `test_svg`, `test_dxf` | **Medium** |
| `draftgeoutils/` (geometry) | Only `get_extended_wire` + one `make_segment_face` path. arcs/circles/Apollonius/inversion/intersections/offsets/fillets/sort_edges largely **untested** | `test_draftgeomutils` | **Low** |
| `draftguitools/` (GUI commands, 66 files) | Manual-input workflow (23 cases) + dimension GUI (2) + import-tool import (3) + pivy (2). The snapper, trackers, edit framework, and the bulk of `gui_*` commands are **not** exercised | `test_manual_input_gui`, `test_dimension_gui`, `test_import_tools`, `test_pivy` | **Low** |
| `draftviewproviders/` (23 files) | Only incidentally instantiated when objects are made with GUI up; no dedicated assertions | (incidental) | **Low / None** |
| `drafttaskpanels/` (7 files) | No dedicated tests | — | **None** |
| `draftutils/` (12 files) | No dedicated unit tests; `params`/`units`/`utils` exercised only indirectly | (incidental) | **Low / None** |
| Legacy `importDXF.py` (~5.1k lines) | One read fixture + one export round-trip | `test_dxf` | **Low** |
| Legacy `importSVG.py` (~1.5k lines) | read + several export regressions | `test_svg` | **Low-Medium** |
| Legacy `importDWG/OCA/AirfoilDAT` | Tests exist but **disabled** | (disabled) | **None (effective)** |
| `Draft.py` / `DraftGeomUtils.py` / `DraftVecUtils.py` shims | Import smoke only | `test_import` | **Low** |
| `WorkingPlane.py` | Indirect (objects placed on WP) | — | **Low** |

---

## 4. Gaps & Risks (prioritized)

1. **DXF import/export — highest risk.** `importDXF.py` is ~5,100 lines, is the
   most-used interop path with other CAD tools, and is covered by a single read
   fixture plus one export. Edge cases (blocks, splines, hatches, text styles,
   layers, units, malformed files) are untested. Regressions here directly break
   user data exchange.
2. **Disabled importer tests (DWG/OCA/AirfoilDAT).** Test code exists but is
   commented out in `TestDraft.py`, so these formats have **zero effective
   coverage** and silent rot risk. DWG in particular depends on an external
   converter (ODA/Teigha) and is fragile.
3. **`draftgeoutils/` geometry math.** Apollonius circles, circle inversion,
   intersections, offsets, fillets, and `sort_edges` are numerically delicate
   and almost entirely untested. Bugs here propagate into offset/array/fillet
   tools.
4. **GUI command layer (`draftguitools/`, 66 files).** The snapper, trackers,
   and edit framework — the most interaction-heavy and historically bug-prone
   code — have no behavioural tests beyond manual-input simulation. Hard to test
   but high user impact.
5. **View providers & task panels.** Display logic, dynamic property handling,
   and dialog wiring are untested; on-load migration of older documents (Proxy
   `onDocumentRestored`, property versioning) is a common regression source.
6. **`draftutils` (params/units/utils).** Foundational helpers used everywhere;
   a regression is broadly amplified yet only covered incidentally.
7. **Edge / failure paths.** Existing tests are largely happy-path "create then
   check it exists/recomputed". Degenerate input (zero-length wire, coincident
   points, self-intersecting offsets) is rarely asserted.

---

## 5. Recommendations

1. **Re-enable and repair the disabled suites** (DWG/OCA/AirfoilDAT) or
   explicitly skip with `@unittest.skipUnless(...)` guarding on the external
   converter, so the suite documents the gap instead of hiding it.
2. **Expand DXF coverage** with a small corpus of fixture files covering blocks,
   layers, splines, hatches, dimensions, text, and at least one malformed file;
   assert round-trip geometry counts and key properties. This is the single
   highest-value addition.
3. **Add focused `draftgeoutils` unit tests** (pure-math, fast, no document):
   intersections, offsets, fillets, sort_edges, circle constructions —
   property-based / numeric-tolerance assertions.
4. **Strengthen modification edge cases**: degenerate/closed/self-intersecting
   wires for offset, trim/extend boundaries, array with zero/negative counts.
5. **Add view-provider / document-restore tests** that save and reload a
   document built by `draft_test_objects.py` and assert all objects survive a
   round-trip (catches property-migration regressions cheaply).
6. **Add `draftutils` unit tests** for `units`, `params`, and `utils` parsing
   helpers (fast, no GUI).
7. **Track quantitative coverage** by enabling `coverage.py` over the Python
   suite in CI to turn these qualitative estimates into measured numbers.

---

## 6. Quick Stats

- Source files in scope: **≈ 220** Python files (≈ 205 in sub-packages + ~15
  legacy top-level), pure Python, no own C++ tests.
- Largest/riskiest file: `importDXF.py` (~5,119 lines).
- Test files: **19** in `drafttests/` (15 with test cases, 2 infra helpers,
  1 fixture `.dxf`, 1 `auxiliary.py`) + 2 entry modules (`TestDraft.py`,
  `TestDraftGui.py`).
- Test cases (`def test_`): **~119 total**, **~113 active** (6 disabled:
  DWG/OCA/Airfoil). Active ≈ 79 non-GUI + 34 GUI.
- Best-covered areas: object **creation** (`make_*`) and **modification**
  operations.
- Weakest areas: `draftgeoutils` geometry math, GUI command/snapper/edit layer,
  view providers, task panels, `draftutils`, and DWG/OCA/Airfoil import.
- Overall Draft coverage estimate: **Medium for the create/modify scripting
  core; Low overall** once the large import code, geometry utilities, and GUI
  layer are weighted in.
