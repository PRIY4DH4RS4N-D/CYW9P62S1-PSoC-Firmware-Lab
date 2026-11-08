# Verified hardware

Target: **CYW9P62S1-43438EVB-01**, application BSP `APP_CYW9P62S1-43438EVB-01`, device **CY8C6247BZI-D54**. This project uses the existing onboard hardware and needs no external LED, resistors or wires.

## Evidence

- Infineon [kit guide, document 002-28692](https://www.infineon.com/assets/row/public/documents/30/44/infineon-cyw9p62s1-43438evb-01-psoc-62s1-wi-fi-bt-pioneer-kit-guide-usermanual-en.pdf), Table 2-1 and printed pages 12–14 for pin mapping, page 38/Figure 3-11 for CapSense and page 39/Figure 3-12 for LED5. A downloaded reference copy is [kit-guide.pdf](kit-guide.pdf). The LED schematic was visually inspected.
- Infineon [CYW9-BASE-01 baseboard schematic](https://www.infineon.com/dgdl/Infineon-CYW9-BASE-01_Schematic_AZW-PCBDesignData-v01_00-EN.pdf?fileId=8ac78c8c7d0d8da4017d0f0221551976), sheet 10, Peripherals, confirms the circuit.
- Local `firmware/bsps/TARGET_APP_CYW9P62S1-43438EVB-01/config/GeneratedSource/cycfg_pins.h` provides the actual LED and electrode macros used here. `cybsp_types.h` defines LED on=0 and off=1.
- Local HAL `sdk/mtb-hal-cat1/release-v2.7.4/COMPONENT_CAT1A/source/pin_packages/cyhal_psoc6_01_124_bga.c` contains `tcpwm_line_compl` mappings for all three LED pins. The PDL device header selects the 124-BGA GPIO definitions for CY8C6247BZI-D54. HAL `source/cyhal_pwm.c` accepts complementary pins as primary outputs, adjusts compare/alignment for them, and implements `cyhal_pwm_init_adv`, `cyhal_pwm_set_duty_cycle`, start, stop and free. The routing and APIs were inspected locally.

## Onboard RGB circuit

LED5 is **common-anode**. Its pin 2 connects through R101 (0 ohms) to P6_VDD. Each cathode has its own factory current-limiting resistor. The driver uses inverted PWM so a larger requested light duty means more time LOW at the pin.

| Channel | BSP macro | MCU pin | LED5 cathode | Factory series resistor | TCPWM alternatives |
|---|---|---|---|---|---|
| Red | CYBSP_LED_RGB_RED | P1.1 | 1 | R15, 750 ohms | TCPWM0 complementary 3; TCPWM1 complementary 3 |
| Green | CYBSP_LED_RGB_GREEN | P0.5 | 3 | R100, 330 ohms | TCPWM0 complementary 2; TCPWM1 complementary 2 |
| Blue | CYBSP_LED_RGB_BLUE | P7.3 | 4 | R16, 270 ohms | TCPWM0 complementary 5; TCPWM1 complementary 13 |

```text
                        P6_VDD
                           |
                       R101 0 ohm
                           |
                 LED5 pin 2 (common anode)
                    /       |       \
                 Red      Green     Blue
                  |         |         |
               pin 1     pin 3      pin 4
                  |         |         |
              R15 750    R100 330   R16 270 ohms
                  |         |         |
                P1.1      P0.5      P7.3
                   active-low 1 kHz PWM
```

HAL allocates three independent counters and clock dividers from those verified mappings; no generated PWM configuration is needed. The copied generated configuration does not reserve those counters. PWM duties are set to zero before counters start. On failure the driver stops and frees allocated PWMs and sets the three cathodes HIGH using GPIO. This is a design and software-call verification; power-up waveforms and runtime PWM polarity still require measurement.

No external RGB wiring is specified because onboard LED5 meets the requirement. Do not parallel an external LED onto these loaded pins or substitute an addressable strip. A common-cathode external LED would require different polarity and a separate electrical design.

## CapSense and serial

| Function | Verified configuration |
|---|---|
| Capacitive Button 1, CSB1 | Button0 widget 0, TX P8.1, shared RX P1.0 |
| Capacitive Button 2, CSB2 | Button1 widget 1, TX P8.2, shared RX P1.0 |
| Five slider segments, CSS1 | LinearSlider0 widget 2, P8.3–P8.7; generated resolution 300 |
| Sensor engine | CSD hardware, `csd_interrupt_IRQn`, priority 5 |
| USB-UART RX/TX | P5.0 / P5.1, KitProg3 bridge, 115200 8N1 |

```text
CSB1 + CSB2 + CSS1 (five segments)
                 |
     preserved generated CapSense configuration
                 |
      async scan -> process -> debounce
                 |
       controller + color engine
                 |
    gamma + brightness -> three TCPWM outputs -> LED5

KitProg3 J6 -> SWD programming and optional USB-UART status
```

The normalized application slider coordinate is 0–1000, converted from the actual runtime widget resolution. It does not create additional physical sensing resolution. The mechanical SW2/SW4 switches are separate and are unused. Keep the factory board configuration; CapSense calibration, baseline tracking and widget filtering remain the supplied middleware's responsibility. No shield electrode is enabled by this application.

GPIO switching can affect capacitive sensing, as noted in the kit guide. Bench testing must include touch/no-touch behavior with PWM running, especially white and demo patterns. No claims of measured touch noise immunity or color calibration are made.
