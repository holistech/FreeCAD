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

"""Unit tests for the Inspection module.

The deviation (distance-to-reference) computation of ``Inspection::Feature``
runs headless on ``recompute()``: it samples points off the Actual shape and
stores their signed distance to the Nominal in the ``Distances`` property. The
expected deviations below are computed by hand from the geometry.
"""

import unittest

import FreeCAD
import Part
import Inspection


class InspectionDeviationTest(unittest.TestCase):
    def setUp(self):
        self.doc = FreeCAD.newDocument("InspectionTest")

    def tearDown(self):
        FreeCAD.closeDocument(self.doc.Name)

    def _make_box(self, name, placement=None):
        box = self.doc.addObject("Part::Box", name)
        box.Length = box.Width = box.Height = 10.0
        if placement is not None:
            box.Placement = placement
        return box

    def testIdenticalShapesZeroDeviation(self):
        """Two coincident identical boxes have zero deviation everywhere."""
        actual = self._make_box("Actual")
        nominal = self._make_box("Nominal")
        self.doc.recompute()

        feat = self.doc.addObject("Inspection::Feature", "Insp")
        feat.Actual = actual
        feat.Nominals = [nominal]
        feat.SearchRadius = 100.0
        self.doc.recompute()

        distances = list(feat.Distances)
        self.assertEqual(len(distances), 8)  # the 8 box vertices
        for d in distances:
            self.assertAlmostEqual(d, 0.0, places=5)

    def testKnownOffsetDeviation(self):
        """A nominal shifted +1 mm in Z yields a 1 mm max deviation."""
        actual = self._make_box("Actual")
        nominal = self._make_box(
            "Nominal",
            FreeCAD.Placement(FreeCAD.Vector(0, 0, 1), FreeCAD.Rotation()),
        )
        self.doc.recompute()

        feat = self.doc.addObject("Inspection::Feature", "Insp")
        feat.Actual = actual
        feat.Nominals = [nominal]
        feat.SearchRadius = 100.0
        self.doc.recompute()

        distances = [abs(d) for d in feat.Distances]
        self.assertEqual(len(distances), 8)
        # The bottom four vertices are 1 mm below the shifted nominal;
        # the top four fall inside the nominal solid (distance ~0).
        self.assertAlmostEqual(max(distances), 1.0, places=4)
        self.assertAlmostEqual(min(distances), 0.0, places=4)

    def testGroupCreation(self):
        """An Inspection::Group is a valid headless document object."""
        group = self.doc.addObject("Inspection::Group", "InspGroup")
        self.assertEqual(group.TypeId, "Inspection::Group")


if __name__ == "__main__":
    unittest.main()
