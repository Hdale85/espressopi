# Decent DE1 App Features Analysis for EspressoPi

Pulled from video transcript of Decent DE1 app walkthrough. Notes on what to prioritize.

## Phase 1 (Current/Near-term)

### UI/Workflow
- ✅ **Workflow tabs** — FLUSH, ESPRESSO, STEAM, WATER (workflow order)
- ✅ **Real-time charts** — Pressure, flow, temperature, weight overlaid during shot
- ✅ **Live stats** — Time breakdown (preinfusion vs pour), pressure peak, volume, temp
- **Profile selector** — Easy profile switching (we have this in sidebar)
- **Shot notes** — User can add text description after shot

### Pressure Profiling
- ✅ **3-step pressure editor** — Preinfusion, rise, decline
- **Auto preinfusion trigger** — Stop preinfusion at 4 bar (not fixed time)
- **Pressure limiting** — Allow max pressure adjustment
- **Flow rate limiting** — Prevent gushers (limit max flow at given pressure)
- **Decline control** — Adjust end pressure to control acidity

### Flow Profiling
- **Flow-controlled preinfusion** — Ramp to target flow quickly
- **Constant flow shots** — Mimic manual lever by holding flow rate
- **Adjustable flow rates** — Different flows for light vs dark roasts

### Advanced Features
- **Stop by weight** — Auto-stop shot when reaching target output weight
- **Temperature profiles** — Declining temp curves (not just flat)
- **Shot statistics** — Peak pressure, avg pressure, extraction yield %

### Steam Control
- **Adjustable steam flow rate** — 0.4-2.2 ml/sec slider (dry vs wet steam)
- **Auto-stop timer** — Set steam to stop after X seconds
- **2-tap steam stop** — Tap once to stop steam, tap again to purge

### Hot Water Tab
- **Customizable water temp** — Set temp for Americanos (50-90°C)
- **Customizable flow rate** — Control water delivery speed
- **Stop by weight** — Auto-stop at target volume/weight

## Phase 2 (After hardware + basic operation)

### Machine Settings
- **Cleaning profile** — Automated backflush with water + cleaner
- **Descaling mode** — Automated descale routine with citric acid
- **Energy saver** — Auto cool-down after X minutes of inactivity
- **Keep hot schedule** — Wake/sleep times (e.g., warm up at 8:30am, sleep at 6pm)
- **Eco steam mode** — Turn off steam heater when idle to save power
- **Transport mode** — Drain machine for travel/storage

### Skins/UI Customization
- ✅ **Theme system** (we're building this)
- **Multiple skins** — Streamline (speed-focused), DSx (power users), Metric (accessibility)
- **Screen savers** — Custom images when machine sleeps
- **Screen brightness control** — Dynamic brightness with battery awareness

### Data & Logging
- **Shot history** — Detailed log with all readings + notes
- **Describe Your Espresso** — Rich shot metadata (beans, grind, taste notes, comparisons)
- **Shot comparison** — Overlay previous shots vs current for dial-in
- **Extraction yield** — Calculate % extraction based on dose + output weight

### Extensions/Integrations
- **Visualizer.coffee integration** — Upload/download shot profiles + compare with community
- **Graphical flow calibrator** — Visual tool to dial in flow calibration
- **D-Flow extension** — Simplified profile editor for beginners
- **MQTT home automation** — Integrate with Apple Home, Google Home

### Settings Architecture
- **MACHINE settings** — Affect espresso machine (firmware, calibration, schedules)
- **APP settings** — Affect UI (language, brightness, skin, extensions, resolution)
- **Bluetooth pairing** — Auto-detect scales, manual pairing fallback

## Phase 3 (Long-term/Community-driven)

### Advanced Profiling
- **Adaptive profiles** — Profiles that adjust based on real-time feedback
- **Manual lever simulation** — Flow-controlled profiles mimicking pressure-driven lever machines
- **Combo profiles** — Pressure + flow layers in single profile
- **Profile versioning** — Track changes, rollback to previous versions

### Machine Intelligence
- **Gusher detection** — Alert when flow too high, suggest adjustments
- **Dialing-in assistant** — Guide user through shot-to-shot refinement
- **Bean-to-profile mapping** — Recommend profiles based on bean characteristics
- **Auto-calibration** — Detect and correct for voltage/altitude differences

### Community & Sharing
- **Profile marketplace** — Community contributes + votes on profiles (like we're building!)
- **Recipe workflows** — Step-by-step brewing guides with photos
- **Shot leaderboards** — Compare metrics with other users

## Not Priority (Decent-specific hardware)

- ✅ SCACE precision calibration (we have mocked sensors; real calibration TBD)
- ✅ Dual heater control (future hardware feature)
- Refill kit auto-detect (our system uses manual water tank)
- USB charging optimization for tablets (not relevant on Pi)

---

## Feature Tiers for Implementation

### Tier 1 (MVP - ship with hardware)
- Workflow tabs (FLUSH, ESPRESSO, STEAM, WATER)
- Real-time pressure/flow/temp/weight charts
- 3-step pressure profile editor
- Shot notes + basic logging
- Profile selector
- Live stats (peak, avg, time breakdown)
- Stop by weight

### Tier 2 (Post-launch, quick wins)
- Auto preinfusion trigger (4 bar)
- Flow limiting + gusher prevention
- Temperature profiles
- Cleaning profile
- Energy saver schedule
- Shot history UI

### Tier 3 (Community-focused)
- Marketplace integration (we're already building this!)
- Describe Your Espresso (rich shot metadata)
- Visualizer.coffee export
- Community profile voting
- Flow profiling (advanced)

### Tier 4 (Nice-to-have)
- Multiple skins/themes (we have framework)
- Home automation (MQTT)
- Graphical calibrator
- Bean characteristics → profile mapping

---

## Key Insights from Decent

1. **Pressure vs Flow** — Decent emphasizes flow is "most important in extraction theory"
   - We should support flow profiling early, not just pressure
   
2. **Pre-infusion automation** — Auto-trigger at 4 bar instead of fixed time is huge
   - Removes inconsistency between dry and wet tubes
   - Much more user-friendly than guessing

3. **Profile descriptions matter** — Decent profiles come with detailed notes
   - "Why does this profile exist?"
   - "What roast level is it for?"
   - "How to dial in"
   - We should enforce this in marketplace profiles

4. **Shot comparison is critical** — Users want to overlay last shot vs target
   - Chart comparison, not just numbers
   - Essential for dial-in workflow

5. **Modular UI** — Decent's "skins" (Streamline, DSx, MimojaCafe) show
   - Different people want different workflows
   - Theme system alone isn't enough; layout flexibility needed
   - Worth investigating modular component architecture

6. **Energy efficiency** — Eco steam (saves 2/3 power), transport mode
   - Important for home users
   - Could be battery-saver for portable setups

7. **Accessibility** — Metric skin designed for disabled users
   - Simple, clear, obvious
   - Worth keeping in mind for inclusive design

---

## Potential Dealbreakers We Don't Have

- **Scale integration** — Decent tightly integrates Bluetooth scales
  - We need this for stop-by-weight
  - Plan: generic Bluetooth scale support or hardwire specific models?

- **Descaling automation** — Decent has step-by-step guided descale
  - We don't have flow control for cleaning water + citric acid
  - Could simulate, but less critical than espresso control

- **SCACE precision calibration** — Decent uses precision equipment
  - We have mocked sensors for now
  - Real hardware will need proper calibration workflow

---

## What NOT to Copy

- Tablet-specific tweaks (font size, resolution, flip display) — Pi + touchscreen are fixed
- Smart charging modes — Pi hardware handles this
- Multiple skins as primary differentiation — focus on ONE great default, theme customization instead
