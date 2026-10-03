# Alerter on an Arduino Uno: build guide

The alerter is the loop's brain for one tank:
- each day it gets the forecast `p` and the tank's chlorophyll;
- it decides ON/OFF with the same rules as `src/sim/loop_controller.py`;
- it switches a relay (the treatment) and shows the state on LEDs and a buzzer.

The Uno has no Wi-Fi, so the laptop sends the daily values over USB. An ESP32 is only needed
later, if the box must run without a laptop.

**What gets measured, and how:**

| Measurement | Why | How | Auto / by hand | Stage |
|---|---|---|---|---|
| Chlorophyll | model input (required), OFF rule | DIY fluorometer | auto | 5 |
| Temperature | model input, safety | DS18B20 probe | auto | 3 |
| pH | safety (bubbling and percarbonate shift it) | analog pH probe | auto | 4 |
| Dissolved oxygen | model input (optional), safety < 4 mg/L | aquarium DO kit | by hand, daily | 6 |
| Salinity | model input (optional) | refractometer | by hand, every 2-3 days | 6 |
| Cell counts | the real endpoint; checks the fluorometer | microscope + Sedgewick-Rafter slide | by hand, every 1-2 days | 6 |
| Ammonia / nitrate / phosphate / H₂O₂ | method safety limits | test strips/kits | by hand, at each re-measure | 6 |
| Non-target survival | arm D harm check | *Artemia* 24-h survival | by hand | 6 |

**Build one stage at a time. Don't start the next stage until the current one passes its "done when" check.**
Dates fit `EXECUTION_PLAN.md`: build and calibrate by Oct 24, cultures Oct 15-31, warm-up Nov 10.

| Stage | What | Target | New cost |
|---|---|---|---|
| 0 | Parts check | Sep 27 | $0 |
| 1 | Logic + lights | Sep 27-28 | $0 (kit) |
| 2 | Relay + pump | by Oct 4 | ~$25 |
| 3 | Temperature | by Oct 4 | ~$8 |
| 4 | pH probe | Oct 5-11 | ~$30 |
| 5 | Fluorometer (chlorophyll) | Oct 5-18 | ~$20 |
| 6 | Hand-measurement kit | Oct 12-24 | ~$90 + borrowed microscope |
| 7 | Laptop link + logging | Oct 19-24 | $0 |
| 8 | Dry run on a real tank | Oct 26 - Nov 9 | $0 |
| 9 | Dosing module (inline dilution, peroxide) | Oct 12-24 | ~$70 |

**Progress:** stages 1 and 2 passed on 2026-09-26: Test A, lights, buzzer, and the bare relay
clicking on D10 (LED as the pretend pump; the real pump isn't bought yet).
On 2026-09-30 the new Uno (COM5) passed Tests A, B and C by hand, every line matching, and the bare
relay clicked on D10 with `hardware/relay_click_test/relay_click_test.ino` (toggles D10 every second).

## Shopping list (what to order now)

Already on hand: Uno, breadboard, M-M wires, blue/green/white LEDs, 220/330/10k Ω resistors,
PN2222A transistors, passive buzzer, bare 5 V relay, 1N4007 diode.

| # | Item | For | Approx. |
|---|---|---|---|
| 1 | Male-to-female jumper wires ([ELEGOO 120-pc M-F/M-M/F-F](https://www.amazon.com/dp/B01EV70C78)) | relay pins, sensor boards | $6 |
| 2 | 12 V diaphragm air pump ([search: 12 V diaphragm air pump](https://www.amazon.com/s?k=12v+dc+diaphragm+air+pump+aquarium); the listing found first is gone) + 12 V 2 A adapter with barrel-jack screw terminals ([bundle](https://www.amazon.com/dp/B08GX5Z4MR)) + air tubing and an air stone | stage 2 (the real pump) | $20 |
| 3 | DS18B20 **waterproof** probe ([5-pack with 4.7 kΩ resistors](https://www.amazon.com/dp/B0C8J77NJR)) | stage 3 | $10 |
| 4 | pH module + BNC probe ([PH-4502C type](https://www.amazon.com/dp/B07KDPQGYD)) + buffer powders 4.00/6.86/9.18 ([VIVOSUN 18-pack](https://www.amazon.com/dp/B0D4L8Y7BT)) | stage 4 | $35 |
| 5 | [Adafruit TSL2591](https://www.amazon.com/dp/B00XW2OFWW) + [LEE 106 Primary Red gel](https://www.amazon.com/dp/B003DIGLV8) + cuvettes with **4 clear sides** ([Globe 4.5 mL, 100](https://www.amazon.com/dp/B08N5B5PL8)) + [470 nm blue LEDs](https://www.amazon.com/dp/B091SLR9SB) | stage 5 | $40 |
| | **Total** | | **~$110** |

Links found 2026-09-26; check the price, the rating and that it still matches before buying. The
cuvettes must have 4 clear sides, because the sensor looks in at 90° to the LED. Calibrate the pH probe
with the 6.86 and 9.18 buffers (they bracket seawater's ~8).

Stage 6 (hand kits: DO kit, refractometer, counting slide, test strips, ~$90) can wait until mid-October;
it's listed in stage 6 below and in `notes/mitigation/MATERIALS_LIST.md`.

---

## Stage 0: parts check

Go through the kit against the stage 1 list. Write down what's missing, and order stages 2-5 parts together (one shipping wait).

**Done when:** you have everything for stage 1 on the desk, and the stage 2-5 order is placed.

## Stage 1: logic + lights (kit parts only, ~1 hour)

**Parts** (on hand): Uno, breadboard, green, blue and white LEDs, 220/330 Ω resistors, passive buzzer, NPN transistor + 330 Ω–1 kΩ, M-M jumper wires.

**Visual wiring: [circuito.io design](https://www.circuito.io/app?components=512,9591,9594,11021,11050,11372,956215)**
(snapshot `wiring_circuito.jpg`). Build it exactly as shown, with two colour swaps:
- circuito's **yellow** LED = your **white** LED (warning);
- no relay in the picture: D10 stays empty until the relay goes there in stage 2; the blue LED already shows when the relay would be ON.

The sketch uses circuito's pins:

| Uno pin | Goes to |
|---|---|
| D6 | green LED → 330 Ω → GND: **idle** |
| D5 | blue LED → 100 Ω (220 Ω also fine) → GND: **treatment ON** |
| D9 | white LED (circuito's yellow) → 220 Ω → GND: **warning** |
| D10 | empty in stage 1; stage 2: the relay transistor |
| D2 | 330 Ω → NPN transistor base; buzzer between 5V and the collector; emitter → GND |
| D3 | DS18B20 yellow wire, 4.7 kΩ to 5V (stage 3) |
| 5V / GND | breadboard rails |

`schematic.png` (drawn by `draw_schematic.py`) is the same circuit as a circuit diagram, plus the
bare-relay driver that circuito can't draw.

The sketch drives a **passive** buzzer (it plays a 2 kHz tone). Change `BUZZ_HZ` for a different pitch.

⚠ **Full-size breadboards split their power rails in the middle** (look for a gap in the red/blue
lines). Jumper the top + to the bottom + and the top − to the bottom −, or parts in the bottom half
get no power. This silenced the buzzer on 2026-09-27: it was in the bottom half, powered from a dead rail.
A buzzer wired straight from D2 to GND also works, just more quietly.

**Flash it:**
1. Open `alerter_uno.ino` in the Arduino IDE.
2. Select Board → Arduino Uno and the COM port, then click Upload.
3. Open the Serial Monitor at **115200** baud with **"Newline"**.

**Test A**: paste one line at a time (X = 3, C_ok = 5):

```
1 0.2 3      -> idle            (green)
2 0.6 4      -> START           (3 beeps, blue, next_check=5)
3 0.7 6      -> ON
4 0.7 8      -> ON
5 0.5 9      -> ON next_check=8 (p not below T_off 0.40: keep going)
8 0.3 4      -> OFF             (1 long beep, green)
9 0.3 3      -> idle
```

**Test B (MAX_ON = 12 days)**: send `reset`, then `1 0.6 4`, then days 2-14 as `<day> 0.9 20`.
- Day 13 prints `STOP_MAX_ON`.
- Day 14 restarts (episodes=2), because `p` is still high.

The Python controller gives the same states on both tests (checked 2026-09-26).

**Test C (handover + floor, added 2026-09-28)**: send `reset`, `x 3`, `cok 3`, `mode H`, `warm 2`,
`floor 0.8`, then one line at a time:

```
1 0.1 2.0    -> idle
2 0.1 2.2    -> idle
3 0.1 4.6    -> idle            (rule fires: rose 2 days and > 2 x warm; forecast still low)
4 0.2 5.1    -> idle
5 0.2 6.0    -> START           (handover: rule fired 2 days ago, forecast never did)
6 0.3 6.5    -> ON
8 0.3 7.0    -> ON              (day 7 skipped: fine)
9 0.3 1.5    -> ON              (1st reading below the floor 0.8 x 2 = 1.6)
10 0.3 1.4   -> OFF_FLOOR       (2nd in a row: H4 floor OFF)
11 0.3 1.3   -> idle
12 0.6 5.0   -> START           (forecast)
```

`alerter_link.py --replay <file> --sim --mode H --warm 2 --floor 0.8 --x 3 --cok 3` prints the same
states (Python reference, 2026-09-28). Run it on the board too: 0 mismatches is the pass mark.

**Other commands:**
- `status`
- `x 2`, `cok 4.5`
- `mode F` (forecast only), `mode R` + `warm 1.8` (rule trigger: chl rose on 2 calendar days AND
  > 2 × warm-up mean), `mode H` + `warm 1.8` (forecast, with the 2-day handover to the rule: arm B)
- `floor 0.8` (H4: 2 readings in a row below 0.8 × warm while ON → `OFF_FLOOR`; `floor 0` for the
  false-alarm arm D), `maxon 3` (MAX_ON in **days since START**; 0 = 4 × X; peroxide 3 with `x 1`)
- `pulse <s>` (added 2026-10-02, peroxide dosing pump): while ON, the relay runs for `<s>` seconds at
  START and at each check day that continues the episode, then switches off; the state still prints
  `ON`, and the day line ends with `pulse=<s>s`. `pulse 0` (default) holds the relay for the whole
  episode (air pump), so Tests A-C are unchanged.
- `skip`: the next pulse is skipped (the day line shows `pulse=skipped`); send it when the low-range
  kit reads an H₂O₂ residual above 0.5 mg/L.
- **Peroxide setup:** `x 1`, `maxon 3`, `pulse <s>`, where `<s>` = seconds the calibrated pump needs to
  deliver the pulse volume (0.265 mL of 3% per 10 L for 0.8 mg/L; from the weigh-calibration in
  mL/s). Because MAX_ON counts days since START, this gives at most 3 pulses (START day and the next
  two check days) and `STOP_MAX_ON` on day 4. The 2.8 mg/L residual stop and the pH > 9.0 stop are
  **not** automatic in the firmware: send `stop` by hand, or use `alerter_link.py --stop "..."` /
  `--ph-max 9.0`.
- `temp 10 17` (temperature warning window; default 10-17 °C for the planned 12-15 °C run)
- `stop` for a safety stop, e.g. when the DO kit reads < 4 mg/L. With the laptop link, use
  `--today ... --stop "DO 3.6 mg/L"` instead, so the stop is logged and replayed after a reset.

**Done when:** Tests A, B and C print exactly the lines above, and the LEDs and buzzer match.

## Stage 2: relay + pump (~$25)

**Parts:**
- 1- or 2-channel 5 V opto-isolated relay module;
- a 12 V aquarium air pump (or peristaltic pump) + 12 V adapter;
- a DC barrel jack or screw-terminal adapter.

**Wiring:**
- Relay VCC→5V, GND→GND, IN→D10.
- The pump's 12 V + wire goes through the relay's **COM → NO** contacts; the − wire goes straight back to the adapter.
- The Uno and the 12 V pump do **not** share power.
- Most relay modules are **active-low**: with a module, set `RELAY_ACTIVE_LOW = true`. If the relay clicks ON while the sketch says idle, flip it.

**Bare 5-pin relay instead of a module** (the kit's blue SRD-05VDC-SL-C). Breadboard picture:
`relay_breadboard.png` (drawn by `draw_relay_breadboard.py`, since circuito.io can't draw this part).
- The coil needs ~70-90 mA, more than an Uno pin can give, so drive it with the NPN transistor:
  - D10 → 330 Ω (or 1 kΩ) → transistor **base**;
  - **emitter** → GND;
  - **collector** → one coil pin; the other coil pin → 5V.
- Put a **1N4007 diode across the coil**, with the striped end (cathode) on the 5V side. It absorbs the voltage spike when the coil turns off; without it the transistor or Uno can die.
- Pins: the top of the relay shows the pinout. With the relay off, **COM** is connected to **NC** (a multimeter beeps). The pump goes on **COM → NO**.
- `RELAY_ACTIVE_LOW = false` (the sketch default): a HIGH on D10 turns the transistor, and so the relay, on.
- The legs sit across the breadboard's centre gap. If they don't fit, solder short wires on.

⚠ **Never put 120 V mains on the breadboard or a bare relay.** A mains-powered pump goes on a
**smart plug** or an enclosed relay box ("IoT Power Relay") on a **GFCI** outlet, with the
sponsor's OK.

**Done when:** rerunning Test A makes the pump run from day 2 to day 8, and stop otherwise.

## Stage 3: temperature (~$8)

**Parts:** DS18B20 **waterproof** probe, 4.7 kΩ resistor (or two 10 kΩ in parallel).

**Wiring:**
- red→5V, black→GND, yellow→D3;
- the resistor goes between D3 and 5V.

**Code:**
- Arduino IDE → Library Manager → install `OneWire` and `DallasTemperature`.
- Set `USE_DS18B20 1` at the top of `alerter_uno.ino` (the code is already written and compile-checked).
- It reads every 10 s and alarms outside the window (default 10-17 °C, set with `temp <lo> <hi>`;
  white LED, fast beeps). `read` prints all sensors; `status` shows the temperature.

**Done when:**
- the probe agrees with a kitchen thermometer within 0.5 °C in a glass of water;
- ice water triggers the alarm, and room-temperature water clears it.

## Stage 4: pH probe (~$30)

**Parts:**
- analog pH probe kit with a BNC probe and the blue PH-4502C board (or DFRobot Gravity pH);
- pH 4.00, 6.86 and 9.18 buffer powder packets (calibrate with 6.86 and 9.18);
- distilled water for rinsing.

**Wiring:** board V+→5V, G→GND, Po→**A2** (A4/A5 are the TSL2591's SDA/SCL). Needs a working analog
header: the old Uno's broke off, so use the new board or a re-soldered header.

**Code** (written, compile-checked): set `USE_PH 1`. Then:
1. Probe in **pH 6.86** buffer, wait 1 min, type `cal686`.
2. Rinse, probe in **pH 9.18** buffer, wait 1 min, type `cal918`.
3. `read` now shows `ph=` (and the raw `ph_v=` volts). Calibration is stored in the Uno's EEPROM and
   survives unplugging; `cal` shows it, `calclear` erases it.
- `alerter_link.py --today` sends a **safety stop** if pH is outside 7.6-8.6 (change with
  `--ph-min/--ph-max`; peroxide runs use `--ph-max 9.0`). A safety stop ends a running treatment; it
  doesn't block a new start that day (same as the Python controller's `force_off`).

**Tips:**
- Store the probe tip wet (its cap with storage solution), never dry.
- The probe can read noisily when the air pump shares the water. Compare readings with the pump on and off.

**Done when:**
- the 6.86 and 9.18 buffers read within ±0.1 after calibration;
- seawater reads ~7.9-8.3 and agrees with a test strip.

## Stage 5: the fluorometer, chlorophyll (~$20, the hard part)

A blue LED makes chlorophyll glow red. A light sensor behind a red filter measures that glow.

**Autonomous accuracy (added 2026-10-02; the device must keep itself honest between service visits).**
Only the first item is built. The reference target, wiper, drift alarm and automatic rescaling are
**planned, not yet built**; the target and wiper need the servo (D11, `USE_SERVO`), which is
otherwise unused since 2026-10-01.
- **Dark reading every measurement:** LED off, LED on, subtract. Already in the code.
- **Reference target (planned):** once a day the servo swings a small piece of fluorescent plastic (or a sealed
  dye vial) in front of the sensor. Its reading should never change, so the device rescales `chlk`
  automatically when the LED or sensor drifts.
- **Wiper (planned):** the servo sweeps a soft rubber blade across the window before each reading, as RIDEM's
  sondes do.
- **Drift alarm (planned):** the device tracks its clear-water floor (lowest readings). If the floor rises for 3 or
  more days, it flags "needs cleaning".
- **Initial calibration** (blank + multiplier) is done once at setup against a reference: lab chlorophyll,
  cell counts, or a sonde. Service visits re-check it with 1-2 reference samples.

**Parts:**
- TSL2591 light-sensor breakout (Adafruit, works on 5 V);
- 470 nm blue LEDs + 220 Ω;
- red gel filter sheet (Roscolux/Lee "primary red", or a red theatre gel sample pack);
- square plastic cuvettes (4.5 mL);
- a small black box (3D print, or black foam board and tape).

**Layout:** the LED shines into the cuvette from one side. The sensor, behind the red filter, looks
in from 90° so it sees the glow, not the LED. Keep everything light-tight.

**Wiring:** TSL2591 VIN→5V, GND→GND, SDA→**SDA**, SCL→**SCL** (the two pins beside AREF, above D13;
same signals as A4/A5); blue LED on **D7** → 220 Ω → GND. STEMMA QT cable: red 5V, black GND,
blue SDA, yellow SCL.

**Code** (written, compile-checked): Library Manager → install **Adafruit TSL2591 Library** and
**Adafruit Unified Sensor**; set `USE_TSL2591 1`.
- `read` turns the blue LED off and on, takes 3 readings each (200 ms), and prints the difference as
  `fl=`, so room light cancels out. Too bright ("SATURATED") → `gain l`; too faint → `gain h` or `gain x`.
  The gain is saved with the calibration (EEPROM); changing it tells you to redo `blank` and `chlk`,
  because both are only valid at the gain they were measured at.
- **Zero:** cuvette of plain seawater in the box → `blank`.
- **Scale:** `chlk` is **µg/L of chlorophyll per signal count**. After the dilution series (below), fit
  reference chlorophyll in µg/L (acetone extraction, or a borrowed calibrated fluorometer) against
  `fl`, and type `chlk <slope>`. C_ok and the floor are then in µg/L. (If no µg/L reference exists,
  fit cells/mL instead and give C_ok and `warm` in cells/mL too; never mix the two units.)
  Then `read` prints `chl=` in µg/L, and `alerter_link.py --today --p 0.6` uses it automatically
  (leave out `--chl`).

**Calibration** (once cultures arrive):
1. Make a dilution series of the culture (100%, 50%, 25%, 12.5%, 6%, 0% in seawater).
2. Read each one 3 times.
3. Cell-count each one.
4. Fit reading vs cells (and µg/L if extracted chlorophyll is possible).

**Done when:**
- the blank (seawater only) reading is stable within ±5% over 10 minutes;
- the dilution series is a straight line (R² > 0.95).

## Stage 6: hand-measurement kit (~$90 + borrowed microscope)

| Item | Approx. |
|---|---|
| Aquarium DO test kit (saltwater) | $15 |
| Salinity refractometer (ATC) | $20 |
| Sedgewick-Rafter counting slide + transfer pipettes | $25 |
| Ammonia kit, nitrate/phosphate strips, H₂O₂ strips | $30 |
| Microscope (borrow from school) | $0 |

**Practice** on a culture flask for 3 days before any experiment. Do each measurement the way
you will in the real run, and fill in `src/lab/lab_data_template.csv`.

**Done when:**
- 3 days of practice data in the template;
- two counts of the same sample agree within 20%.

## Stage 7: laptop link + logging

**Script: `alerter_link.py`** (written 2026-09-27; needs `pip install pyserial`; close the Arduino IDE
Serial Monitor first, since only one program can use the port).

```
python hardware/alerter_uno/alerter_link.py --ports                  # find the Uno's COM port
python hardware/alerter_uno/alerter_link.py --demo                   # Test A, automatically
python hardware/alerter_uno/alerter_link.py --replay narragansett:F7 --days 400   # real history
python hardware/alerter_uno/alerter_link.py --today --p 0.62 --chl 7.4 --start 2026-11-10
```

- Every Uno reply is checked against the Python controller; any `MISMATCH` is printed and logged.
- Log: `hardware/alerter_uno/logs/alerter_log.csv` (not committed).
- **Uno resets:** opening the USB port restarts an Uno and wipes its ON/OFF state. `--today` replays the
  earlier days from the log with the buzzer muted (`mute 1`), then sends today's line.
- Add `--sim` to any command to try it with no board (a stand-in Uno built from the Python controller).
- **Checked on the real Uno (2026-09-27):** `--demo` (lights, beeps and relay clicks right), and all 3,287 days of
  Narragansett station F7 in 50 s: 115 ON days, 10 episodes (6 ended at MAX_ON, as expected on untreated
  water), **0 mismatches** with the Python controller, including days with missing `p` or chlorophyll.
- Later: read chlorophyll, temperature and pH from the Uno's sensors, and get `p` from the model automatically.

- **Loop settings (2026-09-28):** `--mode H` (default; arm B), `--warm <mean>`, `--floor 0.8` (0 for arm D),
  `--maxon 0|3`, `--temp-lo 10 --temp-hi 17`, `--stop "reason"` (logged manual safety stop). Values
  are sent with 6 significant figures and the Python reference uses the sent value, so a reading right
  at a threshold cannot disagree.

**Done when:** a 48-hour test logs with no gaps, and unplugging the USB and reconnecting it recovers cleanly.

## Stage 8: dry run on a real tank (Oct 26 - Nov 9)

Run one tank of plain seawater + culture at low nutrients for 2 weeks, exactly as the warm-up
will run:
- sensors logging;
- daily hand measurements;
- the loop active on the rule trigger (`--mode R --warm <warm-up mean>`).

**Done when:**
- 14 days with no missing daily rows;
- the fluorometer tracks the cell counts;
- nothing overheats, leaks or drifts.

Then the real 21-day warm-up starts on Nov 10.

## Stage 9: dosing module, inline dilution (added 2026-10-03; ~$70)

The peroxide is never squirted straight into the water. A circulation pump draws water in, the dosing
pump meters peroxide into that stream, a mixing hose blends it, and the mix leaves beside the air
stone. In the field the reservoir holds **7% H₂O₂**; on the bench it holds the **0.1% working
dilution** (`PROCEDURES.md` P6), because 0.8 mg/L in 10 L is only 0.11 mL of 7%, too little to meter.

```
water → intake (2-5 mm screen) → circulation pump (12 V) → mixing tee → 1 m mixing hose → outlet beside the air stone
H₂O₂ jug (opaque HDPE, float switch) → peristaltic dosing pump → check valve ──────┘ (into the tee)
```

**Parts:** 2-channel 5 V relay module; 12 V circulation pump (bench: small aquarium pump; field:
10-20 L/min); the peristaltic dosing pump (stage 2); intake screen; check valve; tee + 1 m hose (or an
inline static mixer); flow switch; float switch; opaque HDPE jug; peroxide-compatible tubing
(silicone in the pump head, PE/PVC elsewhere). Details in `notes/mitigation/MATERIALS_LIST.md`.

**Wiring:**
- Relay channel 1 IN → **D10** (dosing pump, as before); channel 2 IN → **D12** (circulation pump).
  Each pump's 12 V + goes through its channel's COM → NO. A 2-channel module is usually active-low:
  set `RELAY_ACTIVE_LOW = true` (it applies to both channels).
- Flow switch between **D8** and GND (closed = flow). Float switch between **D4** and GND (closed =
  reservoir low). Both use the Uno's internal pull-ups, so no resistors.
- Set `USE_DOSER 1` at the top of `alerter_uno.ino` (with it at 0 the sketch behaves exactly as before).

**What the firmware does** (with `pulse <s>` > 0): each pulse runs **PRIME** (circulation only, 5 s) →
**DOSE** (circulation + dosing pump, `pulse` seconds) → **FLUSH** (circulation only, `flush` seconds,
default 90) → idle, printing `DOSER prime`, `DOSER dose`, `DOSER flush`, `DOSER idle`.
- **No-flow interlock:** no flow at the end of PRIME, or flow lost for more than 0.5 s during DOSE →
  both pumps stop, `DOSE_ABORT no_flow`, 3 beeps, white LED. Later pulses print `pulse=aborted` and
  do not run until the intake is fixed and `pulse <s>` is sent again (or `reset`).
- **Reservoir low:** the float is checked every 10 s; on LOW it prints `REFILL` once and lights the
  white LED. Dosing still runs (the jug holds a margin below the float).
- `status` adds `flush=`, `circ=`, `flow=`, `level=` (and `dose=FAULT` after an abort).

**Pump calibration:**
1. Fill the jug with the solution it will dose (bench: 0.1%). Prime the dosing pump's tube.
2. Run the dosing pump for **30 s** into a 10 or 25 mL graduated cylinder; repeat 3 times; average.
3. Rate (mL/s) = volume ÷ 30. `pulse` seconds = pulse volume ÷ rate, rounded to whole seconds.
   Bench example: 50 mL in 30 s = 1.67 mL/s; 8 mL of 0.1% per 10 L → `pulse 5`. If the rounding error
   is over 5%, use a slower pump or a weaker working dilution.
4. Record the rate in the design log; re-check it at every service visit (tubing wears).

**Dry bench test** (LEDs in place of the pumps, jumper wires as the switches):
1. `x 1`, `maxon 3`, `pulse 3`, flow jumper D8 → GND, then `2 0.6 4` → `START ... pulse=3s`, then
   `DOSER prime`, `DOSER dose` (3 s), `DOSER flush` (90 s), `DOSER idle`, with the LEDs in that order.
2. Remove the flow jumper and send the next check day (`3 0.6 4`) → `DOSE_ABORT no_flow` after 5 s, 3
   beeps, white LED. The next check day prints `pulse=aborted`; `pulse 3` re-arms it.
3. Ground D4 → `REFILL` within 10 s, white LED on.

**Water mixing test** (10 L tank of seawater, 0.1% in the jug, pump calibrated): run one pulse, then
measure H₂O₂ with the low-range kit at the **outlet** and the **far corner** at 1, 5 and 15 min.

**Done when:**
- the dry test prints the three sequences above;
- in the water test the far corner reads **0.8 ± 0.2 mg/L by 15 min** and the outlet reads **< 5 mg/L
  at 5 min** (no hot spot).

## Optional: servo (D11; planned for the fluorometer wiper and reference target)

Since 2026-10-01 no treatment needs a servo (aeration and peroxide are switched by the relay). It is
kept for the planned wiper and reference target (stage 5, "Autonomous accuracy"); that code is not
written yet, and today `USE_SERVO` only moves the servo with the treatment state.
- **Wiring:** servo signal (orange/yellow) → **D11**; servo red → an external 5-6 V supply (not the
  Uno's 5 V pin: a stalled servo browns out the Uno); servo brown/black → GND, **shared with the Uno's GND**.
- **Code:** set `USE_SERVO 1` (Servo library, built in). The servo goes to the ON angle while
  treatment is ON and back to the OFF angle otherwise. `servo 90 0` sets the ON / OFF angles.
- The Servo library takes Timer1, so pins 9 and 10 lose PWM. That is fine here: the white LED (D9) and
  the relay (D10) only use on/off.
- **pH note:** `readPhVolts` assumes a 5.000 V reference. USB gives 4.7-5.1 V, so recalibrate the pH
  probe (`cal686`, `cal918`) whenever the power source changes, and run from the same supply.
