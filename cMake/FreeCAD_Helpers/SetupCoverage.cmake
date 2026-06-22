# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the FreeCAD project.

#--------------------------------------------------------------------------
#   Copyright (c) 2026 FreeCAD Project Association                        *
#                                                                         *
#   This file is part of the FreeCAD CAx development system.              *
#                                                                         *
#   This program is free software; you can redistribute it and/or modify  *
#   it under the terms of the GNU Library General Public License (LGPL)   *
#   as published by the Free Software Foundation; either version 2 of     *
#   the License, or (at your option) any later version.                   *
#   for detail see the LICENCE text file.                                 *
#                                                                         *
#   FreeCAD is distributed in the hope that it will be useful,            *
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#   GNU Library General Public License for more details.                  *
#                                                                         *
#   You should have received a copy of the GNU Library General Public     *
#   License along with FreeCAD; if not, write to the Free Software        *
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#   USA                                                                   *
#                                                                         *
#--------------------------------------------------------------------------

# Enable gcov/llvm-cov compatible coverage instrumentation across all targets
# when FREECAD_COVERAGE is ON. Pair with -DENABLE_DEVELOPER_TESTS=ON and run
# both the C++ (ctest) and Python (FreeCADCmd -t 0) suites to emit .gcda data,
# then aggregate with gcovr. Coverage flags change every compile command, so a
# dedicated build tree (e.g. build/coverage) and a full rebuild are expected.

macro(SetupCoverage)
    if(FREECAD_COVERAGE)
        if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
            message(STATUS "Building with code coverage instrumentation (--coverage)")
            # -O0 and -fno-inline keep line counts faithful to the source.
            add_compile_options(--coverage -O0 -g -fno-inline -fno-omit-frame-pointer)
            add_link_options(--coverage)
        else()
            message(WARNING "FREECAD_COVERAGE is only supported with GCC or Clang; ignoring")
        endif()
    endif()
endmacro()
