# ***************************************************************************
# *   Copyright (c) 2002 Juergen Riegel <juergen.riegel@web.de>             *
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
# ***************************************************************************/

import FreeCAD
import os
import sys
import unittest

# ---------------------------------------------------------------------------
# define the functions to test the FreeCAD base code
# ---------------------------------------------------------------------------


def tryLoadingTest(testName):
    "Loads and returns testName, or a failing TestCase if unsuccessful."

    try:
        return unittest.defaultTestLoader.loadTestsFromName(testName)

    # Catch any error raised while importing/loading a registered test module, not just
    # ImportError. A module that fails to load for any reason (e.g. a syntax or attribute
    # error at import time) must surface as a reported test failure rather than aborting
    # the construction of the whole suite, which would silently drop every other test.
    except Exception as loadError:

        class LoadFailed(unittest.TestCase):
            def __init__(self, testName):
                # setattr() first, because TestCase ctor checks for methodName.
                setattr(self, "failed_to_load_" + testName, self._runTest)
                super(LoadFailed, self).__init__("failed_to_load_" + testName)
                self.testName = testName

            def __name__(self):
                return "Loading " + self.testName

            def _runTest(self):
                self.fail("Couldn't load {}: {}".format(self.testName, loadError))

        return LoadFailed(testName)


def All():
    # Registered tests
    tests = FreeCAD.__unit_test__

    suite = unittest.TestSuite()

    for test in tests:
        suite.addTest(tryLoadingTest(test))

    return suite


def PrintAll():
    # Registered tests
    tests = FreeCAD.__unit_test__

    suite = unittest.TestSuite()

    FreeCAD.Console.PrintMessage("\nRegistered test units:\n\n")
    for test in tests:
        FreeCAD.Console.PrintMessage(("%s\n" % test))
    FreeCAD.Console.PrintMessage("\nPlease choose one or use 0 for all\n")

    return suite


def TestText(s):
    s = unittest.defaultTestLoader.loadTestsFromName(s)
    # Some tests (or native components they exercise) can close or corrupt stdout
    # (fd 1). Two failure modes follow from that, both guarded against here:
    #   1. The runner writes its report to fd 1, so its next stream.flush() raises
    #      "[Errno 9] Bad file descriptor" and aborts the whole run, silently skipping
    #      every suite registered after the offending one.
    #   2. A later test that simply print()s then fails with the same error, poisoned
    #      by an earlier test that left fd 1 closed.
    # We run the reporter on a private duplicate of fd 1, and restore fd 1 from that
    # duplicate after every test so no test can poison the ones that follow.
    try:
        saved_fd = os.dup(1)
    except OSError:
        saved_fd = None

    if saved_fd is None:
        # Fall back to the previous behaviour if fd 1 cannot be duplicated.
        r = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
        retval = r.run(s)
        sys.stdout.flush()
        return retval

    stream = os.fdopen(saved_fd, "w", closefd=True)

    def _restore_fd1():
        try:
            os.dup2(saved_fd, 1)
        except OSError:
            pass

    class _Fd1RestoringResult(unittest.TextTestResult):
        def stopTest(self, test):
            super().stopTest(test)
            _restore_fd1()

    try:
        r = unittest.TextTestRunner(
            stream=stream, verbosity=2, resultclass=_Fd1RestoringResult
        )
        retval = r.run(s)
        # Flushing to make sure the stream is written to the console
        # before the wrapping process stops executing. Without this line
        # executing the tests from command line did not show stats
        # and proper traceback in some cases.
        stream.flush()
    finally:
        _restore_fd1()
        stream.close()
    return retval


def RunConfiguredTextTest():
    test_case = FreeCAD.ConfigGet("TestCase")
    return TestText(test_case)


def Test(s):
    TestText(s)


def testAll():
    r = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    return r.run(All())


def testUnit():
    TestText(unittest.TestLoader().loadTestsFromName("UnitTests"))


def testDocument():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName("Document"))
    TestText(suite)
