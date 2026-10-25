# Design re-review, 2026-10-20

Scope: `thermostat.kicad_sch` and `thermostat.kicad_pcb` as of 2026-10-19 00:46, after all the fixes from `DESIGN-REVIEW-2026-10-18.md`. Nothing was changed during this review.

How it was checked:
- KiCad 10 `kicad-cli` ERC, netlist export, and DRC with schematic parity.
- A net-by-net read of the netlist.
- Rendered schematic, copper and silkscreen images, plus a 3D render.
- An ngspice sweep of the half-wave supply.

## Summary

The circuit is now electrically consistent:
- ERC shows no errors.
- DRC shows 0 unconnected pads, no clearance violations, and the schematic and PCB match.
- Every net I traced is correct (list at the end).

The remaining problems are mostly mechanical and about margins, not wiring:
- Terminal block orientation.
- No mounting holes.
- The supply capacitor is too small for a realistic Dial load.
- Temperature-sensor placement.
- The J8 clamp voltage.

---

## A. Fix before ordering boards

### A1. J5 (and J8) terminal blocks probably open into the board
All four field blocks (J1, J4, J5, J8) use the same footprint at the **same rotation (0°)**. J1 and J4 sit on the bottom edge (y = 143, edge at 148). J5 sits on the top edge (y = 54, edge at 50).
- **The problem:** two blocks with the same rotation on opposite edges cannot both open outward.
- **Which way they open:** in this footprint the pin-1 chamfer and the double "front" lines are on the +y side, so the wire openings face +y (down). J1 and J4 are then correct.
- **J5's openings:** they face down into the board, about 3 mm from the Q5–Q7 triac row. That leaves no room for wires.
- **J8's openings:** it sits in the middle of the board (90.4, 91.5), and its openings face U3, D9 and R1/R2.
- **Fix:** check in the KiCad 3D viewer. The XY308 model did not load in my command-line render, so I couldn't confirm visually. Then rotate J5 180°, and move J8 to a board edge (the left edge near J9 is natural), opening outward.

### A2. No mounting holes
The board (63 × 98 mm) has no mounting holes. A wall thermostat needs at least 2, better 4, for example M3 (3.2 mm) in the corners. Space is tightest at the top-left and bottom-left, near U1, C3 and D1.

### A3. C3 (100 µF) is too small if the Dial draws more than about 0.5 W
The earlier simulation assumed the Dial draws a constant 0.52 W. I don't have a measured figure for the M5Stack Dial. An ESP32-S3 with Wi-Fi and the round display could plausibly draw 1–2.5 W at peaks.

I swept the half-wave supply: 1N4007, C3, R-78HB9 model, 7805 with an 80 mA load, transformer source resistance 1.5 Ω. Columns: VAC is the line voltage, Dial is the Dial load, VRECT is the min–max rectified voltage, and +9V min is the converter output minimum.

| VAC | C3 | Dial | VRECT min–max | +9V min | Source current, rms |
|---|---|---|---|---|---|
| 21.6 (−10%) | 100 µF | 0.52 W | 21.8–29.9 V | 8.94 V | 0.17 A |
| 21.6 | 100 µF | 1.5 W | **14.0**–29.8 V | 8.90 V | 0.30 A |
| 21.6 | 100 µF | 2.5 W | **11.0**–29.8 V | **4.4 V (drops out)** | 0.36 A |
| 24.1 | 100 µF | 2.5 W | **11.8**–33.3 V | **6.8 V (drops out)** | 0.40 A |
| 21.6 | 220 µF | 2.5 W | 20.0–29.5 V | 8.85 V | 0.41 A |
| 24.1 | 220 µF | 2.5 W | 24.8–33.1 V | 8.85 V | 0.37 A |
| 21.6 | 470 µF | 2.5 W | 24.7–29.0 V | 8.85 V | 0.41 A |

The R-78HB9.0 needs about 12–14 V in, so 100 µF only works if the Dial stays near 0.5 W.

- **Recommendation:** 220 µF / 63 V, 105 °C, low-ESR (10 mm diameter, 5 mm pitch: `CP_Radial_D10.0mm_P5.00mm`). Use 330–470 µF if there's room.
- **Ripple current:** a 100 µF / 63 V part is typically rated around 0.2–0.3 A at 120 Hz. The bigger capacitor also handles the 0.3–0.4 A ripple current better.
- **Better still:** measure the Dial's current at 9 V (idle, Wi-Fi transmitting, backlight full) and size from that.

### A4. Field terminals still have no per-pin labels
- **What's there:** J3's silkscreen is now correct (G / +3V3 / SDA / SCL, aligned). J1, J4, J5 and J8 show only their value text.
- **What's needed:** labels at each pin: `C Rc` (J1), `G Y1 Y2 O/B` (J4), `W1 W2 E Rh` (J5), `3V3 DQ GND` (J8), and a note at JP1 ("fit for 1 transformer").
- **Wrong value text:** J4's value reads **"Outputs G/OB"**, but the block carries G, Y1, Y2 and O/B. It should read "Outputs G/Y1/Y2/OB".

### A5. D8 sits under the Xiao
D8 (DO-41, about 2.7 mm diameter) is at (107–117, 93.5), between the J6 and J7 header rows, so it sits under the Xiao. Whether that works depends on how the Xiao is mounted:
- **Female sockets** (the schematic symbol is `Conn_01x07_Female`, about 8.5 mm tall): fine.
- **Soldered to male pin headers:** the Xiao sits about 2.5 mm above the board, and D8 hits its underside.

Decide which mounting you'll use. If it's soldered, move D8 out from under the module, for example beside J7 pin 1.

---

## B. Strongly recommended

### B1. On-board DS18B20 (U3): reading high is now more likely
U3 is at (94.8, 97.6):
- about 12 mm from the 7805 (U12, about 0.3 W)
- about 17 mm from the R-78HB (U1, about 0.3 W loss)
- in the middle of the board.

The B.Cu GND pour I added on 2026-10-19 now ties U3's GND leg to the GND pins of U1, U12 and C3 with solid copper. A TO-92 DS18B20 senses largely through its leads, so this makes the self-heating error worse.

When heating or cooling runs, the triacs add about 0.2–0.5 W each.

Options, best first:
1. Treat the outdoor/remote sensor as the control input, or put the room sensor on a short flying lead at the enclosure's bottom vent.
2. Move U3 to the coolest board edge, away from U1, U12 and the triac rows. Add a zone keepout around it, connect its GND with a thin track, and consider a routed slot to isolate it thermally.
3. At minimum, add a pour keepout of about 5 mm around U3, and calibrate an offset in firmware.

### B2. J8 data clamp D9 (5.1 V) is above the RP2040's limit
The RP2040's absolute maximum on an I/O pin is IOVDD + 0.5 V, about 3.8 V. The pins are not 5 V tolerant.
- **What D9 does now:** it clamps the cable side at about 5.1–6 V, so a transient pushes roughly (5.5 − 3.8) / 100 Ω ≈ 17 mA through R27 into the pin's internal protection diode. That's survivable for a short spike, but it isn't real protection.
- **Better: steering diodes.** Use two small Schottkys on the connector side of R27: one from DQ to +3V3 (for example BAT85, DO-35 THT) and one from GND to DQ. This clamps DQ to about −0.3 / +3.6 V. Keep R27.
- **Alternative:** a low-capacitance 3.3 V TVS. Avoid a 3.3–3.6 V zener: its leakage at 3.3 V would load the 4.7 kΩ pull-up.
- **24 VAC wired onto J8:** this destroys R26 or R27 and probably the Xiao, whatever clamp is used. The practical defence is a connector that 24 VAC wiring can't go into (see B8).

### B3. Set GPIO drive strength in firmware
At reset the RP2040's GPIO drive strength is 4 mA. At that setting a pin driving 270 Ω and the MOC's LED delivers roughly 6 mA, not the 8 mA calculated earlier. The MOC3063 needs 5 mA (its maximum trigger current at 25 °C), and more when cold or as the LED ages.

Set the output pins to 8 mA or 12 mA drive:
- Pico SDK: `gpio_set_drive_strength(pin, GPIO_DRIVE_STRENGTH_12MA)`
- MicroPython: `Pin(..., drive=Pin.DRIVE_3)`

Four outputs on at once is then about 32 mA, within the 50 mA chip total.

### B4. USB while wired: logic GND is C
With the half-wave supply, logic GND is the transformer's C wire, and USB GND is earthed through a desktop PC (or a laptop on its charger).
- **C earthed at the furnace (most common):** harmless.
- **R side earthed, or Rc and C swapped at J1:** the transformer is shorted through the USB cable and the PC.

During development, either power the board from a bench supply with no HVAC wiring, or use a USB isolator.

### B5. USB-C plug clearance (from the last review, still open)
The Xiao's USB end faces about x = 105, y = 97. Vertical resistors R5 (100.5, 101.5), R8 (104, 101.5), R17 (100, 94) and R20 (103.5, 94) stand about 9–10 mm tall, and U3 is directly in line at (94.8, 97.6). A USB-C plug's overmold (about 12 × 6.5 mm) probably won't fit.
- **Fix:** move those four resistors aside, which would also help B1.
- **Or:** accept that USB is for bench use only, with the Xiao unplugged from the board.

### B6. F1 margin under a heavy Dial load
- **The figures:** at 2.5 W the rms current through F1 is about 0.4 A, against a 0.5 A hold current at 23 °C. Hold current falls to roughly 0.4 A at about 50 °C, which is plausible inside an enclosure with the regulators running.
- **What to do:** if the Dial's measured draw is high, use the MF-R075 (0.75 A hold, same 60 V MF-R family). Confirm the voltage rating on the datasheet before ordering.

### B7. Output tracks under a short circuit
Output tracks (G, Y1, Y2, O/B, W1, W2, E) are 0.4 mm. That's fine for 0.5 A, but an output shorted to C pulls about 3–5 A until the furnace's 3–5 A fuse blows. That can take tens of seconds at moderate overload, and 0.4 mm at 5 A runs very hot.
- Widen the open runs to 0.6–0.8 mm where clearance allows. The 0.5 mm attempt only failed at a few pinch points: near R22, near the Q3 gate, and near the U5/U7 snubber legs.
- Or accept the risk, as many commercial thermostats do.

### B8. Terminal blocks (from the last review, still open)
- **Wire gauge:** the Xinya XY308 at 2.54 mm pitch is generally rated about 26–20 AWG. HVAC thermostat wire is 18 AWG solid. Check the exact part you'll buy, or switch to 3.5 mm or 5.0 mm pitch blocks.
- **J8:** give it a different style or colour, or use a keyed plug, so 24 VAC can't go in.
- **Moving or rotating blocks:** if you change blocks, recheck A1.

### B9. Dial power header J9 isn't keyed
J9 is a plain 2-pin 2.54 mm header carrying +9 V, so a reversed plug feeds the Dial backwards. Use a keyed connector (for example JST-XH 2-pin) or whatever connector the Dial's DC input takes. Also confirm the Dial's DC input range: 9 V is assumed.

### B10. MOC3063 zero-cross bench test (from the last review, still open)
The circuit is the standard arrangement:
- **MOC between MT2 and the gate:** the MOC's terminal 4 is on the output and terminal 6 goes through 180 Ω to the gate.
- **Gate quadrants:** gate current flows in quadrants 1 and 3 only, avoiding quadrant 4.
- **Snubber:** 100 Ω + 10 nF across each triac. It leaks about 0.1 mA at 60 Hz, too little to falsely trigger high-impedance furnace inputs.

It still needs a bench test with real contactor and reversing-valve coils before the boards are committed. The MOC3023 (no zero-cross) is the fallback.

### B11. Minor parts
- **C2:** 0.1 µF with no voltage rating given. Specify ≥ 100 V, because VRECT reaches 33–39 V and TVS transients can reach about 59 V.
- **U3:** add a 100 nF decoupling capacitor at VDD. Optionally add one at the J8 side of R26 as well.

---

## C. Housekeeping

Schematic:
- **Title blocks:** the schematic and PCB title blocks still say "HVAC Thermostat – Raspberry Pi Pico 2 W", dated 2024.
- **J8 area:** it's cluttered from my 2026-10-18 edit:
  - R26 and D9 overlap J8's body, and wires cross its symbol.
  - U3's power-pin text overlaps "+3V3".
  - R1/R2's values overlap `#PWR021`/`PWR_FLAG`.

  The connections are correct, but it's hard to read. Spread these parts out in Eeschema.
- **Leftover parts:** `#PWR01` and `#FLG04`, an isolated GND symbol and power flag near (260, 98), can be deleted.
- **Label warning:** ERC's `same_local_global_label` comes from a local `GND` label on J7 pin 2 at (190.5, 189.2). Replace it with a GND power symbol.
- **Library warnings:** 238 `endpoint_off_grid` warnings (cosmetic) and 95 `lib_symbol_issues`, because the project has no `sym-lib-table` entry for the `thermostat` library. The symbols are embedded, so this only matters if you use "Update symbols from library".

PCB:
- **3D models:** many footprints have no 3D model in the 3D render (terminal blocks, triacs, MOCs, most resistors and capacitors), so a collision check in the 3D viewer is incomplete.
- **Footprint mismatches:** the footprints differ from current KiCad library copies. Harmless, but "Update footprints from library" would change them.
- **J5 reference text:** it sits over the board edge (the `silk_edge_clearance` warning at 106.3, 49.8).
- **U3 thermal warning:** `starved_thermal` at U3's GND pad, from the pour. It goes away if you add the keepout in B1.
- **Design rules:** the minimum clearance is set three ways: 0.3 in the board setup, 0.2 in the custom rules file, 0.254 in the default net class. Pick one. 0.2 mm is fine at 24 VAC.

Project folder:
- `ERC.rpt` (Oct 5) and `pcb-3d.png` (Oct 11) are stale.
- `sim/dbg.cir` and `sim/dbg2.cir` are scratch files.
- `thermostat.kicad_sch.before-fp-flag-fix` sits in the project root instead of `thermostat-backups/`.

---

## D. Checked and correct

**Power path:** Rc → F1 → D1 → VRECT_DC, with C3 and C2 to GND (= C). Then U1 (R-78HB9.0) → +9V (C13), which feeds J9 (the Dial) and U12 (7805) → +5V (C14) → D8 → J7 pin 1 (Xiao 5V).
- With USB plugged in, D8 blocks backfeed into the 7805.
- D7 (P6KE43CA) clamps Rc to C.

**Triac channels (×7):**
- Each GPIO drives the MOC LED through 270 Ω, and the LED cathode goes to GND.
- MOC pin 4 goes to the output, and pin 6 goes through 180 Ω to the triac gate.
- Triac MT1 is on the bus: Rc for G, Y1, Y2 and O/B, Rh for W1, W2 and E. Triac MT2 is on the output.
- Each output has a 10 nF + 100 Ω snubber across the triac.
- The MOC no-connect pins 3 and 5 are left open, which is correct (pin 5 is the substrate).

**JP1** links Rh to Rc. J5 pin 4 is Rh.

**Xiao pin map:**

| Signal | Xiao pin | RP2040 pin | Header pin |
|---|---|---|---|
| G | D0 | GP26 | J6.1 |
| Y1 | D1 | GP27 | J6.2 |
| Y2 | D2 | GP28 | J6.3 |
| O/B | D3 | GP29 | J6.4 |
| SDA | D4 | GP6 | J6.5 |
| SCL | D5 | GP7 | J6.6 |
| TX (test point TX1) | D6 | GP0 | J6.7 |
| 1-Wire | D7 | GP1 | J7.7 |
| E | D8 | GP2 | J7.6 |
| W1 | D9 | GP4 | J7.5 |
| W2 | D10 | GP3 | J7.4 |

- All outputs default to pulled-down inputs at reset and in BOOTSEL, so no relay fires during boot.

**I²C:** R1 and R2 pull up to +3V3. J3 is GND / +3V3 / SDA / SCL, which is the Qwiic/STEMMA QT order. Many SSD1306 OLED modules use GND / VCC / **SCL / SDA**, so check a module's pinout before plugging it in.

**1-Wire:**
- R4 is a 4.7 kΩ pull-up.
- U3 sits on the Xiao side of R27, and J8 is fed through R26 (+3V3) and R27 (DQ).
- Simulation-only parts (V1, VG1, R_TX1, R_LH1, R_L5, XDIAL1) are excluded from the board and BOM.

**PCB:**
- `RC_24VAC_UNFUSED` and `RH_24VAC` are 0.8 mm.
- The B.Cu GND pour covers the logic area.
- No courtyard overlaps, no clearance errors, nothing unrouted.

## Suggested order
1. Decide how the Xiao is mounted (A5) and confirm the terminal block opening direction (A1). Those two settle the layout changes.
2. Measure or estimate the Dial's power draw, then pick C3 (A3) and F1 (B6).
3. Re-place: rotate J5, move J8 to an edge, add mounting holes, and move U3 and the four resistors in front of the USB port (B1, B5).
4. Schematic edits: C3 value and footprint, the J8 clamp diodes (B2), the C2 rating, U3 decoupling, J4 value, title block, cleanup.
5. Update PCB, route, add the silkscreen labels (A4), then run DRC.
