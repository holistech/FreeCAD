# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2026 FreeCAD Project Association                        *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""Unit tests for the Measure scripting API.

Exercises all measurement document objects on a 10x10x10 box and a
r=3 h=20 cylinder, plus the legacy ``Measurement`` helper class. Expected
values are computed by hand from the geometry.
"""

import math
import unittest

import FreeCAD
import Part
import Measure


class MeasureObjectTest(unittest.TestCase):
    def setUp(self):
        self.doc = FreeCAD.newDocument("MeasureTest")
        self.box = self.doc.addObject("Part::Feature", "Box")
        self.box.Shape = Part.makeBox(10, 10, 10)
        self.cyl = self.doc.addObject("Part::Feature", "Cyl")
        self.cyl.Shape = Part.makeCylinder(3, 20)
        self.doc.recompute()

    def tearDown(self):
        FreeCAD.closeDocument(self.doc.Name)

    def testDistance(self):
        m = self.doc.addObject("Measure::MeasureDistance", "D")
        m.Element1 = (self.box, ["Vertex1"])
        m.Element2 = (self.box, ["Vertex8"])
        self.doc.recompute()
        # opposite corners of the cube: space diagonal sqrt(3) * 10
        self.assertAlmostEqual(m.Distance.Value, math.sqrt(300.0), places=5)

    def testArea(self):
        m = self.doc.addObject("Measure::MeasureArea", "A")
        m.Elements = [(self.box, "Face1")]
        self.doc.recompute()
        self.assertAlmostEqual(m.Area.Value, 100.0, places=5)

    def testLength(self):
        m = self.doc.addObject("Measure::MeasureLength", "L")
        m.Elements = [(self.box, "Edge1")]
        self.doc.recompute()
        self.assertAlmostEqual(m.Length.Value, 10.0, places=5)

    def testAngle(self):
        m = self.doc.addObject("Measure::MeasureAngle", "Ang")
        m.Element1 = (self.box, ["Face1"])
        m.Element2 = (self.box, ["Face3"])
        self.doc.recompute()
        self.assertAlmostEqual(m.Angle.Value, 90.0, places=5)

    def testRadius(self):
        m = self.doc.addObject("Measure::MeasureRadius", "R")
        m.Element = (self.cyl, ["Face1"])
        self.doc.recompute()
        self.assertAlmostEqual(m.Radius.Value, 3.0, places=5)

    def testDiameter(self):
        m = self.doc.addObject("Measure::MeasureDiameter", "Di")
        m.Element = (self.cyl, ["Face1"])
        self.doc.recompute()
        self.assertAlmostEqual(m.Diameter.Value, 6.0, places=5)

    def testPosition(self):
        m = self.doc.addObject("Measure::MeasurePosition", "P")
        m.Element = (self.box, ["Vertex1"])
        self.doc.recompute()
        pos = m.Position
        for coord in (pos.x, pos.y, pos.z):
            self.assertTrue(
                abs(coord) < 1e-6 or abs(coord - 10.0) < 1e-6,
                "{} is not a box corner".format(coord),
            )


class LegacyMeasurementTest(unittest.TestCase):
    def setUp(self):
        self.doc = FreeCAD.newDocument("LegacyMeasureTest")
        self.box = self.doc.addObject("Part::Feature", "Box")
        self.box.Shape = Part.makeBox(10, 10, 10)
        self.cyl = self.doc.addObject("Part::Feature", "Cyl")
        self.cyl.Shape = Part.makeCylinder(3, 20)
        self.doc.recompute()

    def tearDown(self):
        FreeCAD.closeDocument(self.doc.Name)

    def testVertexDistance(self):
        m = Measure.Measurement()
        m.addReference3D(self.box.Name, "Vertex1")
        m.addReference3D(self.box.Name, "Vertex8")
        self.assertTrue(m.has3DReferences())
        self.assertAlmostEqual(m.length(), math.sqrt(300.0), places=5)

    def testCylinderRadius(self):
        m = Measure.Measurement()
        m.addReference3D(self.cyl.Name, "Edge1")
        self.assertAlmostEqual(m.radius(), 3.0, places=5)


if __name__ == "__main__":
    unittest.main()
