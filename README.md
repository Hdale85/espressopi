# EspressoPi

**Open source Raspberry Pi espresso machine controller.**

Turn any commercial or prosumer espresso machine into a precision shot computer — pressure profiling, real-time graphs, shot logging, volumetric dosing, and a beautiful widescreen UI.

---

## What It Does

- **Pressure profiling** — define custom brew curves (ramp, flat, decline)
- **Pre-infusion control** — configurable low-pressure pre-soak before full extraction
- **Real-time display** — live pressure curve, shot timer, dose counter on a widescreen touch display
- **Shot logging** — every shot recorded (time, pressure curve, dose, temp, date) in SQLite
- **Volumetric dosing** — stop by dose (ml) or time
- **Group head temperature** — K-type thermocouple at the puck
- **Boiler pressure monitoring** — dual pressure transducers (brew + steam circuits)
- **Scale integration** *(Phase 2)* — stop by weight via Bluetooth scale
- **Visualizer export** *(Phase 3)* — export to [Visualizer.coffee](https://visualizer.coffee)

---

## Reference Build

**Machine:** Wega IO 1GR (commercial HX machine)

The reference build keeps the original GICAR safety board active for boiler PID, water level, and safety cutoffs. The Pi runs **in parallel**, intercepting only shot-related outputs (group solenoid, pump enable) and adding sensor inputs (pressure, temperature).

This hybrid approach means:
- Boiler safety is handled by battle-tested commercial hardware
- Pi failure = machine falls back to manual operation
- No voiding of safety systems

---

## Hardware

| Component | Purpose |
|-----------|---------|
| Raspberry Pi 4 | Main controller |
| 14" IPS 1920×550 touch display | Full-width front panel UI |
| ADS1256 24-bit ADC (SPI) | Reads pressure transducers |
| 2× G1/4 BSP pressure transducer (0-5V) | Brew pressure + boiler/steam pressure |
| MAX31855 thermocouple amplifier (SPI) | Group head temperature |
| K-type M6 screw-in thermocouple | Mounts in E61 group head boss |
| 4-channel AC SSR board | Switches group solenoid + pump enable |
| KNF/gear pump pulse signal (existing) | Volumetric dosing — no flow meter needed |

**Estimated parts cost:** ~$150-200 (excluding Pi and display)

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Raspberry Pi 4                  │
│                                              │
│  SPI ──── ADS1256 ──── Brew pressure         │
│                   └─── Boiler pressure       │
│  SPI ──── MAX31855 ─── Group temp            │
│  GPIO ─── SSR ──────── EV1 group solenoid    │
│  GPIO ─── SSR ──────── Pump enable (STEMME)  │
│  GPIO ─── DAC ──────── Pump speed (profiling)│
│  GPIO ─── Pulse in ─── KNF dosing pulses     │
│  HDMI ──────────────── 14" touch display     │
└─────────────────────────────────────────────┘
         │ (runs in parallel, does not replace)
┌─────────────────────────────────────────────┐
│         GICAR Safety Board (untouched)       │
│  Boiler PID, water level, safety cutoffs     │
└─────────────────────────────────────────────┘
```

---

## Software Stack

- **Python 3** on Raspberry Pi OS
- **Pygame** — fullscreen 1920×550 UI
- **SQLite** — shot log database
- **FastAPI** — local web interface
- Waveshare ADS1256 library
- Adafruit MAX31855 library

---

## Status

🔧 **In development** — hardware arriving, software not yet started.

- [x] Architecture designed
- [x] Parts ordered
- [ ] Hardware assembly
- [ ] Sensor wiring + testing
- [ ] UI development
- [ ] Shot control logic
- [ ] Shot logging
- [ ] Pressure profiling

---

## License

MIT + Commons Clause — free for personal/hobbyist use.
Commercial use requires explicit permission from the author.
See [LICENSE](LICENSE) for full terms.

Commercial licensing inquiries: hdaleoc@gmail.com

---

## Inspiration

- [Decent DE1](https://decentespresso.com/) — the gold standard espresso machine
- [Gaggiuino](https://gaggiuino.github.io/) — open source Gaggia Classic controller
- [Visualizer.coffee](https://visualizer.coffee) — shot logging platform
