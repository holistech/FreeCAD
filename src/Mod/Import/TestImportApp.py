# SPDX-License-Identifier: LGPL-2.1-or-later

# Headless round-trip tests for the CAD exchange formats (BREP / STEP / IGES /
# glTF). Pattern: build a known solid -> export -> import -> compare geometric
# invariants (volume, area, bounding box, centre of mass) within a tolerance
# appropriate to the format. BREP is exact; STEP is near-exact; IGES often drops
# the solid to a shell (so volume is unreliable -> assert area/bbox); glTF is
# tessellated (so only coarse bbox invariants hold).

import os
import tempfile
import unittest

import FreeCAD
import Part


class ImportExportRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.doc = FreeCAD.newDocument("ImportRoundTrip")
        self.tmp = tempfile.mkdtemp(prefix="fc_import_test_")

    def tearDown(self):
        FreeCAD.closeDocument(self.doc.Name)
        for name in os.listdir(self.tmp):
            try:
                os.remove(os.path.join(self.tmp, name))
            except OSError:
                pass
        os.rmdir(self.tmp)

    def _path(self, name):
        return os.path.join(self.tmp, name)

    def _assertSameGeometry(self, a, b, places=4):
        self.assertAlmostEqual(a.Volume, b.Volume, places=places)
        self.assertAlmostEqual(a.Area, b.Area, places=places)
        # BoundBox.Center is available on every shape type (CenterOfMass is only
        # defined on solids, which a re-imported shape may not be).
        ca, cb = a.BoundBox.Center, b.BoundBox.Center
        self.assertAlmostEqual(ca.x, cb.x, places=places)
        self.assertAlmostEqual(ca.y, cb.y, places=places)
        self.assertAlmostEqual(ca.z, cb.z, places=places)

    # --- BREP: lossless boundary representation -----------------------------
    def testBrepFileRoundTrip(self):
        box = Part.makeBox(10, 20, 30)
        path = self._path("box.brep")
        box.exportBrep(path)
        reimported = Part.Shape()
        reimported.importBrep(path)
        self._assertSameGeometry(box, reimported, places=5)

    def testBrepStringRoundTrip(self):
        cyl = Part.makeCylinder(5, 20)
        data = cyl.exportBrepToString()
        reimported = Part.Shape()
        reimported.importBrepFromString(data)
        self._assertSameGeometry(cyl, reimported, places=5)

    # --- STEP: near-exact NURBS exchange ------------------------------------
    def testStepBoxRoundTrip(self):
        box = Part.makeBox(10, 20, 30)
        path = self._path("box.step")
        box.exportStep(path)
        reimported = Part.read(path)
        self._assertSameGeometry(box, reimported, places=4)

    def testStepCylinderRoundTrip(self):
        cyl = Part.makeCylinder(5, 20)
        path = self._path("cyl.step")
        cyl.exportStep(path)
        reimported = Part.read(path)
        self.assertAlmostEqual(cyl.Volume, reimported.Volume, places=3)
        self.assertAlmostEqual(cyl.Area, reimported.Area, places=3)

    # --- IGES: surface exchange; solids may come back as shells -------------
    def testIgesRoundTripPreservesArea(self):
        box = Part.makeBox(10, 20, 30)
        path = self._path("box.iges")
        box.exportIges(path)
        reimported = Part.read(path)
        # IGES commonly degrades a solid to a shell, so volume is unreliable;
        # surface area and bounding box are the robust invariants.
        self.assertAlmostEqual(box.Area, reimported.Area, places=3)
        self.assertAlmostEqual(box.BoundBox.XLength, reimported.BoundBox.XLength, places=4)
        self.assertAlmostEqual(box.BoundBox.YLength, reimported.BoundBox.YLength, places=4)
        self.assertAlmostEqual(box.BoundBox.ZLength, reimported.BoundBox.ZLength, places=4)

    # --- glTF: export is headless; re-import needs the GUI import path -------
    def testGltfExportProducesFile(self):
        import Import

        box = Part.makeBox(10, 20, 30)
        feat = self.doc.addObject("Part::Feature", "Box")
        feat.Shape = box
        self.doc.recompute()
        path = self._path("box.glb")
        Import.export([feat], path)
        # The glTF writer runs headless and must emit a non-empty binary file.
        # (Headless re-import via Import.insert does not populate objects -- the
        # glTF reader is wired through the GUI import path -- so the round-trip
        # import is intentionally not asserted here.)
        self.assertTrue(os.path.exists(path), "glTF export produced no file")
        self.assertGreater(os.path.getsize(path), 0, "glTF export produced an empty file")

    # --- malformed input: clean failure, not a crash -----------------------
    def testMalformedStepRaises(self):
        path = self._path("broken.step")
        with open(path, "w") as f:
            f.write("this is not a valid STEP file\n")
        with self.assertRaises(Exception):
            Part.read(path)
