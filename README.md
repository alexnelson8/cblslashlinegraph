# Canadian Baseball League (CBL) Player Stat Trajectory (2026)

An interactive, dark-themed analytical dashboard displaying the game-by-game evolution of player batting statistics—**Batting Average (AVG)**, **On-Base Percentage (OBP)**, **Slugging Percentage (SLG)**, and **On-Base Plus Slugging (OPS)**—across the 2026 Regular Season.

Built in the exact aesthetic and architecture as the CBL Run Matrix tool.

---

## 🌟 Key Features

1. **Unified Sliding Y-Axis Dynamic Scaling**:
   - **True Visual Alignment**: All four metrics (**AVG**, **OBP**, **SLG**, and **OPS**) share a single, unified vertical scale. Because $\text{OPS} = \text{OBP} + \text{SLG}$, the amber OPS line is now **always rendered in true visual hierarchy above Slugging and On-Base Percentage**, completely eliminating deceptive dual-axis crossing where OPS appeared lower than Slugging.
   - **Auto-Fit Adaptive Range (Default)**: Automatically zooms the vertical axis tightly around the player's active visible metrics within your selected game window. For example, if you toggle off OPS to focus on AVG, OBP, and SLG, the axis automatically zooms in on that narrower band (e.g. `.250` to `.580`); if you view AVG alone, it zooms specifically to `.260` to `.360`.
   - **0-Baseline Toggle**: One-click switch back to a fixed 0-to-1.000+ baseline when absolute comparison to zero is preferred.
   - **Active Scale Indicator**: Live footer badge displaying the exact active scale bounds (e.g. `Sliding Axis: [.250 – 1.050]`).

2. **Game Range Filtering (e.g. Games 4–40)**:
   - **Dual Interactive Controls**: Set custom game windows via number inputs (`From G#` / `to G#`) or synchronized range sliders.
   - **Quick Window Presets**: Instant buttons for `All`, `Last 5`, `Last 10`, `Last 20`, `1st Half`, and `2nd Half`.
   - **In-Window Split Performance Banner**: Automatically calculates the isolated slash line (AB, R, H, 2B, 3B, HR, RBI, BB, SO, AVG, OBP, SLG, OPS) exclusively across the selected game span.
   - **Synchronized Game Log Table**: The game log table automatically filters to only show games in your chosen window.

3. **Multi-Line Progression Chart**:
   - Interactive line chart tracking **AVG**, **OBP**, **SLG**, and **OPS** game by game.
   - **Dual Y-Axis**: Left axis calibrated for rate stats (.000 to .700+), Right axis calibrated for OPS (.000 to 1.500+).
   - **Metric Toggles**: Clickable chips to toggle any combination of metrics (or view all 4 simultaneously). Axis automatically recalibrates when metrics are toggled.
   - **Dual Progression Modes**:
     - 📈 **Cumulative Season-to-Date**: Track cumulative season slash line progression after each game.
     - 🌊 **5-Game Rolling Trend**: Spot hot and cold streaks over 5-game sliding windows.
   - **Rich Hover Tooltips**: Inspect date, opponent, game score, single-game stat line (e.g. *2-for-4, 1 HR, 2 RBI, 1 BB*), and exact cumulative metrics at every data point.

4. **Player Spotlight Card**:
   - Player headshot with fallback avatar.
   - Official team logo and position badge.
   - Key season totals: Games, Plate Appearances, At-Bats, Hits, Home Runs, RBIs, Walks, Strikeouts.
   - Big bold final 2026 slash line: AVG, OBP, SLG, OPS.
   - Peak OPS and lowest OPS milestones during the season.

5. **Search & Cohort Filtering**:
   - **Team Selector**: Filter to any of the 9 CBL franchises (*Barrie Baycats, Brantford Red Sox, Chatham-Kent Barnstormers, Guelph Royals, Hamilton Cardinals, Kitchener Panthers, London Majors, Toronto Maple Leafs, Welland Jackfish*).
   - **Quick Cohort Pills**: All Hitters, Qualified Hitters (PA ≥ 80), and League OPS Leaders (OPS ≥ .850).
   - **Instant Search**: Autocomplete search by player name, team, or position with keyboard navigation.
   - **Random Player Picker**: One-click exploration of any hitter in the league.

6. **Interactive Chronological Game Log**:
   - Complete table of every game played by the selected hitter in the active game range.
   - Shows single-game line (AB, R, H, 2B, 3B, HR, RBI, BB, SO, Summary) and running cumulative stats.
   - Multi-hit games and Home Run games highlighted.
   - **Interactive Cross-Linking**: Clicking any row in the game log highlights that exact point on the chart; clicking a chart point scrolls to and highlights that row in the table.
   - **CSV Export**: One-click download of the player's game log for the filtered window.

---

## 🚀 How to Open

### Method 1: Direct File Open (Zero Server Required)
Double-click or open either of these files directly in your web browser (Chrome, Edge, Firefox, Safari):
- `cbl_2026_player_progression_interactive.html`
- `index.html`

### Method 2: Local Server
Run the included python server:
```bash
python serve.py
```
This automatically starts a local server on port 8080 and launches `http://localhost:8080/` in your browser.

---

## 🛠 Rebuilding or Updating Data

The workspace includes scripts to refresh and regenerate the data directly from the official CBL APIs:
```bash
# 1. Process game logs and compute cumulative & rolling progression
python process_player_progression.py

# 2. Compile standalone dashboard HTML with embedded data
python build_dashboard.py
```
