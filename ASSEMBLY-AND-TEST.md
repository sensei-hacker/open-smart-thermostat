# Assembly and test guide

Board: design3-compact, 24 VAC HVAC thermostat (XIAO RP2040 + M5Stack Dial). All parts are through-hole and soldered from the bottom.

Build the board in four stages and test after each one. A mistake then shows up while only a few parts are on the board, and the XIAO goes on last so a power-stage fault can't damage it.

## General rules

- **Short parts before tall parts.** In each stage, solder the lowest parts first so the board lies flat on the bench. The rough order is:
  1. Horizontal diodes
  2. Small ceramic caps
  3. DIP sockets or MOCs
  4. Vertical resistors and pin headers
  5. Terminal blocks
  6. Electrolytics, film caps, the PTC fuse and U1
  7. TO-220 parts, which come last
- **Tight spots:** each triac row has vertical resistors 3–5 mm away:
  - Q1–Q4 sit next to R6/R9/R12/R15 and R7/R10/R13/R16.
  - Q5–Q7 sit next to R18/R21/R24 and R19/R22/R25.
  - Solder those resistors before their triac, or the triac body blocks the iron.
- **Pad-to-pour gaps.** Pads near the GND pour have 0.5 mm clearance. The pour pulls heat away, which tempts you to feed in extra solder. Use flux and a fine chisel tip. After each stage, look for bridges with a magnifier and check suspect pads to GND with a meter.
- **Vertical resistors:** the body sits over the pad marked by the silkscreen circle. Bend the other lead down beside it. Keep all resistors facing the same way so you can probe the top lead later.

### Polarity and orientation

| Part | What to check |
|---|---|
| D1, D8, D9, D10 | Cathode band goes to the band on the silkscreen. |
| D7 (P6KE47CA) | Bidirectional, so either way round works. |
| C3, C13, C14 | Electrolytics: + lead goes to the + pad, which is the square pad. |
| U1 (K7805) | Pin 1 = Vin (VCLAMP), pin 2 = GND, pin 3 = 5 V out. Match the printed side to the silkscreen. |
| U4–U10 (MOC3063) | The pin 1 dot or notch goes to the square pad and silkscreen notch. |
| Q1–Q8 (TO-220) | Match the tab side to the silkscreen line. Stand them straight. |
| U3 (DS18B20) | The flat face matches the silkscreen flat. |
| J1, J4, J5, J8 | Wire openings face the board edge. Check this against a real XY308 before soldering. |
| J9 | Pin 1, marked "5V", is +5 V. Pin 2 is GND. |
| XIAO | USB-C end toward the "USB" outline, pin 1 = 5V / D0. |

### Safety notes

- **The triac tabs are live.** Each BT138 tab is MT2, which is that triac's output terminal and carries 24 VAC. Tabs must not touch each other, a heatsink or the case.
- **Q8's tab is the collector**, which is VRECT, up to about 41 V DC.

## Do some parts act as vias, and must channels go in a set order?

Electrically, no. Every hole is plated, so the copper barrel connects the top and bottom layers whether or not a part is fitted. JLC also tests bare boards electrically.

These holes are where tracks change layer through a part's pad, all of which work with the part missing:

| Net | Hole |
|---|---|
| Rc bus | Q1 pin 1 |
| GND | U4 pin 2, C3, C14, F1 |
| +5V | C14 |
| G | C5 |
| W1 | C9 |
| W2 | C10 |
| +3V3 | J3 pin 2 |
| VRECT | C3 |
| Q8 base | Q8 pin 1 |

Don't drill out or overheat these holes.

These are the real dependencies:

| Needs | Why |
|---|---|
| **All channels** need stage 1 (J1, F1, D1). | J1 brings in Rc and C. F1 links C to GND. |
| **W1, W2 and E** need **JP1 fitted** (for one transformer) or a wire on J5's **Rh** terminal (for two transformers). | They switch Rh, not Rc. |
| **All channels** need a 24 VAC source to test. | A triac only turns off on AC, so a DC supply will latch it on. |

### Channel map

| Channel | Triac | MOC | LED R | Gate R | Snubber | Terminal | Switches from | XIAO pin | RP2040 GPIO |
|---|---|---|---|---|---|---|---|---|---|
| **G** (fan) | Q1 | U4 | R5 | R6 | R7 + C5 | J4.1 | Rc | D0 | GP26 |
| Y1 | Q2 | U5 | R8 | R9 | R10 + C6 | J4.2 | Rc | D1 | GP27 |
| Y2 | Q3 | U6 | R11 | R12 | R13 + C7 | J4.3 | Rc | D2 | GP28 |
| O/B | Q4 | U7 | R14 | R15 | R16 + C8 | J4.4 | Rc | D3 | GP29 |
| W1 | Q5 | U8 | R17 | R18 | R19 + C9 | J5 "W1" | Rh | D9 | GP4 |
| W2 | Q6 | U9 | R20 | R21 | R22 + C10 | J5 "W2" | Rh | D10 | GP3 |
| E | Q7 | U10 | R23 | R24 | R25 + C11 | J5 "E" | Rh | D8 | GP2 |

**Build and test G first.**
- It's on the Rc side, so it doesn't need JP1.
- It's nearest the power section.
- Its Rc feed passes through the Q1 pin 1 hole, so testing it also proves the Rc bus.
- A fan relay is the safest real load to energise.

**Then Y1, Y2, O/B, and finally W1, W2, E** after fitting JP1.

## Stage 0: bare board

1. Look over the board for anything odd in the copper or mask.
2. Measure resistance between these pad pairs. Each should be open on a bare board:
   - J1 Rc to J1 C
   - Rc to GND
   - each J4 and J5 pad to its neighbour

## Stage 1: power supply

Solder these, short to tall:

| Order | Parts |
|---|---|
| 1 | D1, D7, D8, D9, D10 |
| 2 | C2 |
| 3 | R28 |
| 4 | J9 header |
| 5 | J1 |
| 6 | F1, C13, C14, C3, U1 |
| 7 | Q8 |

D8 and D9 aren't needed yet, but they're among the lowest parts and sit near Q8 and J8, so this is the easiest time to fit them.

**Checks with no power:**
- C3 + to GND: not a short. It charges up on the meter.
- C13 + to GND: not a short.
- C14 + to GND: not a short.

**First power-up: current-limited DC, if you have a bench supply.**
1. Set the supply to 30 V with a 100 mA limit.
2. Connect + to J1 **Rc** and − to J1 **C**.
3. Expected readings:

| Measure | Expected |
|---|---|
| Input current | Under 20 mA |
| C3 + (VRECT) | About 29.3 V |
| C13 + (VCLAMP) | About 27 V, about 2.4 V below VRECT |
| C14 + (+5V) | 4.9–5.1 V |
| Q8 temperature | Barely warm |

**Then 24 VAC, from the HVAC transformer or a bench 24 VAC transformer:**

| Measure | Expected |
|---|---|
| VRECT | 26–41 V depending on load and line. It's higher with nothing connected. |
| VCLAMP | Never above about 29 V |
| +5V | 4.9–5.1 V |

## Stage 2: channel G

Solder these, short to tall:

| Order | Parts |
|---|---|
| 1 | U4, or its socket |
| 2 | R5, R6, R7 |
| 3 | J4 |
| 4 | C5 |
| 5 | Q1 |

**Test without the XIAO.** It isn't fitted yet, so it's safe to drive the LED from +5V by hand.
1. Connect a test load from J4 G to J1 C. Use one of these:
   - a 24 VAC relay or contactor coil (best)
   - a 220 Ω 5 W resistor, which draws about 110 mA
2. Apply 24 VAC.
3. **Off:** the voltage across the load should be under 2 VAC. That's snubber leakage, and a relay must not hold in.
4. **On:** briefly jumper **J9 pin 1 (+5V)** to the **J6 pin 1 hole** (GP_G).
   - About 17 mA flows through R5. MOC3063 needs 5 mA maximum and allows 60 mA.
   - The load should get the full 24 VAC, and a relay should pull in cleanly.
5. Remove the jumper. The load must drop out within half a cycle.
6. Switch the relay on and off 20 times. It should never stick on and never chatter.

> **Never do this jumper test once the XIAO is fitted.** 5 V on an RP2040 pin damages it.

## Stage 3: the other six channels

Solder each channel's parts in the same order as G: MOC, then resistors, then film cap, then triac.

1. Do **Y1, Y2 and O/B** first. Test each with the same jumper method, connecting +5V to the J6 pin 2, 3 and 4 holes.
2. Fit **JP1** with the jumper cap, or wire Rh.
3. Do **W1, W2 and E.** Their GPIO holes are J7 pins 5, 4 and 6. Their loads go from the J5 terminal to J1 C.
4. While each channel is on, check that the **other** outputs stay off.

## Stage 4: logic, sensors, and the XIAO

Solder these, short to tall:

| Order | Parts |
|---|---|
| 1 | C15 |
| 2 | R1, R2, R4, R26, R27 |
| 3 | J3, J6/J7 headers |
| 4 | J8 |
| 5 | U3 (DS18B20) |
| 6 | XIAO (last) |

- **U3:** solder it quickly, since it's the on-board temperature sensor. Leave about 3 mm of lead under the body to keep it a little away from board heat.
- **XIAO:** solder the headers into the board first, then sit the XIAO on top and solder it. This keeps the header pins straight.

**Checks:**
1. Power from 24 VAC with the XIAO's USB **unplugged**.
2. Check 3V3 at J3 pin 2: 3.2–3.4 V.
3. Check 5 V at J7 pin 1: about 4.6–4.8 V, which is +5V minus D8's drop.
4. Plug in USB. The XIAO must still enumerate, and D8 blocks USB 5 V from flowing back into +5V.
5. Load the test firmware (below). Read the U3 DS18B20 and the J8 probe if fitted. Scan I2C on J3 if a humidity module is plugged in.

## Firmware: GPIO drive strength must be 12 mA

The RP2040's default pin drive is 4 mA. At that setting the pin voltage sags under the MOC LED and the LED gets only about 5 mA. That's the MOC3063's worst-case trigger current (IFT), so it would be unreliable.

At 12 mA drive each LED gets about 8–9 mA:
- Measure about 1.8–2.0 V across the 220 Ω LED resistor when the channel is on.
- If you see about 1.1 V or less, the drive strength isn't set.

**Arduino (arduino-pico core) or the Pico SDK:**
```cpp
#include "hardware/gpio.h"
// G, Y1, Y2, O/B, W1, W2, E
const uint OUT_PINS[] = {26, 27, 28, 29, 4, 3, 2};
for (uint p : OUT_PINS) {
  digitalWrite(p, LOW);  // set low before switching to output
  pinMode(p, OUTPUT);
  gpio_set_drive_strength(p, GPIO_DRIVE_STRENGTH_12MA);
}
```

**MicroPython, on recent rp2 builds:**
```python
from machine import Pin
OUT = {name: Pin(gp, Pin.OUT, value=0, drive=Pin.DRIVE_3)  # DRIVE_3 = 12 mA
       for name, gp in (("G", 26), ("Y1", 27), ("Y2", 28), ("OB", 29),
                        ("W1", 4), ("W2", 3), ("E", 2))}
```

### Other firmware rules the hardware relies on

- **Outputs start low.** RP2040 pins come out of reset as inputs with pull-downs, so nothing fires during boot. Set each pin low before making it an output, as above.
- **No more than 5 outputs on at once.** The RP2040 allows about 50 mA total from its GPIO pins, and 5 × 9 mA is within that. Real HVAC use needs at most 4.
- **Interlocks:**
  - Never Y1/Y2 together with W1/W2/E.
  - Compressor (Y1/Y2) minimum off time of about 5 minutes.
  - O/B set before Y1 turns on.
- **Keep working without the Dial.**
  - Use a watchdog.
  - If the Dial is silent for N seconds, fall back to a safe setpoint using U3.
  - If the sensor fails, turn all outputs off.

## Install

1. Turn off HVAC power at the furnace or air handler.
2. Wire the terminals:
   - J1: C and Rc
   - J4: G, Y1, Y2, O/B
   - J5: W1, W2, E, Rh
   - JP1 fitted for one transformer, removed for two. Check what your system has.
3. Connect the Dial through the J9 USB-C pigtail. Check red = 5 V with a meter first.
4. Mount the board with the DS18B20 (U3) away from the regulator corner and from any wall heat.
