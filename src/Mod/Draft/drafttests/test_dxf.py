# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2013 Yorik van Havre <yorik@uncreated.net>              *
# *   Copyright (c) 2019 Eliud Cabrera Castillo <e.cabrera-castillo@tum.de> *
# *   Copyright (c) 2025 FreeCAD Project Association                        *
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
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""Unit tests for the Draft Workbench, DXF import and export tests."""

## @package test_dxf
# \ingroup drafttests
# \brief Unit tests for the Draft Workbench, DXF import and export tests.

## \addtogroup drafttests
# @{

import os
import tempfile

import FreeCAD as App
import Draft
from drafttests import auxiliary as aux
from drafttests import test_base
from draftutils.messages import _msg
import importDXF


class DraftDXF(test_base.DraftTestCaseDoc):
    """Test reading and writing of DXF files with Draft."""

    def test_read_dxf_Issue24314(self):
        """Verify that reading a DXF file does not leave pending Python error states"""

        file = "Mod/Draft/drafttests/Issue24314.dxf"
        in_file = os.path.join(App.getHomePath(), file)
        _msg("  file={}".format(in_file))
        _msg("  exists={}".format(os.path.exists(in_file)))

        hGrp = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")

        # Set options, doing our best to restore them:
        wasShowDialog = hGrp.GetBool("dxfShowDialog", True)
        wasUseLegacyImporter = hGrp.GetBool("dxfUseLegacyImporter", False)
        wasUseLayers = hGrp.GetBool("dxfUseDraftVisGroups", True)
        wasImportMode = hGrp.GetInt("DxfImportMode", 2)
        wasCreateSketch = hGrp.GetBool("dxfCreateSketch", False)
        wasImportAnonymousBlocks = hGrp.GetBool("dxfstarblocks", False)

        doc = None
        try:
            # disable Preferences dialog in gui mode (avoids popup prompt to user)
            hGrp.SetBool("dxfShowDialog", False)
            # Use the new C++ importer -- that's where the bug was
            hGrp.SetBool("dxfUseLegacyImporter", False)
            # Preserve the DXF layers (makes the checking of document contents easier)
            hGrp.SetBool("dxfUseDraftVisGroups", True)
            # create simple part shapes (2 params)
            # This is required to display the bug because creation of Draft objects clears out the
            # pending exception this test is looking for, whereas creation of the simple shape object
            # actually throws on the pending exception so the entity is absent from the document.
            hGrp.SetInt("DxfImportMode", 2)
            hGrp.SetBool("dxfCreateSketch", False)
            hGrp.SetBool("dxfstarblocks", False)
            doc = importDXF.open(in_file)
            # This doc should have 3 objects: The Layers container, the DXF layer called 0, and one Line
            self.assertEqual(len(doc.Objects), 3)
        finally:
            hGrp.SetBool("dxfShowDialog", wasShowDialog)
            hGrp.SetBool("dxfUseLegacyImporter", wasUseLegacyImporter)
            hGrp.SetBool("dxfUseDraftVisGroups", wasUseLayers)
            hGrp.SetInt("DxfImportMode", wasImportMode)
            hGrp.SetBool("dxfCreateSketch", wasCreateSketch)
            hGrp.SetBool("dxfstarblocks", wasImportAnonymousBlocks)
            if doc:
                App.closeDocument(doc.Name)

    def _set_native_backend(self):
        """Force the built-in C++ DXF importer/exporter (no download, headless)
        and return a restore callback."""
        hGrp = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")
        saved = {
            "dxfShowDialog": hGrp.GetBool("dxfShowDialog", True),
            "dxfUseLegacyImporter": hGrp.GetBool("dxfUseLegacyImporter", False),
            "dxfUseLegacyExporter": hGrp.GetBool("dxfUseLegacyExporter", False),
            "dxfUseDraftVisGroups": hGrp.GetBool("dxfUseDraftVisGroups", True),
            "DxfImportMode": hGrp.GetInt("DxfImportMode", 2),
        }
        hGrp.SetBool("dxfShowDialog", False)
        hGrp.SetBool("dxfUseLegacyImporter", False)
        hGrp.SetBool("dxfUseLegacyExporter", False)
        hGrp.SetBool("dxfUseDraftVisGroups", True)
        hGrp.SetInt("DxfImportMode", 2)

        def restore():
            hGrp.SetBool("dxfShowDialog", saved["dxfShowDialog"])
            hGrp.SetBool("dxfUseLegacyImporter", saved["dxfUseLegacyImporter"])
            hGrp.SetBool("dxfUseLegacyExporter", saved["dxfUseLegacyExporter"])
            hGrp.SetBool("dxfUseDraftVisGroups", saved["dxfUseDraftVisGroups"])
            hGrp.SetInt("DxfImportMode", saved["DxfImportMode"])

        return restore

    @staticmethod
    def _edges(doc):
        edges = []
        for o in doc.Objects:
            shape = getattr(o, "Shape", None)
            if shape is not None and not shape.isNull():
                edges.extend(shape.Edges)
        return edges

    def test_dxf_export_import_roundtrip(self):
        """Export a line and a circle to DXF and re-import them, checking the
        geometry survives the round-trip (replaces the old export stub)."""
        import math

        _msg("  Test 'DXF export/import round-trip'")
        restore = self._set_native_backend()
        out_file = os.path.join(tempfile.mkdtemp(prefix="fc_dxf_"), "roundtrip.dxf")
        newdoc = None
        try:
            line = Draft.makeLine(App.Vector(0, 0, 0), App.Vector(10, 0, 0))
            circle = Draft.makeCircle(5.0)
            self.doc.recompute()
            importDXF.export([line, circle], out_file)
            self.assertGreater(os.path.getsize(out_file), 0, "DXF export produced an empty file")

            newdoc = importDXF.open(out_file)
            edges = self._edges(newdoc)
            self.assertEqual(len(edges), 2, "expected one line edge and one circle edge")
            lengths = sorted(e.Length for e in edges)
            self.assertAlmostEqual(lengths[0], 10.0, delta=0.1)  # line segment
            self.assertAlmostEqual(lengths[1], 2 * math.pi * 5.0, delta=0.5)  # circle perimeter
        finally:
            restore()
            if newdoc:
                App.closeDocument(newdoc.Name)

    def test_dxf_polyline_roundtrip(self):
        """A multi-segment open wire round-trips through DXF preserving its total
        edge length."""
        _msg("  Test 'DXF polyline round-trip'")
        restore = self._set_native_backend()
        out_file = os.path.join(tempfile.mkdtemp(prefix="fc_dxf_"), "wire.dxf")
        newdoc = None
        try:
            pts = [App.Vector(0, 0, 0), App.Vector(10, 0, 0), App.Vector(10, 10, 0)]
            wire = Draft.makeWire(pts, closed=False)
            self.doc.recompute()
            importDXF.export([wire], out_file)

            newdoc = importDXF.open(out_file)
            edges = self._edges(newdoc)
            self.assertGreater(len(edges), 0, "polyline produced no edges")
            total = sum(e.Length for e in edges)
            self.assertAlmostEqual(total, 20.0, delta=0.2)  # 10 + 10
        finally:
            restore()
            if newdoc:
                App.closeDocument(newdoc.Name)


## @}
