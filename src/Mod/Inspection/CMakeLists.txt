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

add_custom_target(InspectionScripts ALL
    SOURCES ${Inspection_Scripts}
)

fc_target_copy_resource(InspectionScripts
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_BINARY_DIR}/Mod/Inspection
    ${Inspection_Scripts}
)

INSTALL(
    FILES
        ${Inspection_Scripts}
    DESTINATION
        Mod/Inspection
)
