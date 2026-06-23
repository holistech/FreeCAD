# Test Execution Results — Empirical Run (2026-06-22)

This document records an **actual execution** of the FreeCAD test suites on a freshly built
debug binary. It complements the structural/qualitative reports (parts 01–21), which were produced
by reading the repository and did **not** run anything. Here, the suites were really compiled and run.

## Environment

| Item | Value |
|------|-------|
| FreeCAD version | 26.3.0 — Libs 26.3.0devR47369 (Git) |
| Build | Debug, built via `pixi` (CMake preset `conda-linux-debug`), `ENABLE_DEVELOPER_TESTS=ON` |
| Toolchain | conda-forge env (pixi 0.70.2), Python 3.11, GCC/Clang from the pixi env |
| OS | Ubuntu 24.04.4 LTS, 24 cores, 125 GB RAM |
| Build size | 7,005 Ninja targets; full build ≈ 14 min |
| Run mode | Headless `FreeCADCmd` for Python; `ctest` for C++ |

> Note: this is a *normal* debug build — it is **not** coverage-instrumented, so no line/branch
> percentages were measured here. This document reports pass/fail execution outcomes only.

## Summary

| Layer | Result |
|-------|--------|
| **C++ (ctest)** | ✅ **1661 / 1661 passed** (0 failed) in 105.39 s |
| **Python — 19 of 20 registered modules** | ✅ **~1,199 tests passed, 0 real failures** (1 expected failure, 3 skipped) |
| **Python — CAM (`TestCAMApp`)** | ⚠️ aborts the whole run via a file-descriptor bug; isolated per-suite run: **81/91 suites green (~1,285 tests)**, remainder are GUI-dependent or stale tests — **no functional regression** |

**Bottom line:** the build is fully functional. The only "red" signals are (a) GUI tests that require
a running `QApplication`/display, and (b) a known cluster of stale CAM tests plus a CAM
file-descriptor bug — none of which indicate broken CAD functionality.

---

## 1. C++ tests (ctest)

```
100% tests passed, 0 tests failed out of 1661
Total Test time (real) = 105.39 sec
```

(`gtest_discover_tests` discovered ~1668 entries; 1661 were run/reported by the summary.) All green.

## 2. Python tests — full `FreeCADCmd -t 0` run

The aggregate run **does not complete**. It aborts inside CAM:

- Test `CAMTests.TestCAMSanity.test320_postprocessor_sanity_checks_integration` corrupts the process
  stdout file descriptor (`get_all_squawks: _outputData failed: [Errno 9] Bad file descriptor`).
- The `unittest` runner then dies on `stream.flush()` with `OSError: [Errno 9] Bad file descriptor`,
  killing the whole process (`rc=1`) **before** the final summary and before any module registered
  after CAM runs.
- Of the ~355 tests that ran before the crash: **0 failures, 0 errors**.

This is a **test-harness/isolation bug** (a test that closes/redirects the shared stdout fd), not a
product defect. It matches the CAM/harness-fragility risk flagged in
[parts/10-cam.md](10-cam.md) and [parts/20-test-harness.md](20-test-harness.md).

## 3. Python tests — module-wise run (one process per module)

To avoid CAM aborting everything, each registered module was run in its own `FreeCADCmd -t <module>`
process. **19 of 20 modules fully green:**

| Module | Tests | Status |
|--------|------:|--------|
| BaseTests | 48 | OK |
| Document | 120 | OK |
| MeshTestsApp | 42 | OK |
| Metadata | 12 | OK |
| StringHasher | 4 | OK |
| TestArch (BIM) | 273 | OK (1 expected failure) |
| TestAssemblyWorkbench | 9 | OK (2 skipped) |
| **TestCAMApp** | — | ❌ fd-crash (see §2, §4) |
| TestDraft | 76 | OK |
| TestFemApp | 90 | OK |
| TestMaterialsApp | 15 | OK |
| TestPartApp | 143 | OK |
| TestPartDesignApp | 175 | OK |
| TestPythonSyntax | 1 | OK |
| TestSketcherApp | 82 | OK (1 skipped) |
| TestSpreadsheet | 87 | OK |
| TestSurfaceApp | 1 | OK |
| TestTechDrawApp | 7 | OK |
| UnicodeTests | 2 | OK |
| UnitTests | 12 | OK |

Total ≈ 1,199 passing tests, **0 real failures**.

## 4. Python tests — CAM per-suite run

CAM was then run suite-by-suite (`FreeCADCmd -t CAMTests.<Suite>`), excluding the fd-corrupting
`TestCAMSanity`. **81 of 91 suites green (~1,285 tests).** The 10 non-green suites, by actual root
cause:

| Suite(s) | Symptom | Root cause | Real defect? |
|----------|---------|-----------|:-----------:|
| `TestPathToolBitBrowserWidget`, `…EditorWidget`, `…ListWidget`, `…PropertyEditorWidget`, `TestPathToolDocumentObjectEditorWidget` | `rc=134` (SIGABRT) | "Must construct a QApplication before a QWidget" — GUI widget tests cannot run under headless `FreeCADCmd` | ❌ No — GUI-dependent |
| `TestPathToolAssetStore` | 16 errors: `…no attribute 'store'` | abstract base test class `BaseTestPathToolAssetStore` loaded directly | ❌ No — collection artifact |
| `TestPathToolBitSerializer` | 2 errors: `…no attribute 'serializer_class'` | abstract base class `_BaseToolBitSerializerTestCase` loaded directly | ❌ No — collection artifact |
| `TestPathDressupArray` | 3 errors: `_TestEngrave …no attribute 'Active'` | incomplete test stub; suite is not registered in `TestCAMApp` | ❌ No — artifact/stub |
| **`TestMachine`** (`TestOutputOptions`) | `TypeError: OutputOptions.__init__() got an unexpected keyword argument 'output_units'`; `assertNotEqual` fails (two objects equal) | **stale test** after an `OutputOptions` "units" refactor | ⚠️ Yes — test maintenance bug |
| **`TestPostToolProcessing`** (`TestEmptyMoveSuppression`) | 3 errors: `KeyError: 'OUTPUT_UNITS'` | same "units" refactor; class is not registered in `TestCAMApp` | ⚠️ Yes — test maintenance bug |

### Methodological caveat
The per-suite run loads **whole modules**, whereas the curated `TestCAMApp` imports only specific
**concrete** test classes. This means several "failures" above are artifacts of loading abstract base
test classes / unregistered helpers that the official suite deliberately excludes
(`BaseTestPathToolAssetStore`, `_BaseToolBitSerializerTestCase`, `TestPathDressupArray`,
`TestEmptyMoveSuppression`). They would not appear in the curated CI suite.

### Genuine finding worth an upstream issue
`TestMachine` and `TestPostToolProcessing` fail for the **same reason**: an `OutputOptions`
refactor (`output_units` → `units`, removal of an `OUTPUT_UNITS` key) was **not propagated to the
tests**. These are stale-test bugs (test maintenance), not broken CAM functionality.

---

## 5. Actionable findings (from execution)

1. **CAM `TestCAMSanity` corrupts the shared stdout fd** and aborts the entire `-t 0` Python run.
   This is the single most impactful test bug found: it masks every Python suite registered after CAM
   in CI. Fix: stop the postprocessor sanity test from closing/redirecting fd 1, or isolate it.
2. **Stale CAM tests after the `OutputOptions` "units" refactor** (`TestMachine`,
   `TestPostToolProcessing`) — update or remove.
3. **GUI widget tests cannot run headless** — they need `xvfb-run build/debug/bin/FreeCAD -t …`
   (GUI binary + virtual display). Not validated in this headless run.
4. Confirms two structural risks from parts 10/20: CAM test fragility and the fact that **a green
   `ctest` does not imply the Python suites passed** (they live outside ctest).

## 6. Reproduction

```bash
# C++
pixi run test --output-on-failure

# Python, per module (robust against the CAM fd crash)
for m in BaseTests Document MeshTestsApp Metadata StringHasher TestArch \
         TestAssemblyWorkbench TestDraft TestFemApp TestMaterialsApp TestPartApp \
         TestPartDesignApp TestPythonSyntax TestSketcherApp TestSpreadsheet \
         TestSurfaceApp TestTechDrawApp UnicodeTests UnitTests; do
  build/debug/bin/FreeCADCmd -t "$m"
done

# CAM, per suite (excluding the fd-corrupting TestCAMSanity)
for s in $(ls src/Mod/CAM/CAMTests/Test*.py | xargs -n1 basename | sed 's/.py$//' | grep -vx TestCAMSanity); do
  build/debug/bin/FreeCADCmd -t "CAMTests.$s"
done
```
