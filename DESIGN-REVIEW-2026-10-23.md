# Pre-fabrication review, 2026-10-23

I checked the files as saved: `thermostat.kicad_pcb` at 2026-10-22 23:49 and `thermostat.kicad_sch` at 2026-10-20 21:10. All checks used the KiCad 10 kicad-cli. I changed no design files.

## Automated checks
- **ERC:** 0 errors. All 337 items are warnings:
  - 236 off-grid endpoints.
  - 100 library-symbol notes.
  - 1 `same_local_global_label` at J7 pin 2. It is harmless: the PCB shows J7 pin 2 on GND.
- **DRC (zones refilled):**
  - 0 unconnected items.
  - 0 clearance, short or courtyard errors.
  - 50 library-footprint-mismatch notes.
  - 2 silkscreen-clipped-by-edge warnings.
- **Schematic parity:** everything matches except the 4 mounting holes. They exist only on the PCB, and three of them share the reference `M3-2`.
- **Zone fill:** the saved fill matches a fresh refill, so the Gerbers will be current.
- **Manufacturability:**
  - Board 63 × 98 mm, 2 layers, no vias.
  - Thinnest track 0.4 mm. Clearance rule 0.2 mm.
  - Smallest drill 0.71 mm.
  - Smallest annular ring 0.15 mm, on U3 (stock TO-92 footprint). That is fine at JLCPCB and PCBWay (0.13 mm minimum).
- **Track widths:**
  - Rc, Rh and C_24VAC: 0.8 mm.
  - Outputs: 0.4 mm.
  - GND: mostly the B.Cu pour.
  - F1 pin 2 joins the pour with thermal spokes.
  - F1 pin 1 (C) is isolated from the pour.
- **Terminal orientation:** J1 and J4 open toward the bottom edge, J5 toward the top edge, and J8 toward the left. This still assumes the XY308 wire entry is on the footprint's +y side, which needs a physical check.

## Decide before ordering (these need board changes)

1. **The Xiao's USB-C port is blocked.**
   - The Xiao's pin 1 end (5V and D0) is at x = 108.45, so the USB-C receptacle faces left at about (105, 97.2).
   - These parts sit in the path of a plug, in the band y = 91–103.5:
     - R17 and R20, vertical resistors.
     - U3 (TO-92).
     - R5 and R8, vertical resistors.
     - R2.
     - C13, an electrolytic capacitor.
     - J9, then U12.
   - If the Xiao is soldered down, you can't reflash it without desoldering. The Xiao's SWD pads are on its underside, so they are covered too.
   - Options:
     - (a) Mount the Xiao in female sockets and pull it to reflash.
     - (b) Clear a corridor about 13 mm wide in front of the port.
     - (c) Rotate the Xiao 180° so USB faces right. That needs a full re-route, and J3, R23, R11 and R14 are in that path.
2. **U3 is back beside the regulators.**
   - Position: (94.5, 93.5).
   - Distances: about 9.5 mm from the 7805's leads, 4.5 mm from D8, and 4 mm from C13.
   - Its GND pad is tied into the B.Cu GND pour that also carries U1, U12 and C3.
   - Expect it to read a few °C high. If U3 is only a backup to J8 or the Dial, that may be acceptable. Otherwise, move it, or at least add a pour keepout and connect GND with a thin track.
3. **Footprint-level open items.** Decide now or accept as-is:
   - J9 unkeyed (B9).
   - D9 zener vs BAT85 steering diodes (B2).
   - No 100 nF decoupling at U3 (B11).
   - C3 size if the Dial needs 220 µF (A3). A 10 mm capacitor doesn't fit at (80.5, 119.5) without moving it.

## Strongly recommended silkscreen (cheap, avoids wiring mistakes)
4. **No terminal labels:**
   - J1: C, Rc.
   - J4: G, Y1, Y2, O/B.
   - J5 (pin 1 is at the right in top view): Rh, E, W2, W1.
   - J8: 3V3, DQ, GND.
   - JP1: "Rh–Rc: fit for single transformer".
   - J9: +9V / GND polarity.
   - A swapped Rc and C at J1 still powers the board, but puts logic GND on Rc.
5. **No board name, revision or date on the silkscreen.** The title block still says "Raspberry Pi Pico 2 W", 2024, rev 1.0.
6. **Mounting holes:**
   - Rename them M1–M4, or H1–H4. The current duplicate `M3-2` triggers parity warnings.
   - The bottom-right hole's reference text sits off the board.
   - The bottom-left hole's plated ring is about 1 mm from D1's Rc pad. Use a plain M3 head with no large washer, or a nylon screw.
7. **J3 is labelled "G" for GND.** Hobbyists could read that as the HVAC G (fan) terminal. Suggest "GND".
8. **15 references are hidden:** R5, R7, R8, R9, R11–R16, R23, J3, Q1, C8. That makes hand assembly harder.

## Value-only changes (can be made in the BOM after ordering)
9. **D7 P6KE43CA → P6KE47CA.**
   - The 43CA has a 36.8 V working voltage and 40.9 V minimum breakdown.
   - A lightly loaded 24 VAC transformer can sit at 27–29 VAC, which is 38–41 V peak. That puts the 43CA right at breakdown.
   - D7 is now ahead of F1, so if it fails short nothing on the board fuses it.
   - The 47CA has a 40.2 V working voltage and 44.7 V minimum breakdown. It uses the same footprint.
10. **C2 rating:** use ≥100 V.
11. **C3:** 100 µF is adequate if the Dial draws 1.5 W or less (see the sim table in the 2026-10-20 review).
12. **Firmware:** set 12 mA drive on the MOC3063 GPIOs.

## Checked OK
- Netlist and PCB match: the C_24VAC → F1 → GND fuse, D7 across J1, J5 reversed pin order, D8 Schottky to Xiao 5V, and the J8 protection parts.
- Xiao pin mapping matches the XIAO RP2040 pinout:
  - J6: D0–D6, with SDA = D4, SCL = D5 and TX = D6.
  - J7: 5V, GND, 3V3, D10–D7, with 1-Wire on D7.
- No parts under the Xiao.
- No vias.
- Teardrops are not needed.
- The 7805 dissipates about 0.2 W. Triacs at 0.5 A run without heatsinks.
