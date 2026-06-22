# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2002 Jürgen Riegel <juergen.riegel@web.de>              *
# *   Copyright (c) 2025 Frank Martínez <mnesarco at gmail dot com>         *
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
# ***************************************************************************/

# FreeCAD init module - Tests
#
# Gathering all the information to start FreeCAD.
# This is the third of four init scripts:
# +------+------------------+-----------------------------+
# | This | Script           | Runs                        |
# +------+------------------+-----------------------------+
# |      | CMakeVariables   | always                      |
# |      | FreeCADInit      | always                      |
# | >>>> | FreeCADTest      | only if test and not Gui    |
# |      | FreeCADGuiInit   | only if Gui is up           |
# +------+------------------+-----------------------------+

# Testing the function of the base system and run
# (if existing) the test function of the modules

import FreeCAD
import typing

if typing.TYPE_CHECKING:
    from __main__ import Log

Log("FreeCAD test running...\n\n")
Log("Init: starting App::FreeCADTest.py\n")
Log("░░░▀█▀░█▀█░▀█▀░▀█▀░░░▀█▀░█▀▀░█▀▀░▀█▀░█▀▀░░░\n")
Log("░░░░█░░█░█░░█░░░█░░░░░█░░█▀░░▀▀█░░█░░▀▀█░░░\n")
Log("░░░▀▀▀░▀░▀░▀▀▀░░▀░░░░░▀░░▀▀▀░▀▀▀░░▀░░▀▀▀░░░\n")

import os
import sys
import TestApp

# Optional Python line-coverage measurement of the embedded test run. Enabled
# only when FREECAD_PYTHON_COVERAGE is set, so the normal test run is unaffected
# and the 'coverage' package stays an optional dependency.
_cov = None
if os.environ.get("FREECAD_PYTHON_COVERAGE"):
    try:
        import coverage

        _cov = coverage.Coverage(data_file=os.environ.get("COVERAGE_FILE") or ".coverage")
        _cov.start()
        Log("Python coverage measurement enabled\n")
    except ImportError:
        Log("FREECAD_PYTHON_COVERAGE set but the 'coverage' package is not installed\n")

testResult = TestApp.RunConfiguredTextTest()

if _cov is not None:
    import io

    _cov.stop()
    _cov.save()
    Log("Python coverage data saved to {}\n".format(_cov.config.data_file))
    try:
        # Suppress the per-file table; surface only the headline percentage.
        total = _cov.report(file=io.StringIO())
        Log("Total Python line coverage: {:.2f}%\n".format(total))
    except Exception as exc:  # noqa: BLE001 - reporting must never fail the run
        Log("Python coverage report failed: {}\n".format(exc))

Log("FreeCAD test done\n")

sys.exit(0 if testResult.wasSuccessful() else 1)
