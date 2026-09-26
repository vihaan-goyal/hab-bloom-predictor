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
| pH | safety (seaweed, peroxide raise it) | analog pH probe | auto | 4 |
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

**Progress:** stages 1 and 2 passed on 2026-09-26: Test A, lights, buzzer, and the bare relay
clicking on D10 (LED as the pretend pump; the real pump isn't bought yet).

## Shopping list (what to order now)

Already on hand: Uno, breadboard, M-M wires, blue/green/white LEDs, 220/330/10k Ω resistors,
PN2222A transistors, passive buzzer, bare 5 V relay, 1N4007 diode.

| # | Item | For | Approx. |
|---|---|---|---|
| 1 | Male-to-female jumper wires (40-pack) | relay pins, sensor boards | $6 |
| 2 | 12 V aquarium air pump + 12 V 1-2 A DC adapter + DC barrel-jack screw-terminal adapter | stage 2 (the real pump) | $20 |
| 3 | DS18B20 **waterproof** temperature probe | stage 3 | $8 |
| 4 | Analog pH probe kit (BNC probe + PH-4502C board) + pH 7.00 and 10.00 buffer packets | stage 4 | $30 |
| 5 | Adafruit TSL2591 light sensor + red gel filter sheet + 4.5 mL square cuvettes + bright 470 nm blue LEDs | stage 5 | $20 |
| | **Total** | | **~$85** |

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
| D2 | 1 kΩ → NPN transistor base; buzzer between 5V and the collector; emitter → GND |
| D3 | DS18B20 yellow wire, 4.7 kΩ to 5V (stage 3) |
| 5V / GND | breadboard rails |

`schematic.png` (drawn by `draw_schematic.py`) is the same circuit as a circuit diagram, plus the
bare-relay driver that circuito can't draw.

The sketch drives a **passive** buzzer (it plays a 2 kHz tone). A passive buzzer can also go
straight from D2 to GND without the transistor; it's just a bit quieter. Change `BUZZ_HZ` for a
different pitch.

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

**Other commands:**
- `status`
- `x 2`, `cok 4.5`
- `mode R` + `warm 1.8` switches to the rule trigger (chl rose 2 days AND > 2 × warm-up mean)
- `stop` for a safety stop, e.g. when the DO kit reads < 4 mg/L

**Done when:** Tests A and B print exactly the lines above, and the LEDs and buzzer match.

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
- Set `USE_DS18B20 1` in the sketch.
- It reads every 10 s and alarms outside 14-22 °C (yellow LED, fast beeps); `status` shows the reading.

**Done when:**
- the probe agrees with a kitchen thermometer within 0.5 °C in a glass of water;
- ice water triggers the alarm, and room-temperature water clears it.

## Stage 4: pH probe (~$30)

**Parts:**
- analog pH probe kit with a BNC probe and the blue PH-4502C board (or DFRobot Gravity pH);
- pH 7.00 and 10.00 buffer powder packets (pH 4 optional);
- distilled water for rinsing.

**Wiring:** board V+→5V, G→GND, Po→**A0**.

**Code:** I'll add it when you get here: a two-point calibration (`cal7`, `cal10` commands) and pH in `status` and the log.

**Tips:**
- Store the probe tip wet (its cap with storage solution), never dry.
- The probe can read noisily when the air pump shares the water. Compare readings with the pump on and off.

**Done when:**
- pH 7 and pH 10 buffers read within ±0.1 after calibration;
- seawater reads ~7.9-8.3 and agrees with a test strip.

## Stage 5: the fluorometer, chlorophyll (~$20, the hard part)

A blue LED makes chlorophyll glow red. A light sensor behind a red filter measures that glow.

**Parts:**
- TSL2591 light-sensor breakout (Adafruit, works on 5 V);
- 470 nm blue LEDs + 220 Ω;
- red gel filter sheet (Roscolux/Lee "primary red", or a red theatre gel sample pack);
- square plastic cuvettes (4.5 mL);
- a small black box (3D print, or black foam board and tape).

**Layout:** the LED shines into the cuvette from one side. The sensor, behind the red filter, looks
in from 90° so it sees the glow, not the LED. Keep everything light-tight.

**Wiring:** TSL2591 VIN→5V, GND→GND, SDA→**A4**, SCL→**A5**; blue LED on **D7** → 220 Ω → GND.

**Code:** I'll add it when you get here:
- a `read` that turns the LED on, averages 10 sensor readings, and subtracts a dark reading;
- then `chl` comes from the sensor instead of being typed.

**Calibration** (once cultures arrive):
1. Make a dilution series of the culture (100%, 50%, 25%, 12.5%, 6%, 0% in seawater).
2. Read each one 3 times.
3. Cell-count each one.
4. Fit reading vs cells (and µg/L if extracted chlorophyll is possible).

**Done when:**
- the blank (seawater only) reading is stable within ±5% over 10 minutes;
- the dilution series is a straight line (R² > 0.95).

**Curcumin** is yellow and fools the reading. Use cell counts for that method.

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

- `pip install pyserial`.
- A short Python script (I'll write it):
  1. once a day, reads the Uno's chlorophyll, temperature and pH, plus your typed DO and salinity;
  2. runs the model to get `p`;
  3. sends `<day> <p> <chl>` to the Uno;
  4. saves everything to a CSV.
- The Uno also prints its sensor readings every 10 min, so nothing is lost if a daily step is missed.

**Done when:** a 48-hour test logs with no gaps, and unplugging the USB and reconnecting it recovers cleanly.

## Stage 8: dry run on a real tank (Oct 26 - Nov 9)

Run one tank of plain seawater + culture at low nutrients for 2 weeks, exactly as the warm-up
will run:
- sensors logging;
- daily hand measurements;
- the loop active on the rule trigger.

**Done when:**
- 14 days with no missing daily rows;
- the fluorometer tracks the cell counts;
- nothing overheats, leaks or drifts.

Then the real 21-day warm-up starts on Nov 10.
