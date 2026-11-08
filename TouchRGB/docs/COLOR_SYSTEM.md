# Color system

Colors use unsigned 24-bit **0xRRGGBB** values, with 8 bits per channel. `rgb_t` is an explicit `{r,g,b}` structure; pack/unpack helpers convert between forms. High bits of an unpacked 32-bit input are ignored. These digital values do not imply 16,777,216 optically distinguishable colors on the LED.

## Presets and category selection

Five categories each contain six colors. In mode 2, the slider chooses slot `floor(position * 6 / 1001)` for normalized position 0?1000. B2 confirms that slot. Holding B2 while releasing the slider advances the category and resets the slot to zero. Categories are remembered across mode changes until reset. Slot and category numbers below match the zero-based serial status.

| Category | Slot | Name | HEX | RGB (decimal) |
|---|---|---|---|---|
| 0 warm hues | 0 | Red | #FF0000 | 255, 0, 0 |
| 0 warm hues | 1 | Orange | #FF8000 | 255, 128, 0 |
| 0 warm hues | 2 | Amber | #FFBF00 | 255, 191, 0 |
| 0 warm hues | 3 | Yellow | #FFFF00 | 255, 255, 0 |
| 0 warm hues | 4 | Coral | #FF7F50 | 255, 127, 80 |
| 0 warm hues | 5 | Salmon | #FA8072 | 250, 128, 114 |
| 1 greens | 0 | Lime | #BFFF00 | 191, 255, 0 |
| 1 greens | 1 | Green | #00FF00 | 0, 255, 0 |
| 1 greens | 2 | Spring green | #00FF80 | 0, 255, 128 |
| 1 greens | 3 | Sea green | #2E8B57 | 46, 139, 87 |
| 1 greens | 4 | Teal | #008080 | 0, 128, 128 |
| 1 greens | 5 | Cyan | #00FFFF | 0, 255, 255 |
| 2 blues | 0 | Sky blue | #00BFFF | 0, 191, 255 |
| 2 blues | 1 | Blue | #0000FF | 0, 0, 255 |
| 2 blues | 2 | Indigo | #4B0082 | 75, 0, 130 |
| 2 blues | 3 | Violet | #8F00FF | 143, 0, 255 |
| 2 blues | 4 | Purple | #8000FF | 128, 0, 255 |
| 2 blues | 5 | Royal blue | #4169E1 | 65, 105, 225 |
| 3 pinks | 0 | Magenta | #FF00FF | 255, 0, 255 |
| 3 pinks | 1 | Pink | #FF69B4 | 255, 105, 180 |
| 3 pinks | 2 | Rose | #FF007F | 255, 0, 127 |
| 3 pinks | 3 | Orchid | #DA70D6 | 218, 112, 214 |
| 3 pinks | 4 | Lavender | #E6E6FA | 230, 230, 250 |
| 3 pinks | 5 | Plum | #DDA0DD | 221, 160, 221 |
| 4 neutrals | 0 | White | #FFFFFF | 255, 255, 255 |
| 4 neutrals | 1 | Warm white | #FFD6AA | 255, 214, 170 |
| 4 neutrals | 2 | Cool white | #D6E8FF | 214, 232, 255 |
| 4 neutrals | 3 | Silver | #C0C0C0 | 192, 192, 192 |
| 4 neutrals | 4 | Gray | #808080 | 128, 128, 128 |
| 4 neutrals | 5 | Black/off | #000000 | 0, 0, 0 |

Warm white and cool white are approximate RGB blends, without a claimed color temperature. Factory LED/resistor variations affect channel balance. Black is a color preset and does not erase the remembered brightness.

## HSV

`hsv_t.h` stores integer degrees; conversion reduces hue modulo 360. Saturation and value are 8-bit quantities 0?255. `color_from_hsv()` covers all six hue sectors with rounded integer arithmetic. Saturation zero creates grayscale; value zero creates black. `color_to_hsv()` uses maximum/minimum channels, rounded saturation and signed rounded hue; grayscale convention is hue=0, saturation=0. Converting through integer HSV loses precision, so arbitrary RGB round trips are approximate.

Wheel mode maps normalized slider coordinates to `round(position * 359 / 1000)`. Left endpoint is hue 0 (red), right endpoint hue 359 (almost red). Generated sensing resolution is 300 and is read from the actual widget configuration; normalized coordinates do not add sensor resolution.

## Brightness and gamma

Brightness is 0?100%. B2 outside confirmation modes rounds up to the next 25% step, with 100% wrapping to 0%. Slider brightness rounds to the nearest percentage. Color and brightness are independent: brightness changes preserve the selected RGB value.

The gamma lookup is generated with:

```text
gamma[channel] = round((channel / 255)^2.2 * 65535)
```

It is a constant 256-entry uint16 table in `gamma_table.h`. `color_level(channel, percent)` gives the static endpoint:

```text
level = round(gamma[channel] * percent / 100)
```

Brightness multiplies gamma-corrected light output, so reducing brightness preserves the corrected channel ratios. At a fixed RGB value, 50% means half of the calculated PWM light duty. This is a design choice: the brightness percentage is linear in calculated light duty, while RGB channels use the gamma transfer. It is not a measured perception curve.

The controller ramps brightness over 180 ms with internal hundredths of a percent and scales the 16-bit levels directly. Example: channel 128 gives gamma=14386 (~21.95% light duty); at 50% brightness the level is 7193 (~10.98%). Channel 255 gives 65535 at full brightness; channel 0 or brightness zero gives zero.

`rgb_output.c` translates level/65535 to a 0?100 HAL duty at 1 kHz with explicit inversion for common-anode LED5. All three channels use actual hardware PWM; complementary-pin routing is handled by the inspected HAL. Hardware clock/counter quantization and the gamma lookup reduce effective physical precision, particularly near black. The 24-bit RGB representation remains exact.

## Smooth transitions and demo

Color changes interpolate each encoded RGB channel linearly over 180 ms, using signed intermediates. Gamma is applied after interpolation. A new touch target starts from the current interpolated color, avoiding a jump back to a previous target. Ordinary release retains the selection. An endpoint is exact when elapsed time reaches the duration; zero duration selects the destination immediately. Timestamps use unsigned subtraction so normal tick wrap is handled. Durations are bounded to 10 seconds in the application.

Demo mode cycles through all 30 named presets. Its default transition interval is 2000 ms. The slider sets `300 + position * 9700 / 1000` milliseconds (300?10000 ms). A speed change affects when the next target is selected and the duration of subsequent fades; the active fade is not immediately rescaled. B1 exits demo without waiting for the fade. Demo includes neutral colors and black.

## Custom RGB values

Mode 4 selects and confirms entries in this firmware array:

```c
const rgb_t custom_presets[] = {
    {255, 0, 0}, {0, 255, 0}, {0, 0, 255}, {18, 52, 86},
    {255, 105, 180}, {128, 0, 255}, {255, 214, 170}, {214, 232, 255}
};
```

Edit `firmware/color_engine.c`, rebuild and reflash to customize these values. The controller derives the array length automatically and maps the slider across the available entries. Presets and settings are kept in RAM/flash constants; user settings are not written to nonvolatile storage.
