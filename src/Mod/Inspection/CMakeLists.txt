# SPDX-License-Identifier: LGPL-2.1-or-later

add_subdirectory(App)
if(BUILD_GUI)
    add_subdirectory(Gui)
endif(BUILD_GUI)

set(Inspection_Scripts
    Init.py
    TestInspectionApp.py
)

if(BUILD_GUI)
    list (APPEND Inspection_Scripts InitGui.py)
endif(BUILD_GUI)

# Note: the build-tree copy of these scripts is handled by App/CMakeLists.txt
# via fc_target_copy_resource_flat (same mechanism that copies Init.py); a
# second copy rule here would clash with it ("multiple rules generate ...").

INSTALL(
    FILES
        ${Inspection_Scripts}
    DESTINATION
        Mod/Inspection
)
