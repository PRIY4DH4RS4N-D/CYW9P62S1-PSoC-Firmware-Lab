/***********************************************************************************************//**
 * \file cy_retarget_io.h
 *
 * \brief
 * Provides APIs for transmitting messages to or from the board via standard
 * printf/scanf functions. Messages are transmitted over a UART connection which
 * is generally connected to a host machine. Transmission is done at 115200 baud
 * using the tx and rx pins provided by the user of this library. The UART
 * instance is made available via cy_retarget_io_uart_obj in case any changes
 * to the default configuration are desired.
 * NOTE: If the application is built using newlib-nano, by default, floating
 * point format strings (%f) are not supported. To enable this support you must
 * add '-u _printf_float' to the linker command line.
 *
 ***************************************************************************************************
 * \copyright
 * (c) 2018-2026, Infineon Technologies AG, or an affiliate of Infineon
 * Technologies AG. All rights reserved.
 * This software, associated documentation and materials ("Software") is
 * owned by Infineon Technologies AG or one of its affiliates ("Infineon")
 * and is protected by and subject to worldwide patent protection, worldwide
 * copyright laws, and international treaty provisions. Therefore, you may use
 * this Software only as provided in the license agreement accompanying the
 * software package from which you obtained this Software. If no license
 * agreement applies, then any use, reproduction, modification, translation, or
 * compilation of this Software is prohibited without the express written
 * permission of Infineon.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Disclaimer: UNLESS OTHERWISE EXPRESSLY AGREED WITH INFINEON, THIS SOFTWARE
 * IS PROVIDED AS-IS, WITH NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING, BUT NOT LIMITED TO, ALL WARRANTIES OF NON-INFRINGEMENT OF
 * THIRD-PARTY RIGHTS AND IMPLIED WARRANTIES SUCH AS WARRANTIES OF FITNESS FOR A
 * SPECIFIC USE/PURPOSE OR MERCHANTABILITY.
 * Infineon reserves the right to make changes to the Software without notice.
 * You are responsible for properly designing, programming, and testing the
 * functionality and safety of your intended application of the Software, as
 * well as complying with any legal requirements related to its use. Infineon
 * does not guarantee that the Software will be free from intrusion, data theft
 * or loss, or other breaches ("Security Breaches"), and Infineon shall have
 * no liability arising out of any Security Breaches. Unless otherwise
 * explicitly approved by Infineon, the Software may not be used in any
 * application where a failure of the Product or any consequences of the use
 * thereof can reasonably be expected to result in personal injury.
 **************************************************************************************************/

/* *SUSPEND-FORMATTING* */
/**
 * \addtogroup group_board_libs Retarget IO
 * \{
 * \brief Redirects standard input/output (\c printf / \c scanf) to a UART port
 *        or any custom I/O backend.
 *
 * \details
 * The library selects the appropriate initialization function based on the
 * active build configuration. Only one interface mode can be active at a time.
 * The HAL mode is determined automatically by the device package in the BSP:
 * HAL v3 sets \c COMPONENT_MTB_HAL; HAL v2 sets \c CY_USING_HAL.
 * These are not manually configurable.
 *
 * | Function | Available When | Description |
 * |----------|----------------|-------------|
 * | <a href="#ga7adc4998fba6bade5709336ba47ac32f">cy_retarget_io_init(mtb_hal_uart_t*)</a> | HAL v3 (\c COMPONENT_MTB_HAL) | Initialize with a pre-initialized HAL UART object |
 * | <a href="#gaddff65f18135a8491811ee3886e69707">cy_retarget_io_init(tx, rx, baud)</a> | HAL v2 (\c CY_USING_HAL) | Macro: calls <a href="#gacb7b45b0b8f0aef59b790415c14496a8">cy_retarget_io_init_fc</a> with NC for CTS/RTS |
 * | <a href="#gacb7b45b0b8f0aef59b790415c14496a8">cy_retarget_io_init_fc</a> | HAL v2 (\c CY_USING_HAL) | Initialize with optional flow control pins |
 * | <a href="#gabcaacea7d2ca44d20b4e224b45932245">cy_retarget_io_init_hal</a> | HAL v2 (\c CY_USING_HAL) | Initialize using pre-set \c cy_retarget_io_uart_obj |
 * | <a href="#ga4905a76eaea9b40111887f5b6ff7d252">cy_retarget_io_init(CySCB_Type*)</a> | PDL-only | Initialize with a pre-initialized SCB UART peripheral |
 * | \ref cy_retarget_io_deinit_anchor "cy_retarget_io_deinit" | All | Release the retarget-io interface |
 * | \ref cy_retarget_io_is_tx_active_anchor "cy_retarget_io_is_tx_active" | All | Check whether TX is pending |
 * | \ref cy_retarget_io_change_baud_rate_anchor "cy_retarget_io_change_baud_rate" | HAL v3 (\c COMPONENT_MTB_HAL) | Change baud rate at runtime |
 * | \ref cy_retarget_io_getchar_anchor "cy_retarget_io_getchar" | \c COMPONENT_RETARGET_IO_CUSTOM | Application-provided: read a character |
 * | \ref cy_retarget_io_putchar_anchor "cy_retarget_io_putchar" | \c COMPONENT_RETARGET_IO_CUSTOM | Application-provided: write a character |
 */
/* *RESUME-FORMATTING* */

#pragma once

#include <stdio.h>
#include "cy_result.h"
#if defined(COMPONENT_MTB_HAL)
#include "mtb_hal_hw_types.h"
#elif defined(CY_USING_HAL)
#include "cyhal_hw_types.h"
#else
#include "cy_pdl.h"
#include <stdbool.h>
#endif


#if defined(__cplusplus)
extern "C" {
#endif

#if !defined(COMPONENT_MTB_HAL)

/* Define module errors */
/**
 * \def CY_RETARGET_IO_RSLT_NULL_UART_PTR
 * \brief Error code returned when a null pointer is passed as a UART parameter.
 *
 * This result code is returned by the initialization functions when a NULL
 * pointer is supplied where a valid UART object pointer is required.
 */
#define CY_RETARGET_IO_RSLT_NULL_UART_PTR    \
    (CY_RSLT_CREATE(CY_RSLT_TYPE_ERROR, CY_RSLT_MODULE_BOARD_LIB_RETARGET_IO, 0))

/**
 * \def CY_RETARGET_IO_BAUDRATE
 * \brief Default UART baud rate used by the retarget-io library (115200).
 *
 * This value can be passed directly to the initialization functions as the
 * \c baudrate parameter when the default baud rate is acceptable.
 */
#define CY_RETARGET_IO_BAUDRATE             (115200)

/** UART HAL object used by this library */
#if defined (CY_USING_HAL)
extern cyhal_uart_t cy_retarget_io_uart_obj;
#endif

#endif //!defined(COMPONENT_MTB_HAL)


#if defined(DOXYGEN) && !defined(COMPONENT_MTB_HAL)
/**
 * \brief Initialization function for redirecting low level IO commands to allow
 * sending messages over a UART interface. This will setup the communication
 * interface to allow using printf and related functions.
 *
 * **Available in:** HAL v3 mode (\c COMPONENT_MTB_HAL, set automatically by the device package)
 *
 * Users of the library must do the following before invoking the init function
 *     1. Configure the UART using the device configurator generated structures or
 *        through manually written config structures. Configuration includes the UART TX
 *        and RX pins, CTS/RTS pins if flow control is desired, Baud Rate and other UART
 *        config parameters.
 *     2. Set up the clock source to the UART peripheral. This could be done using the
 *        device configurator or manually. Set up the clock divider value depending on
 *        the desired baud rate.
 *     2. Initialize the UART HW.
 *     3. Set up the HAL UART object.
 *     4. Pass the initilialized HAL UART object to the init
 *
 * In an RTOS environment, this function must be called after the RTOS has been
 * initialized.
 *
 * \param obj Pointer to the pre-initialized HAL UART object
 *
 * \returns CY_RSLT_SUCCESS if successfully initialized, else an error about
 * what went wrong
 */
cy_rslt_t cy_retarget_io_init(mtb_hal_uart_t* obj);
#endif
#if defined(COMPONENT_MTB_HAL)
cy_rslt_t cy_retarget_io_init(mtb_hal_uart_t* obj);
#endif

#if defined(DOXYGEN) && !defined(CY_USING_HAL)
/**
 * \def cy_retarget_io_init(tx, rx, baudrate)
 * \brief Convenience wrapper macro for simplified UART initialization without flow control.
 *
 * **Available in:** HAL v2 mode (\c CY_USING_HAL, set automatically by the device package)
 *
 * This macro calls cy_retarget_io_init_fc() with NC (not connected) values for CTS and RTS pins,
 * providing a simpler interface when flow control is not needed.
 *
 * \param tx UART TX pin, if no TX pin use NC
 * \param rx UART RX pin, if no RX pin use NC
 * \param baudrate UART baudrate
 */
#define cy_retarget_io_init(tx, rx, baudrate)

/**
 * \brief Initialization function for redirecting low level IO commands to allow
 * sending messages over a UART interface with flow control. This will setup the
 * communication interface to allow using printf and related functions.
 *
 * **Available in:** HAL v2 mode (\c CY_USING_HAL, set automatically by the device package)
 *
 * In an RTOS environment, this function must be called after the RTOS has been
 * initialized.
 *
 * \note This function provides full control including flow control pins (CTS/RTS).
 * \note In CY-HAL mode, cy_retarget_io_init(tx, rx, baudrate) is a convenience macro that calls
 * this function with NC values for CTS/RTS.
 *
 * \param tx UART TX pin, if no TX pin use NC
 * \param rx UART RX pin, if no RX pin use NC
 * \param cts UART CTS pin, if no CTS pin use NC
 * \param rts UART RTS pin, if no RTS pin use NC
 * \param baudrate UART baudrate
 * \returns CY_RSLT_SUCCESS if successfully initialized, else an error about
 * what went wrong
 */
cy_rslt_t cy_retarget_io_init_fc(cyhal_gpio_t tx, cyhal_gpio_t rx, cyhal_gpio_t cts,
                                 cyhal_gpio_t rts, uint32_t baudrate);

/**
 * \brief Initialization function for redirecting low level IO commands to allow
 * sending messages over a UART interface with a configurator generated configuration
 * struct. This will setup the communication interface to allow using printf and
 * related functions.
 *
 * **Available in:** HAL v2 mode (\c CY_USING_HAL, set automatically by the device package)
 *
 * This function assumes that you've already initialized cy_retarget_io_uart_obj
 * using some other mechanism.
 *
 * In an RTOS environment, this function must be called after the RTOS has been
 * initialized.
 *
 * \note Requires cy_retarget_io_uart_obj to be pre-initialized before calling this function.
 *
 * \returns CY_RSLT_SUCCESS if successfully initialized, else an error about
 * what went wrong
 */
cy_rslt_t cy_retarget_io_init_hal(void);
#endif
#if defined(CY_USING_HAL)
#define cy_retarget_io_init(tx, rx, baudrate) cy_retarget_io_init_fc(tx, rx, NC, NC, baudrate)
cy_rslt_t cy_retarget_io_init_fc(cyhal_gpio_t tx, cyhal_gpio_t rx, cyhal_gpio_t cts,
                                 cyhal_gpio_t rts, uint32_t baudrate);
cy_rslt_t cy_retarget_io_init_hal(void);
#endif // defined(CY_USING_HAL)

#if (!defined(COMPONENT_MTB_HAL) && !defined(CY_USING_HAL)) || defined(DOXYGEN)
/**
 * \brief Initialization function for redirecting low level IO commands to allow
 * sending messages over a UART interface with a configurator generated configuration
 * struct. This will setup the communication interface to allow using printf and
 * related functions.
 *
 * **Available in:** PDL-only mode (when neither \c COMPONENT_MTB_HAL (HAL v3),
 * nor \c CY_USING_HAL (HAL v2) is defined)
 *
 * This function assumes that you've already 1) initialized, and 2) enabled the
 * UART instance using PDL function calls.
 *
 * When not using the HAL, retarget-io is not thread safe.  Consider using printf
 * from a single thread or using a mutex to protect the printf calls.
 *
 * \note This mode is not thread-safe and requires manual concurrency management.
 *
 * \param uart Pointer to UART object, usually named and defined in device-configurator.
 *
 * \returns CY_RSLT_SUCCESS if successfully initialized, else an error if the UART
 * parameter is a null pointer.
 */
cy_rslt_t cy_retarget_io_init(CySCB_Type* uart);
#endif

#ifdef DOXYGEN

/** Defining this macro enables conversion of line feed (LF) into carriage
 * return followed by line feed (CR & LF) on the output direction (STDOUT). You
 * can define this macro through the DEFINES variable in the application
 * Makefile.
 */
#define CY_RETARGET_IO_CONVERT_LF_TO_CRLF

#endif // DOXYGEN

/**
 * \anchor cy_retarget_io_is_tx_active_anchor
 * \brief Checks whether there is data waiting to be written to the serial console.
 * \returns true if there are pending TX transactions, otherwise false
 */
bool cy_retarget_io_is_tx_active(void);

/**
 * \anchor cy_retarget_io_deinit_anchor
 * \brief Releases the UART interface allowing it to be used for other purposes.
 * After calling this, printf and related functions will no longer work.
 */
void cy_retarget_io_deinit(void);

#if defined(COMPONENT_RETARGET_IO_CUSTOM) || defined(DOXYGEN)
/**
 * \anchor cy_retarget_io_getchar_anchor
 * \brief Provide custom implementation for reading characters via stdin.
 *  When retarget-io is configured to use a custom interface, this
 *  function must be implemented by the application.
 *  Blocks indefinitely until a character is available.
 * \param c Character received from input stream
 * \returns CY_RSLT_SUCCESS if successfully, else an error.
 */
cy_rslt_t cy_retarget_io_getchar(char* c);

/**
 * \anchor cy_retarget_io_putchar_anchor
 * \brief Provide custom implementation for writing characters via stdout.
 *  When retarget-io is configured to use a custom interface, this
 *  function must be implemented by the application.
 *  Blocks indefinitely until the character is able to be sent.
 * \param c Character from printf to be written to output stream
 * \returns CY_RSLT_SUCCESS if successfully, else an error.
 */
cy_rslt_t cy_retarget_io_putchar(char c);
#endif // COMPONENT_RETARGET_IO_CUSTOM

#if defined(COMPONENT_MTB_HAL) || defined(DOXYGEN)
/**
 * \anchor cy_retarget_io_change_baud_rate_anchor
 * \brief Changes the UART baud rate for the retarget-io interface.
 *
 * This function allows dynamic baud rate changes during runtime using the HAL v3 (MTB-HAL)
 * framework.
 * It operates on the UART object that was previously initialized with cy_retarget_io_init(),
 * so no UART object parameter is needed.
 *
 * The function uses the HAL v3 (MTB-HAL) baud rate setting capability to automatically determine
 * and configure the optimal peripheral clock divider and oversample values required
 * to achieve the target baud rate with minimal error. This leverages the HAL's built-in
 * expertise for accurate baud rate configuration across different hardware platforms.
 *
 * \note This function requires \c COMPONENT_MTB_HAL to be defined (HAL v3, set automatically by the
 * device package).
 *       It is not available when using HAL v2 (CY-HAL) or PDL-only configurations.
 * \note Changing the baud rate will cause a brief communication interruption.
 * \note The terminal/host must also be set to the new baud rate to maintain communication.
 * \note For production environments, consider using a separate debug UART with a fixed baud rate.
 *
 * \param baud_rate Desired baud rate (e.g., 9600, 115200, 230400)
 * \param actual_baud Pointer to store the actual baud rate achieved by the hardware,
 *                    or NULL if the actual baud rate is not needed
 *
 * \returns CY_RSLT_SUCCESS if successfully changed, else an error about
 * what went wrong
 */
cy_rslt_t cy_retarget_io_change_baud_rate(uint32_t baud_rate, uint32_t* actual_baud);
#endif // defined(COMPONENT_MTB_HAL) || defined(DOXYGEN)

#if defined(__cplusplus)
}
#endif

/** \} group_board_libs */
