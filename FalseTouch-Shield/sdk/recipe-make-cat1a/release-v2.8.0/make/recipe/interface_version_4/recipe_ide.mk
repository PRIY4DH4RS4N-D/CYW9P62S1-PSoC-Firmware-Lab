################################################################################
# \file recipe_ide.mk
#
# \brief
# This make file defines the IDE export variables and target.
#
################################################################################
# \copyright
# Copyright (c) 2022-2026, Infineon Technologies AG, or an affiliate of
# Infineon Technologies AG. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

ifeq ($(WHICHFILE),true)
$(info Processing $(lastword $(MAKEFILE_LIST)))
endif

##############################################
# General
##############################################
MTB_RECIPE__IDE_SUPPORTED:=eclipse vscode uvision5 ewarm8

_MTB_RECIPE__IDE_EXPORT_INTERFACE_VERSION=interface_version_4
_MTB_RECIPE__IDE_RECIPE_DIR:=$(MTB_TOOLS__RECIPE_DIR)/make/recipe/$(_MTB_RECIPE__IDE_EXPORT_INTERFACE_VERSION)
ifeq ($(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR),KitProg3)
_MTB_RECIPE__HIDE_ADVANCED_PROGRAM:=false
endif
include $(_MTB_RECIPE__IDE_RECIPE_DIR)/recipe_ide_common.mk

##############################################
# Eclipe VSCode
##############################################

_MTB_RECIPE__IDE_TEXT_DATA_FILE=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_ide_text_data.txt

##############################################
# Eclipe
##############################################
_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE:=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_eclipse_template_meta_data.txt
_MTB_RECIPE__ECLIPSE_TEMPLATE_REGEX_DATA_FILE:=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_eclipse_template_regex_data.txt

eclipse_generate: recipe_eclipse_text_replacement_data_file recipe_eclipse_meta_data_file recipe_eclipse_regex_replacement_data_file
eclipse_generate: MTB_CORE__EXPORT_CMDLINE += -textdata $(_MTB_RECIPE__IDE_TEXT_DATA_FILE) -metadata $(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE) -textregexdata $(_MTB_RECIPE__ECLIPSE_TEMPLATE_REGEX_DATA_FILE)

recipe_eclipse_regex_replacement_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_REGEX_DATA_FILE),^.*//triple-core only//.*$$=)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_REGEX_DATA_FILE),^.*//quad-core only//.*$$=)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_REGEX_DATA_FILE),^.*//penta-core only//.*$$=)

recipe_eclipse_text_replacement_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_SECOND_RESET&&=$(_MTB_RECIPE__OPENOCD_SECOND_RESET_TYPE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_RUN_RESTART_DEBUG_CMD&&=$(_MTB_RECIPE__OPENOCD_RUN_RESTART_CMD_DEBUG_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_RUN_RESTART_ATTACH_CMD&&=$(_MTB_RECIPE__OPENOCD_RUN_RESTART_CMD_ATTACH_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_DO_CONTINUE&&=$(_MTB_RECIPE__OPENOCD_DO_CONTINUE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_SET_STOP_AT&&=$(_MTB_RECIPE__OPENOCD_SET_STOP_AT))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_SHELL_TIMEOUT&&=$(CY_OPENOCD_SHELL_TIMEOUT_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__JLINK_CFG_PROGRAM&&=$(_MTB_RECIPE__JLINK_DEVICE_CFG_PROGRAM))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__JLINK_CFG_DEBUG&&=$(_MTB_RECIPE__JLINK_DEVICE_CFG_DEBUG))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__JLINK_CFG_ATTACH&&=$(_MTB_RECIPE__JLINK_DEVICE_CFG_ATTACH))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_PORT_SELECT&&=$(_MTB_RECIPE__OPENOCD_EXTRA_PORT_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_CM0_FLAG&&=$(_MTB_RECIPE__OPENOCD_CM0_DISABLE_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_TARGET_AP&&=$(_MTB_RECIPE__OPENOCD_TARGET_AP_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_TARGET_AP_DEBUG&&=$(_MTB_RECIPE__OPENOCD_TARGET_AP_DEBUG_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_SMIF_DISABLE&&=$(_MTB_RECIPE__OPENOCD_SMIF_DISABLE_ECLIPSE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_MONITOR_CMDS_NAME&&=$(_MTB_RECIPE__OPENOCD_MONITOR_CMDS_NAME))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__CORE&&=$(_MTB_RECIPE__OPENOCD_CORE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__QSPI_CFG_PATH&&=$(_MTB_RECIPE__OPENOCD_QSPI_CFG_PATH_WITH_FLAG))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__QSPI_CFG_PATH_APPLICATION&&=$(_MTB_RECIPE__OPENOCD_QSPI_CFG_PATH_APPLICATION_WITH_FLAG))
ifneq (,$(_MTB_RECIPE__IS_SECURE_DEVICE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__FIRST_APP_NAME&&=$(lastword $(MTB_APPLICATION_SUBPROJECTS)))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__SECOND_APP_NAME&&=$(firstword $(MTB_APPLICATION_SUBPROJECTS)))
else
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__FIRST_APP_NAME&&=$(firstword $(MTB_APPLICATION_SUBPROJECTS)))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__SECOND_APP_NAME&&=$(lastword $(MTB_APPLICATION_SUBPROJECTS)))
endif
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_CM0_RTOS_CONFIG&&=$(_MTB_RECIPE__OPENOCD_CM0_RTOS_CONFIG))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_CM4_RTOS_CONFIG&&=$(_MTB_RECIPE__OPENOCD_CM4_RTOS_CONFIG))
ifneq (,$(findstring CY_ENABLE_XIP_PROGRAM, $(DEFINES)))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__PGMGUI_QSPI_ENABLE&&=on)
else
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__PGMGUI_QSPI_ENABLE&&=off)
endif
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__PGMGUI_TARGET_AP&&=$(_MTB_RECIPE__OPENOCD_TARGET_AP))

recipe_eclipse_meta_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),UUID=&&PROJECT_UUID_$(MTB_RECIPE__CORE)&&)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),UUID=&&PROJECT_UUID&&)
ifneq (,$(_MTB_RECIPE__IS_MULTI_CORE_APPLICATION))
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),APPLICATION_UUID=&&APPLICATION_UUID&&)
ifneq (,$(_MTB_RECIPE__IS_FIRST_PRJ))
# Advanced KitProg3 programming
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/eclipse/Application/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)=../.mtbLaunchConfigs)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/App/flash/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/multicore=../.mtbLaunchConfigs)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/App/internal=../.mtbLaunchConfigs)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),UPDATE_APPLICATION_PREF_FILE=1)
else
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=../.mtbLaunchConfigs=../.mtbLaunchConfigs)
endif #(,$(_MTB_RECIPE__IS_FIRST_PRJ))
ifeq (,$(_MTB_RECIPE__IS_SECURE_DEVICE))
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/eclipse/$(MTB_RECIPE__CORE)/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/multi_core=.mtbLaunchConfigs)
else
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/eclipse/$(MTB_RECIPE__CORE)/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/multi_core_secure=.mtbLaunchConfigs)
endif
else #(,$(_MTB_RECIPE__IS_MULTI_CORE_APPLICATION))
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/single/internal=.mtbLaunchConfigs)
endif #(,$(_MTB_RECIPE__IS_MULTI_CORE_APPLICATION))
ifeq ($(MTB_COMBINE_SIGN_$(_MTB_RECIPE__IDE_PRJ_DIR_NAME)_HEX_FILES),)
ifneq (,$(_MTB_RECIPE__IS_MULTI_CORE_APPLICATION))
ifeq ($(MTB_RECIPE__CORE),CM4)
ifeq ($(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR),KitProg3)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/flash/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/multicore/Add $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch=.mtbLaunchConfigs/$(_MTB_RECIPE__ECLIPSE_PROJECT_NAME) $(_MTB_RECIPE__ECLIPSE_OPENOCD_DEBUG_MULTICORE_SECOND_CONFIG_NAME) $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch)
endif
endif
endif
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/flash/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/any=.mtbLaunchConfigs)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/any=.mtbLaunchConfigs)
endif
ifeq ($(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR),KitProg3)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/eclipse/$(MTB_RECIPE__CORE)/KitProg3/advanced=.mtbLaunchConfigs)
endif

.PHONY: recipe_eclipse_text_replacement_data_file recipe_eclipse_meta_data_file recipe_eclipse_regex_replacement_data_file

##############################################
# VSCode
##############################################
_MTB_RECIPE__VSCODE_MULTI_CORE_PRJ_TASKS_JSON:=$(_MTB_RECIPE__IDE_CORE_SCRIPT_DIR)/vscode/dependencies_tasks.json
_MTB_RECIPE__VSCODE_MULTI_CORE_APP_TASKS_JSON:=$(_MTB_RECIPE__IDE_CORE_SCRIPT_DIR)/vscode/tasks_internal.json
_MTB_RECIPE__VSCODE_SINGLE_CORE_APP_TASKS_JSON:=$(_MTB_RECIPE__IDE_CORE_SCRIPT_DIR)/vscode/tasks_internal.json

_MTB_RECIPE__VSCODE_MULTI_CORE_PRJ_LAUNCH_JSON:=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/vscode/CMx/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/launch.json
_MTB_RECIPE__VSCODE_MULTI_CORE_APP_LAUNCH_JSON:=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/vscode/Application/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/launch.json
_MTB_RECIPE__VSCODE_SINGLE_CORE_APP_LAUNCH_JSON:=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/vscode/CMx/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/launch.json

_MTB_RECIPE__VSCODE_TEMPLATE_META_DATA_FILE:=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_vscode_template_meta_data.txt
_MTB_RECIPE__VSCODE_TEMPLATE_REGEX_DATA_FILE:=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_vscode_template_regex_data.txt
vscode_generate: recipe_vscode_text_replacement_data_file recipe_vscode_meta_data_file recipe_vscode_regex_replacement_data_file
vscode_generate: MTB_CORE__EXPORT_CMDLINE += -textdata $(_MTB_RECIPE__IDE_TEXT_DATA_FILE) -metadata $(_MTB_RECIPE__VSCODE_TEMPLATE_META_DATA_FILE) -textregexdata $(_MTB_RECIPE__VSCODE_TEMPLATE_REGEX_DATA_FILE)

recipe_vscode_text_replacement_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__DEVICE_PROGRAM&&=$(_MTB_RECIPE__JLINK_DEVICE_CFG_PROGRAM))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__DEVICE_DEBUG&&=$(_MTB_RECIPE__JLINK_DEVICE_CFG_DEBUG))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_CHIP&&=$(_MTB_RECIPE__OPENOCD_CHIP_NAME))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_CORE&&=$(_MTB_RECIPE__OPENOCD_CORE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__QSPI_CFG_PATH&&=$(_MTB_RECIPE__OPENOCD_QSPI_CFG_PATH))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__QSPI_CFG_PATH_APPLICATION&&=$(_MTB_RECIPE__OPENOCD_QSPI_CFG_PATH_APPLICATION))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__MULTICORE_SECOND_CONFIG_VSCODE&&=$(_MTB_RECIPE__MULTICORE_SECOND_CONFIG_VSCODE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_MONITOR_CMDS_NAME&&=$(_MTB_RECIPE__OPENOCD_MONITOR_CMDS_NAME))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__MCU_NAME&&=$(_MTB_RECIPE__MCU_NAME))
ifneq (,$(_MTB_RECIPE__IS_SECURE_DEVICE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__FIRST_APP_NAME&&=$(lastword $(MTB_APPLICATION_SUBPROJECTS)))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__SECOND_APP_NAME&&=$(firstword $(MTB_APPLICATION_SUBPROJECTS)))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__TARGET_PROCESSOR_NUMBER_MULTICORE&&=1)
else
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__FIRST_APP_NAME&&=$(firstword $(MTB_APPLICATION_SUBPROJECTS)))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__SECOND_APP_NAME&&=$(lastword $(MTB_APPLICATION_SUBPROJECTS)))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__TARGET_PROCESSOR_NUMBER_MULTICORE&&=0)
endif
ifeq ($(MTB_RECIPE__CORE),CM0P)
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__TARGET_PROCESSOR_NAME&&=CM0+)
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__TARGET_PROCESSOR_NUMBER&&=0)
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__PROCESSOR_COUNT&&=2)
else
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__TARGET_PROCESSOR_NAME&&=CM4)
ifeq (,$(_MTB_RECIPE__IS_MULTI_CORE_DEVICE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__TARGET_PROCESSOR_NUMBER&&=0)
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__PROCESSOR_COUNT&&=1)
else
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__TARGET_PROCESSOR_NUMBER&&=1)
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__PROCESSOR_COUNT&&=2)
endif #ifeq (,$(_MTB_RECIPE__IS_MULTI_CORE_DEVICE))
endif #ifeq ($(MTB_RECIPE__CORE),CM0P)
ifeq (psoc64,$(_MTB_RECIPE__OPENOCD_CHIP_NAME))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_PSOC6_TARGET_AP&&=set TARGET_AP $(_MTB_RECIPE__OPENOCD_CORE)_ap)
ifeq (,$(_MTB_RECIPE__IS_FIRST_PRJ))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__CM0_CM4_ELF_FILE_APPLICATION&&=$(_MTB_RECIPE__VSCODE_ELF_FILE_APPLICATION))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__CM0_CM4_JLINK_DEVICE&&=$(_MTB_RECIPE__JLINK_DEVICE_CFG_DEBUG))
endif
else
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_PSOC6_TARGET_AP&&=)
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__CM0_CM4_ELF_FILE_APPLICATION&&=$(_MTB_RECIPE__VSCODE_ELF_FILE_APPLICATION))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__CM0_CM4_JLINK_DEVICE&&=$(_MTB_RECIPE__JLINK_DEVICE_CFG_DEBUG))
endif
ifneq (true,$(_MTB_RECIPE__IS_MULTI_CORE_DEVICE))
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_ENABLE_CM0&&=set ENABLE_CM0 0)
else
	$(call mtb__file_append,$(_MTB_RECIPE__IDE_TEXT_DATA_FILE),&&_MTB_RECIPE__OPENOCD_ENABLE_CM0&&=)
endif

recipe_vscode_regex_replacement_data_file:
ifeq (psoc64,$(_MTB_RECIPE__OPENOCD_CHIP_NAME))
	$(call mtb__file_write,$(_MTB_RECIPE__VSCODE_TEMPLATE_REGEX_DATA_FILE),^(.*)//PSoC64 Only//(.*)$$=\1\2)
	$(call mtb__file_append,$(_MTB_RECIPE__VSCODE_TEMPLATE_REGEX_DATA_FILE),^.*//PSoC6 Only//.*$$=)
else
	$(call mtb__file_write,$(_MTB_RECIPE__VSCODE_TEMPLATE_REGEX_DATA_FILE),^(.*)//PSoC6 Only//(.*)$$=\1\2)
	$(call mtb__file_append,$(_MTB_RECIPE__VSCODE_TEMPLATE_REGEX_DATA_FILE),^.*//PSoC64 Only//.*$$=)
endif

recipe_vscode_meta_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__VSCODE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/vscode/CMx/openocd.tcl=openocd.tcl)
ifneq (,$(_MTB_RECIPE__IS_MULTI_CORE_APPLICATION))
ifneq (,$(_MTB_RECIPE__IS_FIRST_PRJ))
	$(call mtb__file_append,$(_MTB_RECIPE__VSCODE_TEMPLATE_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/vscode/Application/openocd.tcl=../openocd.tcl)
endif
endif
.PHONY: recipe_vscode_text_replacement_data_file recipe_vscode_meta_data_file recipe_vscode_regex_replacement_data_file

##############################################
# UV
##############################################
_MTB_RECIPE__CMSIS_ARCH_NAME:=CAT1A_DFP
_MTB_RECIPE__CMSIS_VENDOR_NAME:=Infineon
_MTB_RECIPE__CMSIS_VENDOR_ID:=7

# Define _MTB_RECIPE__CMSIS_PNAME for export into uVision
ifeq ($(MTB_RECIPE__CORE),CM0P)
_MTB_RECIPE__CMSIS_PNAME:=Cortex-M0p
else ifeq ($(MTB_RECIPE__CORE),CM4)
_MTB_RECIPE__CMSIS_PNAME:=Cortex-M4
else
_MTB_RECIPE__CMSIS_PNAME:=
endif

# Program.ini file
_MTB_RECIPE__PROGRAM_INI_FILE:=$(MTB_TOOLS__PRJ_DIR)/program.ini

ifneq (,$(_MTB_RECIPE__IS_SECURE_DEVICE))
uvision5: recipe_uvision_program_ini_file
recipe_uvision_program_ini_file:
	$(call mtb__file_write,$(_MTB_RECIPE__PROGRAM_INI_FILE),LOAD $$L\..\build\$(TARGET)\Debug\$(APPNAME).hex)
else ifneq (,$(_MTB_RECIPE__IS_MULTI_CORE_APPLICATION))
ifeq ($(MTB_RECIPE__CORE),CM0P)
uvision5: recipe_uvision_program_ini_file
recipe_uvision_program_ini_file:
	$(call mtb__file_write,$(_MTB_RECIPE__PROGRAM_INI_FILE),LOAD ..\proj_cm4\proj_cm4_Objects\proj_cm4.axf)
endif # ifeq ($(MTB_RECIPE__CORE),CM0P)
endif # ifneq (,$(_MTB_RECIPE__IS_SECURE_DEVICE))

# uVision build data file
_MTB_RECIPE__UVISION_BUILD_DATA_FILE:=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_ide_build_data.txt

uvision5: MTB_CORE__EXPORT_CMDLINE += -build_data $(_MTB_RECIPE__UVISION_BUILD_DATA_FILE)
uvision5: recipe_uvision_build_data_file

recipe_uvision_build_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__UVISION_BUILD_DATA_FILE),LINKER_SCRIPT=$(MTB_RECIPE__LINKER_SCRIPT))
ifeq ($(MTB_RECIPE__CORE),CM4)
	$(call mtb__file_append,$(_MTB_RECIPE__UVISION_BUILD_DATA_FILE),FPU=$(_MTB_RECIPE_CMSIS__DFPU))
endif

.PHONY: recipe_uvision_build_data_file

# UVision DFP data file
_MTB_RECIPE__UVISION_DFP_DATA_FILE:=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_ide_dfp_data.txt

uvision5: recipe_uvision_dfp_data_file
uvision5: MTB_CORE__EXPORT_CMDLINE += -dfp_data $(_MTB_RECIPE__UVISION_DFP_DATA_FILE)

recipe_uvision_dfp_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__UVISION_DFP_DATA_FILE),DEVICE=$(DEVICE))
	$(call mtb__file_append,$(_MTB_RECIPE__UVISION_DFP_DATA_FILE),DFP_NAME=$(_MTB_RECIPE__CMSIS_ARCH_NAME))
	$(call mtb__file_append,$(_MTB_RECIPE__UVISION_DFP_DATA_FILE),VENDOR_NAME=$(_MTB_RECIPE__CMSIS_VENDOR_NAME))
	$(call mtb__file_append,$(_MTB_RECIPE__UVISION_DFP_DATA_FILE),VENDOR_ID=$(_MTB_RECIPE__CMSIS_VENDOR_ID))
	$(call mtb__file_append,$(_MTB_RECIPE__UVISION_DFP_DATA_FILE),PNAME=$(_MTB_RECIPE__CMSIS_PNAME))
.PHONY: recipe_uvision_program_ini_file recipe_uvision_dfp_data_file

##############################################
# EW
##############################################
ifeq (true,$(_MTB_RECIPE__TVII_DEVICE))
_MTB_RECIPE__IAR_CORE_PREFIX:=_
else
_MTB_RECIPE__IAR_CORE_PREFIX:=
endif

ifeq ($(MTB_RECIPE__CORE),CM4)
ifneq (,$(filter true,$(_MTB_RECIPE__TVII_DEVICE) $(_MTB_RECIPE__IS_MULTI_CORE_DEVICE)))
_MTB_RECIPE__IAR_CORE_SUFFIX=$(_MTB_RECIPE__IAR_CORE_PREFIX)M4
endif
endif
ifeq ($(MTB_RECIPE__CORE),CM0P)
_MTB_RECIPE__IAR_CORE_SUFFIX=$(_MTB_RECIPE__IAR_CORE_PREFIX)M0+
endif

_MTB_RECIPE__EWARM_BUILD_DATA_FILE:=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/recipe_ide_build_data.txt

ewarm8: MTB_CORE__EXPORT_CMDLINE += -build_data $(_MTB_RECIPE__EWARM_BUILD_DATA_FILE)
ewarm8: recipe_ewarm_build_data_file

recipe_ewarm_build_data_file:
	$(call mtb__file_write,$(_MTB_RECIPE__EWARM_BUILD_DATA_FILE),LINKER_SCRIPT=$(MTB_RECIPE__LINKER_SCRIPT))
.PHONY: recipe_ewarm_build_data_file

##############################################
# Combiner/Signer Integration
##############################################

ifneq ($(MTB_COMBINE_SIGN_$(_MTB_RECIPE__IDE_PRJ_DIR_NAME)_HEX_FILES),)
_MTB_RECIPE__VSCODE_CS_TASKS_JSON:=$(_MTB_RECIPE__IDE_CORE_SCRIPT_DIR)/vscode/tasks_program_sign_combine.json
_MTB_RECIPE__VSCODE_CS_LAUNCH_JSON:=$(_MTB_RECIPE__IDE_TEMPLATE_DIR)/vscode/CMx/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/launch_combine_sign.json

_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE=$(MTB_TOOLS__OUTPUT_CONFIG_DIR)/eclipse_combine_sign_meta_data.txt
_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME:=.mtbLaunchConfigs/$(_MTB_RECIPE__ECLIPSE_APPLICATION_NAME).&&MTB_COMBINE_SIGN_&&IDX&&_CONFIG_NAME&&

eclipse_generate: MTB_CORE__EXPORT_CMDLINE += -metadata $(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE)
eclipse_generate: recipe_eclipse_combine_sign_meta

recipe_eclipse_combine_sign_meta:
	$(call mtb__file_write,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE))
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/flash/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/combine_sign/Debug.launch=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) Debug $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/flash/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/combine_sign/Attach.launch=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) Attach $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/combine_sign/Program.launch=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) Program.launch)
ifeq ($(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR),KitProg3)
ifneq (,$(_MTB_RECIPE__IS_MULTI_CORE_APPLICATION))
ifeq ($(MTB_RECIPE__CORE),CM4)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPLACE=$(_MTB_RECIPE__IDE_RECIPE_DIR)/Proj/flash/$(_MTB_RECIPE__PROGRAM_INTERFACE_SUBDIR)/multicore/Add $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) $(_MTB_RECIPE__ECLIPSE_OPENOCD_DEBUG_MULTICORE_SECOND_CONFIG_NAME) $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch)
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPEAT=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) $(_MTB_RECIPE__MULTICORE_SECOND_CONFIG_ECLIPSE) $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch=$(MTB_COMBINE_SIGN_$(_MTB_RECIPE__IDE_PRJ_DIR_NAME)_HEX_FILES))
endif
endif
endif
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPEAT=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) Debug $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch=$(MTB_COMBINE_SIGN_$(_MTB_RECIPE__IDE_PRJ_DIR_NAME)_HEX_FILES))
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPEAT=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) Attach $(_MTB_RECIPE__PROGRAM_INTERFACE_LAUNCH_SUFFIX).launch=$(MTB_COMBINE_SIGN_$(_MTB_RECIPE__IDE_PRJ_DIR_NAME)_HEX_FILES))
	$(call mtb__file_append,$(_MTB_RECIPE__ECLIPSE_COMBINE_SIGN_META_DATA_FILE),TEMPLATE_REPEAT=$(_MTB_RECIPE__ECLIPSE_CS_DST_BASE_NAME) Program.launch=$(MTB_COMBINE_SIGN_$(_MTB_RECIPE__IDE_PRJ_DIR_NAME)_HEX_FILES))

endif
