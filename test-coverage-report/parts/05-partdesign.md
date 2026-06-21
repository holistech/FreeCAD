# Test Coverage — PartDesign Workbench

> Scope: `src/Mod/PartDesign/` (App + Gui) and C++ tests in
> `tests/src/Mod/PartDesign/`.
> Method: structural/qualitative review of source and test files only. No build
> was run; no coverage was measured. Coverage levels (None/Low/Medium/High) are
> estimates justified by which features have dedicated test cases.

---

## 1. Source Surface

PartDesign is one of the larger native workbenches. The module directory holds
~310 files across `App/`, `Gui/` and Python.

### App layer (`src/Mod/PartDesign/App/`, ~40 `.cpp` + headers)

The App layer contains the feature/document-object model and the actual geometry
computation. Key areas:

- **Body / Tip management**: `Body.cpp`, `BodyPyImp.cpp`, `Feature.cpp`,
  `FeatureBase.cpp`, `FeatureSolid.cpp` — the body container, the feature chain,
  base-feature and tip handling.
- **Sketch-based additive/subtractive features**: `FeatureSketchBased.cpp`,
  `FeatureAddSub.cpp`, `FeatureExtrude.cpp`, `FeaturePad.cpp`,
  `FeaturePocket.cpp`, `FeatureRevolution.cpp`, `FeatureRevolved.cpp`,
  `FeatureGroove.cpp`, `FeatureLoft.cpp`, `FeaturePipe.cpp` (sweep),
  `FeatureHelix.cpp`, `FeatureHole.cpp`.
- **Primitive features**: `FeaturePrimitive.cpp` (box, cylinder, sphere, cone,
  ellipsoid, prism, torus, wedge).
- **Dress-up features**: `FeatureDressUp.cpp`, `FeatureFillet.cpp`,
  `FeatureChamfer.cpp`, `FeatureDraft.cpp`, `FeatureThickness.cpp`.
- **Transformations**: `FeatureTransformed.cpp`, `FeatureMultiTransform.cpp`,
  `FeatureLinearPattern.cpp`, `FeaturePolarPattern.cpp`, `FeatureMirrored.cpp`,
  `FeatureScaled.cpp`.
- **Boolean**: `FeatureBoolean.cpp`.
- **Datum geometry**: `DatumPoint.cpp`, `DatumLine.cpp`, `DatumPlane.cpp`,
  `DatumCS.cpp`.
- **References / binders**: `ShapeBinder.cpp` (ShapeBinder + SubShapeBinder).
- **Misc**: `FeatureRefine.cpp`, `Measure.cpp`, Python bindings
  (`AppPartDesignPy.cpp`, `*PyImp.cpp`).

### Gui layer (`src/Mod/PartDesign/Gui/`, ~70 `.cpp` + headers + `.ui`)

Commands, task-panel dialogs and view providers. Largely interactive code:
`Command.cpp`, `CommandBody.cpp`, `CommandPrimitive.cpp`, a `Task*Parameters`
dialog per feature, `ViewProvider*` per feature, `ReferenceSelection.cpp`,
`SketchWorkflow.cpp`, `Utils.cpp`, `DlgActiveBody.cpp`. This layer is essentially
untested by automated tests (the GUI Python tests exercise the document/command
side, not the dialogs themselves).

---

## 2. Existing Tests

### C++ tests (GoogleTest, target `PartDesign_tests_run`, gated by `BUILD_PART_DESIGN`)

Located in `tests/src/Mod/PartDesign/App/`. **10 `TEST_F` cases** across 5 files,
plus binary `.FCStd` test models in `TestModels/`:

| File | Cases | Purpose |
|------|-------|---------|
| `BackwardCompatibility.cpp` | 4 | Open a v0.21 model; two-lengths Pad with expressions, cyclic expression, cross-object reference — migration / expression-engine regression on real `.FCStd` files. |
| `ShapeBinder.cpp` | 2 | ShapeBinder and SubShapeBinder object creation/existence. |
| `GeoFeatureGroupExtension.cpp` | 2 | Group accepts Boolean object; cross-group link-validity failure. |
| `Pad.cpp` | 1 | `TestMidPlaneTwoLength` — Pad with mid-plane + two lengths. |
| `DatumPlane.cpp` | 1 | Attaching a datum plane. |

The C++ suite is small and biased toward file-format/expression regressions and
object existence, not toward geometry-result verification.

### Python tests

Two registration entry points:
- `TestPartDesignApp` (registered in `src/Mod/PartDesign/Init.py`) imports 23
  test modules from the `PartDesignTests` package.
- `TestPartDesignGui` (registered in `src/Mod/PartDesign/InitGui.py`) imports the
  remaining modules (incl. `TestMaterial`, `TestActiveObject`) and adds its own
  GUI-level cases.

The real test bodies live in `src/Mod/PartDesign/PartDesignTests/`
(26 `Test*.py` files). **~182 `def test*` methods** in the package, plus **7** in
`TestPartDesignGui.py` → **~189 Python test methods total**.

Per-file `def test*` counts:

| Module | Cases | Focus |
|--------|------:|-------|
| `TestTopologicalNamingProblem.py` | 70 | TNP regressions across nearly every feature type — by far the dominant suite (133 KB). |
| `TestInvoluteGear.py` | 18 | Involute gear sketch macro + v0.20 fixtures. |
| `TestPad.py` | 10 | Pad variants (lengths, mid-plane, reversed, to-face, etc.). |
| `TestHelix.py` | 8 | Helix/spring parameters. |
| `TestHole.py` | 8 | Hole feature (counterbore, threads, etc.). |
| `TestPrimitive.py` | 8 | Primitive features. |
| `TestSuppressed.py` | 8 | Feature suppression behavior. |
| `TestLinearPattern.py` | 6 | Linear pattern. |
| `TestPolarPattern.py` | 6 | Polar pattern. |
| `TestLoft.py` | 5 | Loft. |
| `TestBoolean.py` | 4 | Boolean. |
| `TestPocket.py` | 4 | Pocket. |
| `TestShapeBinder.py` | 4 | Shape/Sub-shape binder. |
| `TestDatum.py` | 3 | Datum point/line/plane. |
| `TestFillet.py` | 3 | Fillet. |
| `TestMirrored.py` | 3 | Mirrored transformation. |
| `TestMultiTransform.py` | 3 | Multi-transform. |
| `TestPipe.py` | 2 | Pipe/sweep. |
| `TestRevolve.py` | 2 | Revolution. |
| `TestSketch.py` | 2 | Sketch on body/datum. |
| `TestActiveObject.py` | 1 | Active body/object tracking (GUI suite). |
| `TestChamfer.py` | 1 | Chamfer. |
| `TestDraft.py` | 1 | Draft. |
| `TestMaterial.py` | 1 | Material assignment (GUI suite). |
| `TestThickness.py` | 1 | Thickness. |
| `TestPartDesignGui.py` | 7 | Feature move/refuse-move, multi-transform, sketch creation, default colors of binders/datum. |

`Fixtures/` holds two `.FCStd` gear fixtures; `TestModels/` (C++) holds 4 `.FCStd`
regression models.

---

## 3. Coverage Map

| Component | C++ tests? | Python tests? | Est. coverage | Notes |
|-----------|:---------:|:-------------:|:-------------:|-------|
| Body / Tip / feature chain | Indirect | Indirect (TNP, move tests) | Medium | No dedicated Body unit test; exercised via feature/TNP/GUI move tests. |
| Base feature / migration | Yes (4) | Indirect (TNP) | Medium | BackwardCompatibility covers v0.21 open + expressions. |
| Pad / Extrude | Yes (1) | Yes (10) | High | Well covered both layers. |
| Pocket | No | Yes (4) | Medium-High | Good Python coverage. |
| Revolution / Groove | No | Yes (2 revolve) | Low-Medium | Groove has no dedicated test. |
| Loft | No | Yes (5) | Medium | |
| Sweep (Pipe) | No | Yes (2) | Low-Medium | Thin coverage for a complex feature. |
| Helix | No | Yes (8) | Medium-High | |
| Hole | No | Yes (8) | Medium-High | Threads/counterbore covered. |
| Primitives | No | Yes (8) | Medium | One test ~ per primitive type. |
| Fillet | No | Yes (3) | Medium | |
| Chamfer | No | Yes (1) | Low | Single case. |
| Draft | No | Yes (1) | Low | Single case. |
| Thickness | No | Yes (1) | Low | Single case. |
| Linear pattern | No | Yes (6) | Medium | |
| Polar pattern | No | Yes (6) | Medium | |
| Mirrored | No | Yes (3) | Medium | |
| MultiTransform | No | Yes (3) + GUI | Medium | |
| Scaled transform | No | Indirect | Low | No dedicated test module. |
| Boolean | No (only group-accept) | Yes (4) | Medium | |
| Datum (pt/line/plane/CS) | Yes (1 plane) | Yes (3) | Medium | DatumCS has no dedicated case. |
| ShapeBinder / SubShapeBinder | Yes (2) | Yes (4) | Medium-High | Both layers. |
| Suppression | No | Yes (8) | Medium-High | |
| Topological naming (TNP) | No | Yes (70) | High | Strongest area by volume. |
| Material assignment | No | Yes (1) | Low | |
| Active object/body | No | Yes (1) | Low | |
| Refine / Measure | No | No | None | Untested. |
| Gui: commands | No | Indirect (move/sketch) | Low | A few command paths only. |
| Gui: Task* dialogs (~25) | No | No | None | No automated dialog tests. |
| Gui: ViewProvider* (~25) | No | Partial (default colors) | Low | Only color defaults checked. |
| Involute gear macro | No | Yes (18) | High | Extra/utility, well covered. |

---

## 4. Gaps & Risks (prioritized)

1. **GUI layer almost entirely untested (High risk).** ~70 Gui `.cpp` files —
   the ~25 `Task*Parameters` dialogs, `ReferenceSelection`, `SketchWorkflow`,
   command logic and most `ViewProvider*` — have no automated tests beyond a few
   document-level command exercises and three "default color" checks. Regressions
   in task panels would not be caught.
2. **Thin dress-up coverage (Medium-High risk).** Chamfer, Draft and Thickness
   each have a single Python case. These are geometry-sensitive OCC operations
   prone to edge-selection / topological breakage.
3. **Sweep (Pipe) under-tested (Medium-High risk).** Only 2 cases for one of the
   most failure-prone features (multi-section, orientation, scaling, guide
   curves) — the `TaskPipeParameters`/orientation/scaling UI is uncovered.
4. **Groove, Scaled transform, DatumCS, Refine, Measure have no dedicated tests
   (Medium risk).** Groove and Scaled are covered only incidentally, if at all.
5. **C++ suite is shallow (Medium risk).** Only 10 cases, mostly object-existence
   and file/expression migration; little direct verification of computed shape
   geometry (volume, bounding box, face count) at the App level.
6. **Coverage is volume-skewed toward TNP.** 70 of ~182 package tests are TNP;
   functional feature-parameter coverage per feature is comparatively thin.
7. **Maintenance smell.** A commented-out `testBoxCase`/duplicate
   `PartDesignGuiTestCases` class remains in `TestPartDesignGui.py`; `TestHelix`
   is imported twice in `TestPartDesignApp.py` — minor but indicates drift.

---

## 5. Recommendations

1. Add headless GUI/command tests for the additive/subtractive command workflow
   (create body → sketch → pad/pocket → dress-up) to cover the largely untested
   Gui command and task-panel logic, even without exercising widgets directly.
2. Expand dress-up tests (Chamfer/Draft/Thickness) with multiple
   edge/face-selection and parameter variants, asserting resulting solid volume
   and face/edge counts.
3. Strengthen Sweep/Pipe tests: multi-section, orientation modes, scaling, and
   binormal/guide configurations.
4. Add dedicated modules for Groove, Scaled transform, DatumCS, Refine and
   Measure.
5. Grow the C++ App suite with geometry-assertion tests (volume / bounding box /
   topology counts) for Pad, Pocket, Revolution, Loft and patterns, complementing
   the existing migration/expression regressions.
6. Add a dedicated Body/Tip unit test (insert/move/remove feature, base-feature,
   tip relocation) at the App level rather than only via TNP/GUI.
7. Clean up dead/duplicated test code (commented class, double `TestHelix`
   import).

---

## 6. Quick Stats

- **Source files in scope**: ~310 total; App ~40 `.cpp`, Gui ~70 `.cpp`.
- **C++ tests**: 10 `TEST_F` across 5 files (`PartDesign_tests_run`,
  gated by `BUILD_PART_DESIGN`) + 4 `.FCStd` regression models.
- **Python tests**: ~189 `def test*` methods — ~182 in the `PartDesignTests`
  package (26 modules) + 7 in `TestPartDesignGui.py`.
  - Largest: `TestTopologicalNamingProblem.py` (70), `TestInvoluteGear.py` (18),
    `TestPad.py` (10).
- **Registration**: `Init.py` → `TestPartDesignApp`; `InitGui.py` →
  `TestPartDesignGui`.
- **Best-covered**: Pad, TNP, Hole, Helix, suppression, involute-gear macro.
- **Worst-covered**: entire Gui task-panel/dialog layer, dress-up features,
  Sweep, Groove/Scaled/DatumCS/Refine/Measure.
- **Overall estimate**: App/feature model **Medium**; topological-naming
  robustness **High**; GUI layer **Low/None**.
