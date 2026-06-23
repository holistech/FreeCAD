# SPDX-License-Identifier: LGPL-2.1-or-later

# Data-exchange tests for the Spreadsheet workbench: CSV import/export round-trips,
# a minimal XLSX import, and an FCStd persistence round-trip. CSV import/export was
# completely untested before.

import os
import tempfile
import zipfile
import unittest

import FreeCAD


class SpreadsheetExchangeTest(unittest.TestCase):
    def setUp(self):
        self.doc = FreeCAD.newDocument("SpreadsheetExchange")
        self.tmp = tempfile.mkdtemp(prefix="fc_sheet_")

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

    def _sheet(self, name="Sheet"):
        return self.doc.addObject("Spreadsheet::Sheet", name)

    # --- CSV round-trips ----------------------------------------------------
    def testCsvRoundTripTabDelimiter(self):
        s = self._sheet()
        cells = {"A1": "1", "B1": "2", "A2": "foo", "B2": "bar"}
        for addr, val in cells.items():
            s.set(addr, val)
        self.doc.recompute()
        path = self._path("data.csv")
        s.exportFile(path)  # default delimiter is tab

        s2 = self._sheet("Sheet2")
        s2.importFile(path)
        self.doc.recompute()
        self.assertEqual(s2.get("A1"), s.get("A1"))
        self.assertEqual(s2.get("B2"), s.get("B2"))
        self.assertEqual(s2.get("A2"), "foo")

    def testCsvRoundTripCommaDelimiter(self):
        s = self._sheet()
        s.set("A1", "10")
        s.set("B1", "20")
        s.set("C1", "hello")
        self.doc.recompute()
        path = self._path("data_comma.csv")
        s.exportFile(path, ",")

        s2 = self._sheet("Sheet2")
        s2.importFile(path, ",")
        self.doc.recompute()
        self.assertEqual(s2.get("A1"), s.get("A1"))
        self.assertEqual(s2.get("C1"), "hello")

    def testCsvExportsFormulaResultNotFormula(self):
        s = self._sheet()
        s.set("A1", "2")
        s.set("A2", "=A1 * 3")
        self.doc.recompute()
        self.assertEqual(s.get("A2"), 6)
        path = self._path("formula.csv")
        s.exportFile(path)

        s2 = self._sheet("Sheet2")
        s2.importFile(path)
        self.doc.recompute()
        # CSV export writes the evaluated value, so the re-imported cell holds 6,
        # not the formula text.
        self.assertEqual(s2.getContents("A2"), "6")

    # --- minimal XLSX import ------------------------------------------------
    def _writeMinimalXlsx(self, path):
        workbook = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>'
            '<definedName name="myalias">Sheet1!$A$1</definedName>'
            "</workbook>"
        )
        rels = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/>'
            "</Relationships>"
        )
        shared = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="1" uniqueCount="1">'
            "<si><t>world</t></si></sst>"
        )
        sheet = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
            '<row r="1">'
            '<c r="A1" t="n"><v>42</v></c>'
            '<c r="B1" t="inlineStr"><is><t>hello</t></is></c>'
            '<c r="C1" t="s"><v>0</v></c>'
            "</row>"
            "</sheetData></worksheet>"
        )
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("xl/workbook.xml", workbook)
            z.writestr("xl/_rels/workbook.xml.rels", rels)
            z.writestr("xl/sharedStrings.xml", shared)
            z.writestr("xl/worksheets/sheet1.xml", sheet)

    def testXlsxImport(self):
        import importXLSX

        path = self._path("book.xlsx")
        self._writeMinimalXlsx(path)
        doc = importXLSX.open(path)
        try:
            sheets = [o for o in doc.Objects if o.TypeId == "Spreadsheet::Sheet"]
            self.assertEqual(len(sheets), 1)
            sheet = sheets[0]
            self.assertEqual(sheet.get("A1"), 42)
            self.assertEqual(sheet.get("B1"), "hello")
            self.assertEqual(sheet.get("C1"), "world")
            self.assertEqual(sheet.getAlias("A1"), "myalias")
        finally:
            FreeCAD.closeDocument(doc.Name)

    # --- FCStd persistence --------------------------------------------------
    def testPersistenceRoundTrip(self):
        s = self._sheet()
        s.set("A1", "3")
        s.set("A2", "=A1 * 7")
        s.setAlias("A1", "seed")
        self.doc.recompute()
        path = self._path("sheet.FCStd")
        self.doc.saveAs(path)
        name = self.doc.Name
        FreeCAD.closeDocument(name)

        reopened = FreeCAD.openDocument(path)
        try:
            sheet = [o for o in reopened.Objects if o.TypeId == "Spreadsheet::Sheet"][0]
            self.assertEqual(sheet.get("A2"), 21)
            self.assertEqual(sheet.getAlias("A1"), "seed")
        finally:
            # restore an empty doc so tearDown's closeDocument has a target
            self.doc = FreeCAD.newDocument("SpreadsheetExchange")
            FreeCAD.closeDocument(reopened.Name)
