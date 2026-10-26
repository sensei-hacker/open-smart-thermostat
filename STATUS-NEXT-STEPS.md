# Status and next steps (written before reboot)

Project: `design3-compact/` (KiCad 10, 24 VAC HVAC thermostat, XIAO RP2040). Full review is in `DESIGN-REVIEW-2026-10-18.md`.

## Rules to keep following
- Work only in `design3-compact/`, never design2-xiao2040.
- Back up to `thermostat-backups/` before every edit.
- Never edit while KiCad has the files open (check `~*.lck` and `pgrep -af kicad`).
- Ask the user before changing the schematic or PCB where they differ. The user runs Update PCB from Schematic themselves.
- Verify with KiCad 10's own tools, not my parser: `kicad-cli (KiCad 10) sch erc|export netlist`, `pcb drc`. The system KiCad 6 cannot open these files.
- When cutting s-expression blocks by index, use a paren-matching helper (a plain rfind of the previous block start deleted a neighbouring item once).

## Done so far
Schematic (`thermostat.kicad_sch`), all verified with kicad-cli (ERC: only library-mismatch/off-grid warnings plus one `same_local_global_label` at J7 pin 2 GND):
- Spare channel removed. 1WIRE goes to J7 pin 7 (D7/GP1).
- LED resistors 270 ohm.
- `+3V3`/`+5V` power symbols had power_out pins, so the rails were split. Fixed (power_in, global labels, PWR_FLAG on +3V3).
- Half-wave supply: BR1 removed, D1 1N4007 added, logic GND = C (`C_24VAC_RTN` is gone). Sim: VRECT_DC 26-33 V, +9V 8.94 V, +5V 5.00 V.
- D8 1N5817 Schottky between +5V and J7 pin 1 (Xiao 5V pin is USB VBUS).
- J3 is a generic I2C port: pin 1 GND, pin 2 +3V3, pin 3 SDA, pin 4 SCL. The Dial has its own power connector; its 5 V must not go to J3 pin 2.
- F1 value is now MF-R050 PTC 60V (same footprint).
- J5 is 4-pin (W1, W2, E, Rh) with the 4P Xinya footprint.
- J8 protection: R26 47 ohm in the +3V3 feed, R27 100 ohm in DQ, D9 BZX79-C5V1 zener from DQ to GND at the connector.

PCB (`thermostat.kicad_pcb`):
- User ran Update PCB and routed D8, D9, R26, R27, J3 and J5.
- I set `/RC_24VAC_UNFUSED` and `/RH_24VAC` tracks to 0.8 mm. Outputs stay at 0.4 mm (0.5 mm caused 35 clearance violations at the 0.2 mm rule; they only carry about 0.5 A).
- I added a B.Cu GND pour, x 78-139, y 76-118, priority 0, and refilled zones.
- DRC: 0 unconnected, 0 clearance violations. Left: a silkscreen-clipped-by-edge note, library-mismatch notes, and one `starved_thermal` at U3 pad 1 (harmless).
- Backups: `.before-widths-pour` (PCB), `.before-schottky`, `.before-j3-3v3`, `.before-j5-4pin`, `.before-j8-protect` (schematic).

Design notes worth remembering:
- Load current returns through the equipment's own wiring, not through this board. J1 pin 1 / GND carries only the logic supply (about 0.1 A).
- At most four relays are on at once. Estimated bus current is 0.8-1 A realistic and about 2 A worst case. Outputs are 0.5 A or less.

## Next steps
1. After the reboot, open the PCB, press B to refill zones, and look at the pour around the Xiao and U3. Add a keepout near U3 (DS18B20) if wanted.
2. Remaining review items, in the user's order of interest:
   - B4: DS18B20 thermal placement (reads high next to warm parts).
   - B8: terminal blocks. Check the Xinya XY308 rating for 18 AWG, or use 3.5/5.0 mm pitch.
   - B9: USB-C plug clearance (vertical resistors R5, R8, R17, R20 in front of the port).
   - A3/A4: silkscreen. Fix the J3 labels (GND/3V3/SDA/SCL, one pin off) and add labels at every field terminal (C, Rc, G, Y1, Y2, O/B, W1, W2, E, Rh, 3V3/DQ/GND, and the JP1 note).
   - B3: bench-test the MOC3063 zero-cross part with inductive loads. MOC3023 is the fallback.
   - Housekeeping (section E): mounting hole refs, stale `ERC.rpt`, `dbg*.cir`, the leftover `#PWR01`/`#FLG04` near (260.52, 97.8) in the schematic, the same_local_global_label warning at J7 pin 2.
3. Optional: add a schematic note about the Dial cable and J3 pin 2, and re-run the SPICE sim (`sim/schematic_to_spice.py`) now that J8/J5/D8 changed.
4. The memory file `memory/xiao-5v-connection-task.md` and the review file progress notes were updated. The final progress line in `memory/design-review-2026-10-18.md` for J3/F1/J5/J8 may be missing (that append was not approved), so add it.

## Update 2026-10-20 (after the re-review in DESIGN-REVIEW-2026-10-20.md)
Decisions:
- Debugging is done from a laptop on battery, with no earth connection. F1 moved into the C leg as insurance in case a path to earth exists.
- The Xiao will be soldered directly to the board. USB is not blocked.

Schematic, verified with kicad-cli (backup `.before-fuse-c-j5`):
- F1 now sits between J1 pin 1 (new net `C_24VAC`) and GND. D7 goes across J1, from Rc to C_24VAC. D1's anode is on `RC_24VAC_UNFUSED`, and `RC_24VAC_FUSED` is gone. The sim source and Y1 load return to C_24VAC. The sim still gives 26-33 V / 8.94 V / 5.00 V.
- J5 pins are reversed: 1 = Rh, 2 = E, 3 = W2, 4 = W1. Each net stays in the same physical hole once J5 is rotated 180 degrees.
- D8's footprint is now `D_DO-41_SOD81_P7.62mm_Horizontal`.

PCB, placement only (backup `.before-fuse-c-j5`):
- J5 rotated to (110.12, 54, 180). The J5 reference text is beside the block.
- J8 moved to (81.5, 55.5, 270) on the top-left edge, opening left. D9 is at (79.5, 65). R27 is at (85.08, 68.5, 180). R26 is at (85.08, 72, 180).
- U3 moved to (128.3, 72.5), top-right and outside the GND pour.
- D8's pad 1 (cathode) is at (93.92, 89, 180). After the footprint swap the anode lands at (86.3, 89). The +5V run past D8 was re-netted to Net-(D8-K) and extended to J7 pin 1. The old trace under the Xiao was removed.
- Tracks that only served the moved parts were removed.

Next:
1. The user runs Update PCB from Schematic (with "update footprints" on), then presses B.
   - Expected: the J5 shorts clear. D8's anode lands at (86.3, 89).
   - New shorts appear around J1/F1/D1/D7 because of the C_24VAC change.
2. Route:
   - J1.1 to F1.1 and D7.2. F1.2 to GND. D1's anode to the Rc bus. Remove the old tracks between J1 and GND.
   - The J8 group: J8.1 to R26.2; J8.2 to D9.K and R27.2; J8.3 and D9.A to GND. R26.1 to +3V3 and R27.1 to 1WIRE at R4. R4.1 also needs its +3V3 feed again.
   - U3: GND by a thin track, DQ to J7.7, VDD to +3V3.
3. Before ordering, confirm on a real XY308 which side the wires enter. KiCad has no 3D model for it.
4. Still open: mounting holes, C3 220 uF (measure the Dial's draw), terminal pin labels, J4 value text, the D9 clamp (BAT85 steering), firmware drive strength, and housekeeping.

## Update 2026-10-23 (after DESIGN-REVIEW-2026-10-23.md)
- The user moved U3 to (134, 83.5) and cleared the area in front of the USB port. J9 stays unkeyed (accepted). D9 stays a zener.
- Schematic (backup `.before-tvs47-c15`):
  - D7 value is now P6KE47CA. The model is in sim/thermostat_models.lib.
  - Added C15, 100 nF, C_Disc_D3.0mm_W1.6mm_P2.50mm, from +3V3 to GND at U3. The netlist diff shows only these changes, and ERC has no errors.
- Next, for the user:
  - Run Update PCB.
  - Place C15 beside U3 and route it.
  - Still open: terminal and board silkscreen labels, and mounting-hole refs.
- 2026-10-23, afternoon:
  - Update PCB had deleted the PCB-only mounting holes. I added H1–H4 to the schematic: Mechanical:MountingHole_Pad, footprint MountingHole_3.2mm_M3_DIN965_Pad, value M3, pins no-connect. Backup `.before-mounting-holes`. ERC is clean, and the netlist only gained H1–H4.
  - Still open: D8 pin 2 (+5V, at 85, 79.38) is unrouted to the 7805/C14 +5V track.
- 2026-10-23, evening:
  - PCB title-block date set to 2026-10-23 (backup `.before-date`). Final DRC: 0 unconnected, 0 parity issues.
  - Generated fab/ (Gerbers, PTH/NPTH Excellon in mm, drill maps) and thermostat-fab-2026-10-23.zip.
  - Checked the Gerbers with my own parser:
    - 198 holes, matching the PCB's 198 through-hole pads.
    - Every hole has copper on both sides and a mask opening.
    - No copper or silk within 0.3 mm of the edge.
    - No silk on pads.
    - Previews: fab/gerber_front.png, fab/gerber_back.png.
- 2026-10-23, late (backups `.before-r220`):
  - Resistor consolidation, in the schematic and PCB values:
    - 7 LED (270) and 7 gate (180) resistors → 220 Ω.
    - R26 47 → 100 Ω.
  - Checks:
    - Netlist diff shows values only. ERC 0 errors. DRC 0 unconnected, 0 parity issues.
    - The regenerated Gerbers and drills are identical, so the zip is unchanged.
    - Sim: Y1 load 22.7 Vrms when on, 0.2 when off.
  - BOM.csv and BOM-LCSC.csv updated: C2 and C15 share one 100 nF 100 V line (no LCSC number yet); 220 Ω is C57439.

## Update 2026-10-23, night: option B power supply (backups `.before-clamp5v`)
- Why: the R-78HB9.0-0.5 cost ~$18. The cheap modules are rated 36 V max, but VRECT can reach ~38-41 V with a lightly loaded transformer at high line, plus coil-switching spikes up to D7's ~65 V clamp.
- Schematic:
  - Added a clamp: Q8 TIP122 (collector on VRECT_DC, emitter on the new net VCLAMP), R28 2.2k from VRECT_DC to the base, and D10 BZX79-C30 from the base to GND. VCLAMP = min(VRECT - ~2.4 V, ~29 V).
  - U1 is now a K7805-500R3 (6.5-36 V in, LCSC C86735). It keeps the R-78HB footprint, runs from VCLAMP to +5V, and C13 (now 10uF/50V) is its input cap.
  - U12 (7805) and the +9V rail are removed.
  - J9 is now "Dial 5V" on +5V: the Dial runs on USB 5 V through a USB-C pigtail.
  - Added #FLG05 on VCLAMP and two text notes.
  - Checks: ERC 0 errors. The netlist diff shows only the intended changes.
- Sim (sim/ models added: K7805, TIP122, BZX79C30; DIAL_LOAD is now 1 W on 5 V; the sim scripts probe VCLAMP instead of +9V):
  - VRECT 24.7-33.2 V, VCLAMP 22.9-28.6 V, +5V 4.94 V.
  - Q8 drops ~2.4 V and dissipates ~0.15 W at an 80 mA logic load.
- BOM.csv and BOM-LCSC.csv updated. D10 and R28 still need LCSC numbers.
- Next, for the user:
  - Run Update PCB. U12 is deleted, and Q8, R28 and D10 arrive unplaced.
  - Place them, ideally Q8 where U12 was, keeping Q8 away from U3.
  - Route VRECT -> Q8.C/R28, Q8.E -> U1.1/C13, and U1.3 -> +5V.
  - Rename the J9 silkscreen from "Gnd 9V" to "Gnd 5V".
- After routing: rerun DRC and regenerate the Gerbers, drill files, CPL and zip. The 2026-10-23 zip is now obsolete.
- 2026-10-24: added the "Pour to pads" rule (0.5 mm zone-to-pad clearance) to thermostat.kicad_dru (backup `.before-pour-pads`) to reduce hand-solder bridges to the GND pour. A refilled copy passes DRC: 0 errors, 0 unconnected, one harmless starved_thermal at J7 pad 2 (isolated pour island). The user must press B and save so the saved pour matches the rule.
- 2026-10-24, later: the user refilled and saved. Final DRC: 0 errors, 0 unconnected, 0 parity (only lib_footprint_mismatch and the J7 pad 2 starved_thermal). Regenerated fab/ (Gerbers, drills, previews), CPL.csv (72 parts, pad-midpoint centres, TX1 excluded) and thermostat-fab-2026-10-24.zip. The old fab/, CPL.csv and 2026-10-23 zip are in thermostat-backups/fab-2026-10-23/. Gerber check: 204 holes = 202 THT pads + 2 tented vias, all with copper on both sides; no copper/silk within 0.3 mm of the edge; no silk on pads. Still open in the BOM: LCSC numbers for D10, R28, C2/C15, XY308-4P, jumper cap.

## End-of-project reminders (user asked to be reminded)
- [ ] Firmware: set RP2040 GPIO drive strength to 12 mA on the MOC3063 LED pins (`gpio_set_drive_strength(pin, GPIO_DRIVE_STRENGTH_12MA)`).
- 2026-10-24: BOM-LCSC.csv filled (backup `.before-lcsc-fill`): R28 C58595, J4/J5 XY308-2.54-4P C915913, D10 BZX55C30 C5190031 (BZX79-C30 equivalent), C15 C168753 (50V 2.54mm), C2 C454377 (100V, 5.08mm leads to be formed to 2.5mm), jumper cap C2689176. Stock checked through JLCPCB's parts search on 2026-10-24.
- Reviewed smeisner/smart-thermostat and lolokraus/Open-Source-Smart-Thermostat: no board changes needed; ideas are humidity sensor on J3/Dial Grove, firmware fallback/safety (see chat).
- 2026-10-24: D10 value changed to BZX55C30 in the schematic (backup `.before-bzx55`); ERC 0 errors, netlist diff = value only. The PCB still says BZX79-C30 on F.Fab only (not in the Gerbers); run Update PCB to sync it, and no fab regeneration is needed. BOM.csv D10 = BZX55C30 C5190031. BOM-LCSC.csv gained "buy elsewhere" lines (XIAO, Dial, USB-C pigtail, DS18B20 probe, AHT20/SHT31). Wrote ASSEMBLY-AND-TEST.md (staged build, channel G first, jumper LED test before the XIAO, GPIO 12 mA code).

### 2026-10-25: C2 5 mm, U3 power fix, JLC BOM, fab regenerated
- C2 footprint is now C_Disc_D5.0mm_W2.5mm_P5.00mm (user), so the C454377 part (5.08 mm leads) fits without bending.
- Schematic: U3 had snapped to (68.58, 171.45), leaving the +3V3 and GND symbols 0.58 mm off its wires, so U3/C15 had no power. Moved both symbols onto the wire ends (backup `thermostat.kicad_sch.before-u3-power-fix`). User ran Update PCB.
- DRC with parity on the saved board: 0 unconnected, 0 parity issues. Remaining items are library-footprint-mismatch warnings plus the existing J7.2 starved-thermal warning (pad also has a track).
- BOM-LCSC.csv reformatted for JLC (Comment/Designator/Footprint/... /Notes). Headers split into 2P/4P/7P parts. D8 changed to C698892 and D9 to C895329 (old codes had 0 stock). U1 C86735 is not in JLC's assembly library; the EVISUN C19188491 is the JLC alternative.
- Fab regenerated: `fab/`, `thermostat-fab-2026-10-25.zip` (14 files), CPL.csv (only C2 moved). Old set in `thermostat-backups/fab-2026-10-24/`.

### 2026-10-26: header holes 1.1 mm (next revision)
- The ordered boards (JLC, fab zip 2026-10-25) have 1.0 mm header holes, about 0.1 mm of slack over the 0.905 mm diagonal of a 0.64 mm square pin. Test-fit a pin before soldering; don't force it.
- The PCB now has 1.1 mm drills on J3, J6, J7, J9 and JP1 (22 pads, pads stay 1.7 mm). Backup `thermostat.kicad_pcb.before-hdr-1p1`. The fab zip and CPL were not regenerated, so they still match the ordered boards.
- Rule of thumb: square pins need hole = diagonal + about 0.15-0.25 mm; round leads, lead diameter + the same.
- The change is on the board's footprint copies only; "Update footprints from library" would put 1.0 mm back.
- DRC with parity on a scratch copy: 0 unconnected, 0 parity issues, no new errors (3 more library-mismatch warnings from the changed drills).
