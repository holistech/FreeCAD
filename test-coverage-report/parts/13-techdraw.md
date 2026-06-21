# Test Coverage — TechDraw Workbench

Scope: `src/Mod/TechDraw/` (production source) and `tests/src/Mod/TechDraw/` (C++
GoogleTest). This report is a structural/qualitative assessment. No build or
execution was performed; coverage levels (None/Low/Medium/High) are estimated
from the ratio of tested code paths to the implemented source surface.

## 1. Source Surface

TechDraw is the 2D technical-drawing (drafting) workbench. It generates 2D
projections of 3D models via hidden-line-removal (HLR), places dimensions,
sections, hatches and annotations on a drawing page, and exports to SVG/DXF/PDF.

### App (algorithmic / document objects) — ~96 `.cpp`, ~68 `.h` (≈164 files)

- **Projection / HLR geometry (highest-risk core):**
  `GeometryObject.cpp/.h`, `Geometry.cpp/.h`, `GeometryMatcher.cpp/.h`,
  `ProjectionAlgos.cpp/.h`, `FeatureProjection.cpp/.h`, `EdgeWalker.cpp/.h`,
  `DrawProjectSplit.cpp/.h`. These wrap OpenCASCADE HLRBRep to convert a
  `TopoDS_Shape` into 2D visible/hidden edge sets, walk edges into closed faces,
  and match geometry across recomputes. This is the mathematical heart of the
  workbench.
- **DrawView* document objects:** `DrawView`, `DrawViewPart`,
  `DrawViewSection`, `DrawComplexSection`, `DrawViewDetail`, `DrawViewMulti`,
  `DrawViewCollection`, `DrawViewClip`, `DrawBrokenView`, `DrawViewArch`,
  `DrawViewDraft`, `DrawViewImage`, `DrawViewSymbol`, `DrawViewSpreadsheet`,
  `DrawViewAnnotation`, `DrawProjGroup`, `DrawProjGroupItem`.
- **Dimensions & annotations:** `DrawViewDimension`, `DrawViewDimExtent`,
  `DimensionGeometry`, `DimensionFormatter`, `DimensionAutoCorrect`,
  `DimensionReferences`, `LandmarkDimension`, `DrawViewBalloon`,
  `DrawLeaderLine`, `DrawRichAnno`, `DrawWeldSymbol`, `DrawTileWeld`,
  `DrawDimHelper`.
- **Cosmetic / overlay geometry:** `Cosmetic`, `CosmeticVertex`,
  `CosmeticEdge`, `CenterLine`, `CosmeticExtension`, `GeomFormat`,
  `LineFormat`, plus `PropertyCosmetic*List` / `PropertyGeomFormatList`.
- **Hatching:** `DrawHatch`, `DrawGeomHatch`, `PATPathMaker` (PAT pattern
  parsing).
- **Page / template / export:** `DrawPage`, `DrawTemplate`,
  `DrawSVGTemplate`, `DrawParametricTemplate`, `TechDrawExport.cpp` (DXF/SVG
  write), `DrawUtil` (shared math/string helpers).

### Gui (interaction / rendering) — ~145 `.cpp`, ~140 `.h` (≈285 files)

- ~60 `QGI*` QGraphics scene items (`QGIViewPart`, `QGIViewDimension`,
  `QGIViewSection`, `QGISVGTemplate`, `QGCustomSvg`, …) that render the App
  objects on the Qt scene; ~121 files match the `QG*` prefix.
- ~36 `ViewProvider*` classes; ~73 files relate to Task panels / dialogs
  (`TaskSectionView`, `TaskActiveView`, …).
- Commands: `Command*.cpp` (`CommandCreateDims`, `CommandAnnotate`,
  `CommandAlign`, `CommandDecorate`, `CommandExtensionDims/Pack`),
  `DimensionValidators`, `MDIViewPage`, `PagePrinter`, `PathBuilder`,
  preference dialogs (`DlgPrefsTechDraw*`).

Total production surface ≈ **450 files** (App + Gui).

## 2. Existing Tests

### C++ GoogleTest — `tests/src/Mod/TechDraw/App/`

| File | Fixture | Cases (TEST_F) | Purpose |
|------|---------|----------------|---------|
| `LineFormat.cpp` | `TestLineFormat` | 2 | `LineFormat::setQColor`/`getQColor` round-trip; verifies opaque colors stay opaque and that alpha is preserved through `QColor` ↔ `Base::Color` conversion. |

Build: `TechDraw_tests_run` executable (`CMakeLists.txt`), linked against the
`TechDraw` App library, gated by `BUILD_TECHDRAW`. **Total C++ cases: 2.**

### Python — registered via `Init.py` (`TestTechDrawApp`) and `InitGui.py` (`TestTechDrawGui`)

The two registered modules are thin import aggregators; the actual
`unittest.TestCase` classes live in `src/Mod/TechDraw/TDTest/`.

| Test module (TDTest) | Registered via | `def test*` | Purpose |
|----------------------|----------------|-------------|---------|
| `DrawViewPartTest` | App | 1 | Create a `DrawViewPart` from a box, recompute, assert 4 edges & "Up-to-date" (smoke test of HLR pipeline). |
| `DrawProjectionGroupTest` | App | 1 | Build a multi-view projection group, recompute, assert state. |
| `DrawHatchTest` | App | 1 | Apply a `DrawHatch` to a face, assert recompute success. |
| `DrawViewAnnotationTest` | App | 1 | Create an annotation view. |
| `DrawViewBalloonTest` | App | 1 | Create a balloon. |
| `DrawViewImageTest` | App | 1 | Embed an image view. |
| `DrawViewSymbolTest` | App | 2 | Symbol view incl. non-ASCII SVG symbol. |
| `DrawViewSectionTest` | Gui | 1 | Create a `DrawViewSection`, assert 4 edges & state. |
| `DrawViewDetailTest` | Gui | 1 | Create a detail view, assert recompute. |
| `DrawViewDimensionTest` | Gui | 2 | Length and radius dimensions, assert state. |

**Total Python cases: ~12** (App ≈8, Gui ≈4). `TDPyTest.py`,
`TechDrawTestUtilities.py`, `DLeaderRText.py` are helpers/fixtures, not
registered test cases. SVG/PNG assets (`TestHatch.svg`, `TestImage.png`,
`TestTemplate.svg`, …) back the import/symbol tests.

## 3. Coverage Map

| Source area | Files (approx) | Tests touching it | Est. coverage |
|-------------|---------------|-------------------|---------------|
| Projection / HLR geometry (GeometryObject, ProjectionAlgos, EdgeWalker, Matcher) | ~14 | Indirect smoke only (edge-count asserts in Part/Section tests) | **Low** |
| DrawViewPart / Section / Detail / ProjGroup | ~20 | 1 each, recompute + edge count | **Low** |
| Dimensions (geometry, formatter, auto-correct, references) | ~10 | Length+radius smoke (2) | **Low** |
| Cosmetic / CenterLine / GeomFormat / **LineFormat** | ~14 | LineFormat color round-trip (C++, 2); rest none | LineFormat **Medium**, others **None** |
| Hatch / GeomHatch / PAT | ~5 | 1 smoke | **Low** |
| Page / Template / SVG / DXF export (`TechDrawExport`) | ~12 | Symbol/template assets only; no export assertion | **None–Low** |
| Balloon / Leader / RichAnno / Weld / Tile | ~14 | Balloon (1), annotation (1) | **Low** |
| `DrawUtil` math/string helpers | ~2 | None (untested directly) | **None** |
| Gui (`QGI*`, ViewProviders, Task panels, Commands, printing) | ~285 | None (Gui tests exercise App objects, not rendering) | **None** |

## 4. Gaps & Risks (prioritized)

1. **HLR / projection geometry correctness (CRITICAL).** The HLR core
   (`GeometryObject`, `ProjectionAlgos`, `EdgeWalker`, `GeometryMatcher`,
   `DrawProjectSplit`) is the workbench's defining algorithm and its most
   regression-prone code (OpenCASCADE-version-sensitive). It is exercised only
   by smoke tests that assert an edge *count* (4 edges of a box) and an
   "Up-to-date" state — nothing checks edge geometry, visible/hidden
   classification, curve types, projection direction, or face walking. Silent
   wrong-geometry regressions would pass.
2. **No section/detail geometry assertions.** Section cutting and detail
   clipping (`DrawViewSection`, `DrawComplexSection`, `DrawViewDetail`) only
   check recompute success; cut-plane correctness, hatch placement and clip
   boundaries are untested. `DrawComplexSection` and `DrawBrokenView` have **no
   test at all**.
3. **Dimension value/formatting correctness.** Tests confirm a dimension object
   recomputes but never assert the measured value or the formatted string.
   `DimensionFormatter`, `DimensionAutoCorrect`, `DimensionGeometry` (angular,
   ordinate, arc-length, tolerances) are effectively untested logic.
4. **Export pipelines untested.** SVG/DXF/PDF generation (`TechDrawExport`,
   `DrawSVGTemplate`, `PagePrinter`) has no output verification — a corrupted
   export format would not be caught.
5. **`DrawUtil` helpers untested.** Shared numeric/string utilities used
   throughout have no direct unit tests, despite being pure and trivially
   testable.
6. **Entire Gui layer untested.** ~285 files (scene items, view providers,
   task panels, commands, validators) have zero automated coverage; the Gui
   test modules only construct App objects.
7. **Cosmetic geometry & PAT parsing** (`CenterLine`, `CosmeticEdge`,
   `PATPathMaker`) untested apart from LineFormat colors.

## 5. Recommendations

- **Add deterministic HLR golden tests:** project a known solid (e.g. a stepped
  block) and assert the count *and* coordinates/types of visible vs. hidden
  edges, plus projection direction. This is the single highest-value addition.
  Pure C++ tests against `GeometryObject`/`ProjectionAlgos` avoid Gui/threading.
- **Unit-test `DrawUtil` and `DimensionGeometry`/`DimensionFormatter`** at the
  C++ level — pure functions, fast wins, no document needed.
- **Assert dimension values and formatted strings** (linear, radial, angular,
  ordinate, tolerance/decimal formatting) in the Python tests rather than only
  recompute state.
- **Add `DrawComplexSection` and `DrawBrokenView` smoke + geometry tests**
  (currently zero coverage of these object types).
- **Add export round-trip checks:** export a page to SVG/DXF and assert key
  structural invariants (element counts, viewbox, presence of edges) rather than
  pixel/byte equality.
- **Expand the C++ suite beyond LineFormat:** `GeometryMatcher`, `EdgeWalker`,
  `Cosmetic*`, and `PATPathMaker` are good unit-test candidates.

## 6. Quick Stats

- Production files in scope: **≈450** (App ≈164, Gui ≈285).
- HLR/projection-geometry source files: **≈14** (the core risk area).
- C++ test files: **1** (`LineFormat.cpp`) — **2** `TEST_F` cases.
- Python test modules (registered, in `TDTest/`): **10 classes** — **≈12**
  `test*` methods.
- Total automated test cases in scope: **≈14**.
- Estimated overall coverage: **Low** — broad but shallow smoke coverage of App
  object creation/recompute; the safety-critical HLR geometry is unverified
  beyond edge counts; the Gui layer and export pipelines are essentially
  untested.
