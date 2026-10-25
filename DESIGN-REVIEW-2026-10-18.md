# Design review: design3-compact thermostat (2026-10-18)

This review covers `thermostat.kicad_sch` (Oct 16) and `thermostat.kicad_pcb` (Oct 11).

**Method.** I extracted the netlists with scripts, compared the schematic with the PCB pad by pad, and checked copper connectivity, courtyards, track widths and silkscreen. I also checked datasheet limits and re-ran one triac channel in ngspice with inductive loads. The installed KiCad is 6.0.2 and cannot open these KiCad 10 files, so ERC and DRC were **not** run. Re-run both in KiCad 10 after acting on this list.

Items are ordered by severity. Nothing in the schematic or PCB has been changed. Every item here is a suggestion for you to decide on.

---

## A. Blocking: fix before ordering boards

### A1. The DS18B20 data line is not connected to the Xiao
**Status: done in the schematic (2026-10-18).** The SPARE channel is removed (Q8, U11, R26–R28, C12) and `1WIRE` now goes to J7 pin 7 (D7/GP1). Update PCB from Schematic, then route that pad. J5 pin 4 is flagged no-connect for now.
The `1WIRE` net contains only J8 pin 2, R4 and U3 pin 2. No Xiao pin is on it, so neither the on-board sensor nor the outdoor sensor can be read.

All 11 Xiao I/O pins are already in use:

| Pin | Use |
|---|---|
| D0–D3 | G, Y1, Y2, OB |
| D4, D5 | I²C |
| D6 | TX |
| D7–D10 | SPARE, E, W1, W2 |

A schematic note still reads "DS18B20 (1-Wire) on GP26". That comes from the old Pico design, where GP26 was free. On the Xiao, GP26 is D0, which now drives G.

Options:
- **(Recommended)** Move `1WIRE` to D6 (GP0) and drop the `TX` net and the TX1 test point. Debug output can go over USB serial instead.
- Free D7 by dropping the SPARE channel (Q8, U11, R26–R28, C12).
- Add a DS2484 I²C-to-1-Wire bridge on the existing I²C bus. This costs one more chip.

### A2. The PCB is out of date for +3V3 on the pull-ups and the on-board DS18B20
**Status: root cause found and fixed in the schematic (2026-10-18).** This was not a stale PCB. The schematic's `+3V3` and `+5V` power symbols had a power *output* pin, and KiCad only names a net from a power *input* pin, so those symbols never connected anything. The J7/J8 `+3V3` and J7 `+5V` connections were local labels (net `/+3V3`), which are also a different net from a global power net. Fixed by making both symbols' pins power inputs, turning those three labels into global labels, and adding a PWR_FLAG on +3V3. The same defect meant U12's output and C14 were **not** connected to the Xiao 5V pin (J7 pin 1); my earlier "verified" note for that was wrong, because my own netlist script merged nets by name. Verified now with KiCad 10's own netlist export (`kicad-cli`). Run Update PCB from Schematic again.

(Original finding, for reference:)
On the PCB, these pads are not on `+3V3`:
- **R1 pad 1 and R2 pad 1** (the I²C pull-ups) are on `Net-(R1-Pad1)`, which only joins R1 to R2. As a result, SDA and SCL have no pull-up.
- **U3 pin 3 (VDD)** is on `Net-(U3-VDD)`, which has no copper at all, so the on-board DS18B20 is unpowered.

The schematic has all three on `+3V3`. Run *Update PCB from Schematic*, then route these three pads to +3V3.

### A3. The J3 silkscreen labels are shifted by one pin
The board text "G / 3V / SDA / SCL" sits at y = 89.5, 92, 94.5 and 97. The J3 pads are at y = 92.5 (GND), 95.0 (+3V3), 97.6 (SDA) and 100.1 (SCL). Each label therefore sits about one pin above the pad it names, and "3V" is beside the GND pad. Move the labels down by about 3 mm so each lines up with its pad.

### A4. The field terminals have no silkscreen labels
None of J1, J4, J5, J8 or JP1 has board text identifying its terminals, such as C, Rc, G, Y1, Y2, O/B, W1, W2, E, SPARE, Rh, or 3V3/DQ/GND. These terminals are where an installer connects HVAC wires. A mislabelled or unlabelled terminal is the most likely way this board gets damaged, because 24 VAC into J8 would destroy the Xiao. Add a label at every terminal, and a short note at JP1 such as "fit for single-transformer systems".

### A5. The Xiao 5 V pin is USB VBUS: add a diode
On the XIAO RP2040, the 5V pin is wired straight to USB VBUS. If USB is plugged in while the board is powered, the 7805 and the PC's USB port drive each other. Seeed's guidance is to put a diode between the external 5 V source and the 5V pin.

Add a Schottky diode (1N5817 or 1N5819, THT) from `+5V` to J7 pin 1, with the cathode at the Xiao. The Xiao then sees about 4.6–4.7 V, which is fine for its 3.3 V LDO. See also B1, which is a second reason USB is risky on this board.

---

## B. Strongly recommended: design and safety

### B1. Logic GND is not at C potential, because of the full bridge
**Status: done in the schematic (2026-10-18).** BR1 is replaced by D1 (1N4007, DO-41) from fused Rc to `VRECT_DC`; C (J1 pin 1) and logic GND are now one net. The old `C_24VAC_RTN` net no longer exists. Simulated from the schematic: `VRECT_DC` 26.2–33.3 V, +9 V 8.94 V, +5 V 5.00 V.

With a full bridge, logic `GND` equals C minus about 0.7 V on one half-cycle. On the other half-cycle it equals Rc minus about 0.7 V, which is about 34 V below C. So relative to C (and to earth, since most furnaces bond C to chassis), the logic GND carries a **34 V-peak half-wave at 60 Hz, about 17 V rms**.

Consequences:
- **USB to an earth-grounded PC** (a desktop, or a laptop on its charger) shorts that waveform through one bridge diode and F1. That puts current through the USB ground, the PC port and the Xiao until the PTC trips.
- **The outdoor DS18B20 cable** (J8) and **the M5Stack Dial** (J9) are on the same swinging GND. Long outdoor cable plus 60 Hz common-mode swing means noise and surge exposure. A capacitive touch screen whose ground moves 34 V relative to the user's body is also a known way to get erratic touch.
- The schematic note "Keep logic GND separate from AC hot R_BUS; isolation via MOC3063" suggests the logic side is isolated. With the bridge, it is not.

**Suggested fix:** replace the bridge with a **half-wave rectifier**: one 1N4007 from fused Rc, with logic `GND` tied directly to `C_24VAC_RTN`. Many commercial thermostats use this arrangement.
- **Corrected numbers (ngspice, 24.1 VAC, constant-power load of 0.9–1.4 W into U1; the first version of this item overstated the ripple):**

  | Rectifier | C3 | Peak | Minimum | Ripple p-p |
  |---|---|---|---|---|
  | Full bridge | 100 µF | 33.0 V | 30.0 V | 3 V |
  | Half-wave | 100 µF | 33.5 V | 26.7 V | 6.8 V |
  | Half-wave | 220 µF | 33.2 V | 30.2 V | 3 V |

- Ripple roughly doubles for the same capacitor, but the minimum input is still about 27 V against the R-78HB9's 14 V minimum. **100 µF is enough**; 220 µF only matches today's ripple and is optional.
- **The peak does not go down.** It is set by the 34 V AC amplitude, and a half-wave rectifier has one diode drop instead of two, so the peak is about 0.5 V *higher*. Nothing downstream can be downsized: C3 (63 V), U1 (72 V max) and the TVS clamp all see the same voltage. The saving is one part (BR1 becomes a 1N4007).
- The MOC3063s are still needed, because the triacs are referenced to Rc and Rh, not to C.
- This change also makes USB debugging much safer, though A5 still applies.
- The DC drawn from the transformer is negligible for a typical 40 VA HVAC transformer.

**Quick bench check of the current design:** with the board powered from 24 VAC, put a meter on AC volts between J8 pin 3 (GND) and the C terminal. A full bridge should read about 15–17 VAC. A half-wave design with GND = C would read 0.

### B2. Total GPIO current exceeds the RP2040 limit
Each MOC LED draws (3.3 − 1.2 V) / 220 Ω ≈ 9.5 mA. The RP2040 allows **50 mA total** across all GPIO (the IOVDD limit), and the default pad drive is 4 mA, at which VOH sags.

| Channels on | Total current | Within 50 mA limit? |
|---|---|---|
| 4 (e.g. G + Y1 + Y2 + O/B) | ≈ 38 mA | Yes |
| 6 | ≈ 57 mA | No |
| All 8 | ≈ 76 mA | No |

The MOC3063 needs at least 5 mA (IFT max).

Suggested fix:
- Change R5, R8, R11, R14, R17, R20, R23 and R26 to **270 Ω**, which gives about 6–7 mA each.
- In firmware, set those pins to 8 mA drive strength.
- In firmware, never energise more than about 5 channels at once. A real thermostat never needs more than that.

If you want headroom for all 8 channels, drive the LEDs from +5V through a ULN2803 or small NPN transistors instead.

### B3. Zero-cross MOC3063 with inductive loads: needs a bench test
HVAC loads (contactor coils, fan relays, gas valves) are inductive. With a zero-cross driver, the main triac turns off at *current* zero, when the line voltage is already well above zero. The MOC3063 will not re-trigger above its inhibit voltage, which the datasheet gives as **VINH 5–20 V**. That can cause missed half-cycles, which show up as humming, chattering or a DC component in the coil.

**What I tried:** I re-ran the existing `relay_test.cir` channel in ngspice with three loads:
- 60 Ω resistive;
- a relay coil at PF 0.7 (56 Ω + 0.21 H);
- a contactor at PF 0.4 (32 Ω + 0.194 H).

I ran each with VINH at 15 V and at 5 V, and with and without the snubber. Every case conducted fully: the triac carried about 0.6 V rms and the load got the expected rms current. **That result is not trustworthy.** The behavioural MOC model re-fires instantly while the voltage passes through the window. Real devices have finite response times, so the model cannot settle this question in either direction.

The 100 Ω + 10 nF snubber slows the voltage rise after commutation, which helps in reality.

**Recommendation:** bench-test one channel with a real 24 VAC contactor or relay. The MOCs are socketed, so the fallback is a direct swap to a **random-phase MOC3023** (same DIP-6 pinout, IFT 5 mA, 400 V). Random-phase triggering at 24 VAC causes no meaningful EMI.

### B4. The on-board DS18B20 will read high
U3 sits about 6 mm from the Xiao, about 13 mm from the 7805 and about 16 mm from the R-78HB. The board dissipates roughly:
- 0.3 W in the 7805;
- about 0.4 W in the R-78HB;
- up to about 0.5 W per energised triac.

In a closed wall enclosure, expect the reading to be several °C high, and to shift depending on which outputs are on. Options:
- Move U3 to a board edge or corner, ideally at the bottom so heat rises away from it, and cut routing slots around it.
- Or use a remote sensor for room temperature. An SHT4x or SHT31 on the J3 I²C bus also gives humidity, which is useful for HVAC.
- At minimum, plan a firmware calibration offset.

### B5. Track widths
Every track is 0.4 mm, including the 24 VAC buses. `RC_24VAC_UNFUSED` carries the sum of all Rc-side loads, which can reach 1–2 A with contactor inrush. If an installer shorts an output to C, it carries several amps until the furnace's 3–5 A fuse blows. 0.4 mm of 1 oz copper is good for about 1.2 A continuous.

Use **≥ 1.0–1.5 mm** for `RC_24VAC_UNFUSED`, `RH_24VAC`, `C_24VAC_RTN`, the output nets (G, Y1, Y2, OB, W1, W2, E, SPARE) and the triac MT1/MT2 pads.

### B6. Ground copper
The only GND copper is two small zones, about 14 × 3.5 mm on F.Cu and 2 × 10 mm on B.Cu. GND is otherwise routed with 0.4 mm tracks. Add a B.Cu GND pour over the logic area: the Xiao, U1, U12, C3, C13, C14, J3 and J8. This gives the R-78HB switcher and the I²C lines a solid return.

### B7. Protect the field-wired low-voltage connectors
J8 (the outdoor DS18B20, on a long cable that runs outdoors) and J3 bring +3V3 and Xiao I/O off the board.
- Add **100 Ω in series with DQ**, plus a clamp at the connector, for example a 3.6–5.1 V zener or a small TVS to GND.
- Consider a 47–100 Ω resistor or a small PTC in the +3V3 feed to J8. A shorted outdoor cable would otherwise collapse the Xiao's 3.3 V rail.
- On a long 1-Wire run, 4.7 kΩ may need to drop to about 2.2 kΩ.

### B8. Terminal blocks
All field terminals are Xinya XY308 at 2.54 mm pitch with 1.2 mm drill. Thermostat wire is usually **18 AWG solid**. Check that the blocks you buy are rated for 18 AWG, because many 2.54 mm-pitch blocks top out at 20–22 AWG. A 3.5 mm or 5.0 mm pitch block is the usual choice for HVAC wire.

Also consider making J8 a different style or colour, or a keyed connector, so 24 VAC cannot easily end up on it.

### B9. Check USB-C plug clearance
The Xiao's USB-C end faces about x = 106, y = 97. Vertical resistors R5 (100.5, 101.5), R8 (104, 101.5), R17 (100, 94) and R20 (103.5, 94) stand about 9–10 mm tall, directly in front of the port. Check that a USB-C plug's overmold fits, or move those four resistors.

---

## C. Component choices

| Ref | Now | Observation | Suggestion |
|---|---|---|---|
| F1 | Bourns MF-RHT050 (500 mA) | **Vmax is 30 V.** The line is 24.1 VAC (34 V peak) and high line can be 27–28 VAC, so there is little margin. | MF-R050 (60 V, 0.5 A hold, 5.1 mm lead spacing). Check the body outline against the footprint. |
| D7 | P6KE43CA | VRWM is 36.8 V and the peak at 24.1 VAC is 34.1 V, an 8% margin. Conduction starts at about 29 VAC. Fine for your measured supply. | If you ever measure more than 26 VAC, use P6KE47CA. Its 64.8 V clamp then needs **C3 rated ≥ 80 V**. The R-78HB is fine up to 72 V. |
| Q1–Q8 | BT138-600E, 12 A, TO-220 | Oversized for loads under 1 A. The upside is that the ~95 A surge rating survives an output shorted to C. | Keep them, or use BT136 or BT134 if you need space. Do **not** drop to 1 A TO-92 triacs unless you add a PTC on each bus. |
| C3 | 100 µF / 63 V | Fine as is, also with half-wave (B1). | Use ≥ 80 V only if you adopt the 47CA TVS. |
| U1 | R-78HB9.0-0.5 | Input range 14–72 V against about 28–34 V actual. Good margin. | No change. |
| U12 | L7805CV | Dissipates (9 − 5) V × ~80 mA ≈ 0.3 W. Fine. | No change. |
| R5, R8, R11, R14, R17, R20, R23, R26 | 220 Ω | See B2. | 270 Ω |
| U4–U11 | MOC3063, socketed | See B3. | MOC3023 as a fallback. |

---

## D. Architecture questions for you

1. **How do the Xiao and the Dial talk to each other?** The XIAO RP2040 has no Wi-Fi, so presumably the Dial's ESP32-S3 is the networked UI.
   - If **J3 ("Touch I2C") is meant for the Dial's Port A (Grove)**, note that J3 pin 2 is **+3V3**. Port A's VCC is **5 V**, so a standard Grove cable would back-feed 5 V into the Xiao's 3.3 V rail. In that case, either leave pin 2 unconnected on the cable or change J3 pin 2.
   - If J3 is for something else, the communication link to the Dial still needs a home. TX on D6 is the only spare-looking pin, and A1 proposes using it for 1-Wire.
2. **Should the Xiao exist at all?** If the Dial is the brain, an I²C expander such as an MCP23008 could drive the 8 MOC LEDs from the Dial's Port A. That would remove the Xiao and the 7805, and the DS18B20s could go on the Dial's Port B. The reason to keep the Xiao is to have an independent local controller that keeps the HVAC safe if the Dial firmware hangs. Both choices are reasonable. It's a design decision, not a defect.
3. **Rh side (JP1 open, two transformers):** W1, W2 and E switch from Rh. SPARE switches from **Rc** even though its terminal is on J5 with the heat outputs. Check that this is what you intended.

---

## E. Housekeeping

### Schematic
- **Stale text:** "24VAC HVAC thermostat - Raspberry Pi Pico 2 W", "Temperature: DS18B20 (1-Wire) on GP26", and the GND isolation note (see B1).
- **Stale values:** J1 is now "Rc/C" but still says "Rh/Rc/C". J5's value omits Rh.
- **MOC3063 symbol:** pin 4 is named "GATE". In the datasheet, pins 4 and 6 are both main terminals and pin 5 is the substrate (leave it unconnected, as it is now). The wiring is correct because the output is bidirectional, but the pin name is misleading.

### PCB
- Give the four mounting holes references (H1–H4). Right now they are all "REF**".
- The 3D model of BR1 looks offset from its pads in `pcb-3d.png`. This is cosmetic only.

### Project files
- **Stale files:** `ERC.rpt` is from Oct 5. Delete `sim/dbg.cir` and `sim/dbg2.cir`.
- **Simulation:** the sim-only parts (V1, R_TX, R_REF, VG1, R_LH, R_L5, XDIAL1) are correctly marked not-in-BOM and not-on-board. Consider adding a series inductance to R_LH so the KiCad simulation exercises an inductive load (see B3).

### Firmware notes that depend on the hardware
- Set GPIO drive strength (B2).
- Interlock heat against cool, and enforce the O/B polarity setting.
- Enforce a compressor minimum off-time of 5 minutes or more.
- Use the RP2040 hardware watchdog, so a hung MCU drops all outputs.
- On boot, the RP2040 GPIOs come up as inputs, so all outputs are off by default. This is good.

---

## F. Checked and OK

**Pin mappings**
- **Xiao headers:** J6 = D0–D6 and J7 = 5V/GND/3V3/D10–D7. Pin 1 of both rows is at the same (USB) end, and the rows are 15.24 mm apart.
- **Triac drive:** MT1 is on the bus, MT2 is the output, and the gate is fed through the MOC from MT2. This triggers in quadrants I and III (BT138-600E IGT ≤ 10 mA).
- **Triac gate resistor:** 180 Ω limits MOC current to about 190 mA peak, below the MOC's 1 A rating.
- **Parts:** pinouts are correct for the DS18B20 (GND/DQ/VDD), both 3-pin regulators (VIN/GND/VOUT) and the DF04M.

**Circuit values**
- **Snubber leakage:** 10 nF at 60 Hz is about 265 kΩ, so an off output leaks about 90 µA, too little to hold any relay.
- **R-78HB input:** about 28–31 V simulated, against its 14 V minimum and 72 V maximum. The TVS clamp (59 V) is also below 72 V.

**Power rails**
- **+5V:** J7 pin 1, U12 pin 3 and C14 pin 1 are on one net and fully routed.
- **+9V:** J9 pin 1, U1 pin 3, U12 pin 1 and C13 pin 1 are on one net and fully routed.

**PCB**
- **Routing:** apart from the stale +3V3 pads in A2, every PCB net is routed as one connected piece.
- **Placement:** no courtyard overlaps and no parts outside the board edge.
- **Clearance:** the closest different-net track spacing is 0.2 mm, which meets the 0.2 mm rule. That is acceptable at 34 V peak, though wider is better near the terminals.
