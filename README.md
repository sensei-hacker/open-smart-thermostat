# Open Smart Thermostat (XIAO RP2040 + M5Stack Dial)

A 24 VAC HVAC thermostat board. A Seeed XIAO RP2040 handles temperature control and switches the HVAC wires through optically isolated triacs. An M5Stack Dial provides the user interface.

KiCad 10 project. All parts are through-hole for hand assembly.

## Hardware
- **Outputs:** 7 channels: G, Y1, Y2, O/B (switched from Rc) and W1, W2, E (switched from Rh).
  - Each channel is a MOC3063 zero-cross optotriac driving a BT138-600E triac with an RC snubber.
  - JP1 links Rh to Rc for single-transformer systems.
- **Power:**
  - Half-wave rectified from Rc/C (1N4007) with a P6KE47CA TVS and an MF-R050 PTC fuse.
  - A TIP122 + 30 V zener pre-clamp (about 29 V max) feeds a Mornsun K7805-500R3 5 V switching module.
  - The Dial is powered from 5 V through J9 and a USB-C pigtail.
- **Sensors:**
  - an on-board DS18B20 (U3)
  - J8 for a remote DS18B20 probe
  - J3 I2C port (GND / 3V3 / SDA / SCL) for a humidity module such as an AHT20 or SHT31

## Files
| Path | What |
|---|---|
| `thermostat.kicad_sch`, `thermostat.kicad_pcb`, `thermostat.kicad_pro`, `thermostat.kicad_dru` | KiCad 10 project |
| `fab/`, `thermostat-fab-*.zip` | Gerbers, Excellon drills and previews (JLCPCB-ready) |
| `BOM-LCSC.csv` | Purchasing BOM with LCSC part numbers, plus "buy elsewhere" items |
| `BOM.csv`, `CPL.csv` | JLCPCB-format BOM and placement files |
| `ASSEMBLY-AND-TEST.md` | Staged build and bench-test procedure, and firmware requirements |
| `DESIGN-REVIEW-*.md`, `STATUS-NEXT-STEPS.md` | Design reviews and change log |
| `sim/` | ngspice models, and a script that builds a SPICE netlist from the schematic's Sim fields (`cd sim && python3 schematic_to_spice.py && python3 plot_schematic_run.py`) |

The M5Stack Dial schematic is available from M5Stack's documentation site.

## Status
- The board is designed and DRC-clean, but **not yet built or tested**.
- Bench-test the MOC3063/triac channels with a real 24 VAC relay or contactor coil before installing (see `ASSEMBLY-AND-TEST.md`).

## Firmware requirement
Set the RP2040 GPIO drive strength to **12 mA** on the seven output pins (GP26, GP27, GP28, GP29, GP4, GP3, GP2), or the MOC3063 LEDs may not trigger reliably.

## Safety
- This connects to HVAC equipment.
- Turn off power at the furnace or air handler before wiring.
- Use at your own risk.
