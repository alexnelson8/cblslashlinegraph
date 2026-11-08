import json
import os

def generate_interactive_html():
    with open('cbl_2026_player_progression.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to compact JSON string
    json_str = json.dumps(data, separators=(',', ':'))

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>2026 CBL Player Stat Trajectory | AVG, OBP, SLG, OPS</title>
  <!-- Tailwind CSS -->
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
  <script>
    // Fallback to local Chart.js if CDN fails
    if (typeof Chart === 'undefined') {{
      document.write('<script src="chart.umd.min.js"><\\/script>');
    }}
  </script>
  <style>
    /* Custom scrollbars */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: #0f172a;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #334155;
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #475569;
    }}

    .metric-chip {{
      transition: all 0.2s ease;
      user-select: none;
    }}
    .metric-chip.active {{
      border-color: currentColor;
      box-shadow: 0 0 12px -2px currentColor;
    }}
    .metric-chip.inactive {{
      opacity: 0.35;
      border-color: #334155 !important;
      background-color: transparent !important;
      color: #94a3b8 !important;
    }}

    .log-row:hover {{
      background-color: rgba(59, 130, 246, 0.08);
      cursor: pointer;
    }}
    .log-row.highlighted {{
      background-color: rgba(59, 130, 246, 0.2) !important;
      outline: 1px solid #3b82f6;
    }}

    /* Custom range slider styling */
    input[type=range] {{
      -webkit-appearance: none;
      background: #1e293b;
      height: 6px;
      border-radius: 3px;
      outline: none;
    }}
    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #3b82f6;
      cursor: pointer;
      border: 2px solid #0f172a;
      box-shadow: 0 0 6px rgba(59, 130, 246, 0.5);
    }}
    input[type=range]::-moz-range-thumb {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: #3b82f6;
      cursor: pointer;
      border: 2px solid #0f172a;
      box-shadow: 0 0 6px rgba(59, 130, 246, 0.5);
    }}
  </style>
</head>
<body class="bg-[#0b1120] text-[#f8fafc] antialiased min-h-screen p-4 md:p-8 font-sans">
  <div class="max-w-7xl mx-auto space-y-6">

    <!-- Top Header -->
    <header class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#1e293b] pb-6">
      <div>
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <span class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
            Official 2026 Regular Season
          </span>
          <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            173 Batters • 215 Games
          </span>
          <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
            Interactive Progression & Range Filtering
          </span>
        </div>
        <h1 class="text-2xl md:text-3xl lg:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
          CBL Player Stat Trajectory
        </h1>
        <p class="text-slate-400 text-sm mt-1 max-w-3xl">
          Track the game-by-game evolution of Batting Average (AVG), On-Base Percentage (OBP), Slugging (SLG), and OPS with sliding Y-axis dynamic scaling and customizable game window ranges.
        </p>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center gap-3">
        <button onclick="pickRandomPlayer()" class="flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-[#1e293b] hover:bg-[#334155] border border-[#334155] text-slate-200 transition-all shadow-sm">
          <span>🎲 Random Player</span>
        </button>
        <button onclick="exportCurrentPlayerCsv()" class="flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-[#1e293b] hover:bg-[#334155] border border-[#334155] text-slate-200 transition-all shadow-sm">
          <span>📥 Export Game Log</span>
        </button>
      </div>
    </header>

    <!-- Controls Bar: Team Filter, Quick Filters, Player Search -->
    <div class="bg-[#131d31] border border-[#1e293b] rounded-xl p-4 md:p-5 shadow-lg space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
        
        <!-- Team Selector -->
        <div class="md:col-span-4">
          <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Filter by Team</label>
          <div class="relative">
            <select id="team-filter" onchange="onTeamFilterChange()" class="w-full bg-[#0b1120] border border-[#334155] rounded-lg px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 appearance-none cursor-pointer">
              <option value="ALL">All Teams (173 Players)</option>
              <!-- Filled dynamically -->
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>

        <!-- Filter Quick Pills -->
        <div class="md:col-span-4">
          <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Quick Cohorts</label>
          <div class="flex items-center gap-1.5 bg-[#0b1120] p-1 rounded-lg border border-[#334155]">
            <button id="pill-all" onclick="setCohort('ALL')" class="flex-1 py-1.5 px-2 rounded-md text-xs font-medium transition-colors bg-blue-600 text-white shadow-sm text-center">
              All Hitters
            </button>
            <button id="pill-qualified" onclick="setCohort('QUALIFIED')" class="flex-1 py-1.5 px-2 rounded-md text-xs font-medium transition-colors text-slate-400 hover:text-white text-center">
              PA ≥ 80
            </button>
            <button id="pill-ops-leaders" onclick="setCohort('OPS_LEADERS')" class="flex-1 py-1.5 px-2 rounded-md text-xs font-medium transition-colors text-slate-400 hover:text-white text-center">
              OPS ≥ .850
            </button>
          </div>
        </div>

        <!-- Searchable Player Select -->
        <div class="md:col-span-4">
          <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Select Player</label>
          <div class="relative">
            <input type="text" id="player-search-input" placeholder="Search player (e.g. Jaco, Machibroda)..." autocomplete="off" onfocus="openPlayerSearch()" oninput="filterPlayerDropdown()" class="w-full bg-[#0b1120] border border-[#334155] rounded-lg pl-9 pr-8 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500">
            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 text-sm">🔍</span>
            <button id="clear-search-btn" onclick="clearPlayerSearch()" class="hidden absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-white text-sm">✕</button>

            <!-- Autocomplete Results Dropdown -->
            <div id="player-dropdown" class="hidden absolute z-50 left-0 right-0 mt-1.5 max-h-72 overflow-y-auto bg-[#131d31] border border-[#334155] rounded-xl shadow-2xl divide-y divide-[#1e293b]">
              <!-- Dynamically populated -->
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Player Spotlight Card -->
    <div id="player-spotlight" class="bg-[#131d31] border border-[#1e293b] rounded-xl p-5 md:p-6 shadow-xl relative overflow-hidden">
      <!-- Decorative background glow -->
      <div class="absolute -top-24 -right-24 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
        
        <!-- Player Bio & Team -->
        <div class="lg:col-span-4 flex items-center gap-4">
          <div class="relative flex-shrink-0">
            <div id="player-avatar-wrap" class="w-20 h-20 md:w-24 md:h-24 rounded-full bg-[#0b1120] border-2 border-blue-500/40 p-1 flex items-center justify-center overflow-hidden shadow-inner">
              <img id="player-headshot" src="" alt="Player Headshot" class="w-full h-full object-cover rounded-full" onerror="handleHeadshotError(this)">
            </div>
            <img id="player-team-logo" src="" alt="Team Logo" class="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-[#0b1120] border border-[#334155] p-1 object-contain">
          </div>

          <div class="min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span id="player-pos-badge" class="px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider bg-blue-500/20 text-blue-400 border border-blue-500/30">UTIL</span>
              <span id="player-games-badge" class="text-xs text-slate-400">13 Games</span>
            </div>
            <h2 id="player-name" class="text-xl md:text-2xl font-bold truncate text-white">Hayden Jaco</h2>
            <p id="player-team-name" class="text-sm text-slate-400 truncate">Barrie Baycats</p>
            
            <div class="flex items-center gap-3 mt-2 text-xs text-slate-400">
              <span>PA: <strong id="player-pa" class="text-slate-200">44</strong></span>
              <span>AB: <strong id="player-ab" class="text-slate-200">36</strong></span>
              <span>H: <strong id="player-h" class="text-slate-200">14</strong></span>
              <span>HR: <strong id="player-hr" class="text-slate-200">2</strong></span>
              <span>RBI: <strong id="player-rbi" class="text-slate-200">9</strong></span>
            </div>
          </div>
        </div>

        <!-- 4 Big Key Stats -->
        <div class="lg:col-span-8 grid grid-cols-2 sm:grid-cols-4 gap-3">
          
          <!-- AVG Card -->
          <div class="bg-[#0b1120]/80 border border-emerald-500/20 rounded-xl p-3.5 text-center relative overflow-hidden group hover:border-emerald-500/40 transition-colors">
            <div class="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-1">Batting AVG</div>
            <div id="stat-avg" class="text-2xl md:text-3xl font-extrabold text-white font-mono">.389</div>
            <div class="text-[10px] text-slate-400 mt-1 flex items-center justify-center gap-1">
              <span id="stat-avg-diff" class="text-emerald-400 font-medium">H / AB</span>
            </div>
          </div>

          <!-- OBP Card -->
          <div class="bg-[#0b1120]/80 border border-sky-500/20 rounded-xl p-3.5 text-center relative overflow-hidden group hover:border-sky-500/40 transition-colors">
            <div class="text-[11px] font-bold text-sky-400 uppercase tracking-wider mb-1">On-Base (OBP)</div>
            <div id="stat-obp" class="text-2xl md:text-3xl font-extrabold text-white font-mono">.450</div>
            <div class="text-[10px] text-slate-400 mt-1 flex items-center justify-center gap-1">
              <span id="stat-obp-diff" class="text-sky-400 font-medium">(H+BB+HBP)/PA</span>
            </div>
          </div>

          <!-- SLG Card -->
          <div class="bg-[#0b1120]/80 border border-purple-500/20 rounded-xl p-3.5 text-center relative overflow-hidden group hover:border-purple-500/40 transition-colors">
            <div class="text-[11px] font-bold text-purple-400 uppercase tracking-wider mb-1">Slugging (SLG)</div>
            <div id="stat-slg" class="text-2xl md:text-3xl font-extrabold text-white font-mono">.611</div>
            <div class="text-[10px] text-slate-400 mt-1 flex items-center justify-center gap-1">
              <span id="stat-slg-diff" class="text-purple-400 font-medium">Total Bases / AB</span>
            </div>
          </div>

          <!-- OPS Card -->
          <div class="bg-[#0b1120]/80 border border-amber-500/20 rounded-xl p-3.5 text-center relative overflow-hidden group hover:border-amber-500/40 transition-colors">
            <div class="text-[11px] font-bold text-amber-400 uppercase tracking-wider mb-1">On-Base + Slug (OPS)</div>
            <div id="stat-ops" class="text-2xl md:text-3xl font-extrabold text-amber-300 font-mono">1.061</div>
            <div class="text-[10px] text-slate-400 mt-1 flex items-center justify-center gap-1">
              <span id="stat-ops-diff" class="text-amber-400 font-medium">OBP + SLG</span>
            </div>
          </div>

        </div>

      </div>

      <!-- Quick season highlights footer inside player card -->
      <div class="mt-4 pt-3 border-t border-[#1e293b] flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
        <div class="flex items-center gap-4">
          <span>🚀 Peak OPS: <strong id="peak-ops-val" class="text-amber-400 font-mono">1.244</strong> <span id="peak-ops-date" class="text-slate-400">(Aug 16)</span></span>
          <span>📉 Lowest OPS: <strong id="low-ops-val" class="text-slate-200 font-mono">.857</strong> <span id="low-ops-date" class="text-slate-400">(Jun 12)</span></span>
        </div>
        <div class="flex items-center gap-2">
          <span>2B: <strong id="sub-2b" class="text-slate-200">2</strong></span>
          <span class="text-slate-600">•</span>
          <span>3B: <strong id="sub-3b" class="text-slate-200">0</strong></span>
          <span class="text-slate-600">•</span>
          <span>BB: <strong id="sub-bb" class="text-slate-200">4</strong></span>
          <span class="text-slate-600">•</span>
          <span>SO: <strong id="sub-so" class="text-slate-200">5</strong></span>
          <span class="text-slate-600">•</span>
          <span>R: <strong id="sub-r" class="text-slate-200">10</strong></span>
        </div>
      </div>
    </div>

    <!-- Chart Controls & Graph Section -->
    <div class="bg-[#131d31] border border-[#1e293b] rounded-xl p-5 md:p-6 shadow-xl space-y-4">
      
      <!-- Graph Header & Toggles -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#1e293b] pb-4">
        <div>
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <span>📈</span>
            <span id="chart-main-title">Season Progression Trajectory</span>
          </h3>
          <p id="chart-subtitle" class="text-xs text-slate-400 mt-0.5">
            Running cumulative slash line across the selected game window.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          
          <!-- Progression Mode (Cumulative vs 5-Game Rolling) -->
          <div class="flex items-center bg-[#0b1120] p-1 rounded-lg border border-[#334155] text-xs">
            <button id="btn-mode-cum" onclick="setChartMode('cumulative')" class="px-3 py-1.5 rounded-md font-semibold transition-all bg-blue-600 text-white shadow-sm">
              Cumulative Season
            </button>
            <button id="btn-mode-roll" onclick="setChartMode('rolling')" class="px-3 py-1.5 rounded-md font-semibold transition-all text-slate-400 hover:text-white">
              5-Game Rolling Trend
            </button>
          </div>

          <!-- Y-Axis Scale Mode Toggle -->
          <div class="flex items-center bg-[#0b1120] p-1 rounded-lg border border-[#334155] text-xs">
            <button id="btn-scale-autofit" onclick="setScaleMode('autofit')" class="px-2.5 py-1.5 rounded-md font-semibold transition-all bg-emerald-600 text-white shadow-sm flex items-center gap-1.5" title="Auto-scale Y-axis tightly to highlight trends">
              <span>📐 Sliding Y-Axis</span>
            </button>
            <button id="btn-scale-fixed" onclick="setScaleMode('fixed')" class="px-2.5 py-1.5 rounded-md font-semibold transition-all text-slate-400 hover:text-white flex items-center gap-1.5" title="Fixed 0-Baseline scale">
              <span>0-Baseline</span>
            </button>
          </div>

          <!-- Metric Toggle Filter Chips -->
          <div class="flex items-center gap-1.5">
            <!-- AVG Chip -->
            <button id="chip-avg" onclick="toggleMetric('avg')" class="metric-chip active flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
              AVG
            </button>
            <!-- OBP Chip -->
            <button id="chip-obp" onclick="toggleMetric('obp')" class="metric-chip active flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500">
              <span class="w-2 h-2 rounded-full bg-sky-400"></span>
              OBP
            </button>
            <!-- SLG Chip -->
            <button id="chip-slg" onclick="toggleMetric('slg')" class="metric-chip active flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500">
              <span class="w-2 h-2 rounded-full bg-purple-400"></span>
              SLG
            </button>
            <!-- OPS Chip -->
            <button id="chip-ops" onclick="toggleMetric('ops')" class="metric-chip active flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500">
              <span class="w-2 h-2 rounded-full bg-amber-400"></span>
              OPS
            </button>

            <!-- Reset / Show All -->
            <button onclick="showAllMetrics()" title="Show All 4 Lines" class="p-1.5 rounded-md bg-[#0b1120] text-slate-400 hover:text-white border border-[#334155] text-xs">
              All
            </button>
          </div>

        </div>
      </div>

      <!-- Game Range Filter & Window Bar -->
      <div class="bg-[#0b1120] border border-[#1e293b] rounded-xl p-3.5 sm:p-4 space-y-3">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          
          <!-- Range Inputs & Pill -->
          <div class="flex flex-wrap items-center gap-2.5 text-xs">
            <span class="font-semibold text-slate-300 flex items-center gap-1.5">
              <span class="text-blue-400">📅</span> Filter Game Range:
            </span>
            <div class="flex items-center gap-1.5 bg-[#131d31] px-2.5 py-1 rounded-lg border border-[#334155]">
              <span class="text-slate-400">From G#</span>
              <input type="number" id="range-start-input" min="1" max="1" value="1" onchange="onRangeInputChange()" class="w-14 bg-[#0b1120] border border-[#334155] rounded px-1.5 py-0.5 text-center text-white font-mono focus:border-blue-500 focus:outline-none">
              <span class="text-slate-400">to G#</span>
              <input type="number" id="range-end-input" min="1" max="1" value="1" onchange="onRangeInputChange()" class="w-14 bg-[#0b1120] border border-[#334155] rounded px-1.5 py-0.5 text-center text-white font-mono focus:border-blue-500 focus:outline-none">
            </div>
            <span id="range-count-pill" class="px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              All Games
            </span>
          </div>

          <!-- Quick Presets -->
          <div class="flex flex-wrap items-center gap-1.5 text-xs">
            <span class="text-slate-400 mr-1 text-[11px] hidden sm:inline">Presets:</span>
            <button onclick="setRangePreset('all')" class="px-2.5 py-1 rounded bg-[#131d31] hover:bg-[#1e293b] text-slate-300 hover:text-white border border-[#334155] text-xs transition-colors">All</button>
            <button onclick="setRangePreset('last5')" class="px-2.5 py-1 rounded bg-[#131d31] hover:bg-[#1e293b] text-slate-300 hover:text-white border border-[#334155] text-xs transition-colors">Last 5</button>
            <button onclick="setRangePreset('last10')" class="px-2.5 py-1 rounded bg-[#131d31] hover:bg-[#1e293b] text-slate-300 hover:text-white border border-[#334155] text-xs transition-colors">Last 10</button>
            <button onclick="setRangePreset('last20')" class="px-2.5 py-1 rounded bg-[#131d31] hover:bg-[#1e293b] text-slate-300 hover:text-white border border-[#334155] text-xs transition-colors">Last 20</button>
            <button onclick="setRangePreset('firstHalf')" class="px-2.5 py-1 rounded bg-[#131d31] hover:bg-[#1e293b] text-slate-300 hover:text-white border border-[#334155] text-xs transition-colors">1st Half</button>
            <button onclick="setRangePreset('secondHalf')" class="px-2.5 py-1 rounded bg-[#131d31] hover:bg-[#1e293b] text-slate-300 hover:text-white border border-[#334155] text-xs transition-colors">2nd Half</button>
          </div>

        </div>

        <!-- Dual Slider Inputs -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div class="flex items-center gap-2">
            <span class="text-[11px] text-slate-400 w-12">Start:</span>
            <input type="range" id="range-slider-start" min="1" max="1" value="1" oninput="onSliderStartInput()" class="w-full accent-blue-500 cursor-pointer">
            <span id="slider-start-val" class="font-mono text-xs text-slate-200 w-8 text-right">1</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[11px] text-slate-400 w-12">End:</span>
            <input type="range" id="range-slider-end" min="1" max="1" value="1" oninput="onSliderEndInput()" class="w-full accent-blue-500 cursor-pointer">
            <span id="slider-end-val" class="font-mono text-xs text-slate-200 w-8 text-right">1</span>
          </div>
        </div>

        <!-- In-Window Performance Summary banner (shown when filtered) -->
        <div id="window-summary-bar" class="hidden pt-2.5 border-t border-[#1e293b] flex flex-wrap items-center justify-between gap-2 text-xs">
          <div class="flex flex-wrap items-center gap-2 text-slate-300">
            <span class="font-bold text-amber-400 flex items-center gap-1"><span>🎯</span> Isolated Window Split Line:</span>
            <span id="window-slash-line" class="font-mono text-emerald-400 font-bold bg-[#131d31] px-2 py-0.5 rounded border border-[#334155]">.000 AVG | .000 OBP | .000 SLG | .000 OPS</span>
            <span id="window-counting-stats" class="text-slate-400 font-sans">(0-for-0, 0 HR, 0 RBI)</span>
          </div>
          <button onclick="setRangePreset('all')" class="text-xs text-blue-400 hover:text-blue-300 underline font-medium">Reset Full Season ✕</button>
        </div>

      </div>

      <!-- Chart Container -->
      <div class="relative w-full h-[380px] md:h-[440px]">
        <canvas id="progressionChart"></canvas>
      </div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-400 pt-2 border-t border-[#1e293b]">
        <div class="flex items-center gap-2">
          <span>💡 Hover over any point for exact opponent, score, and single-game performance.</span>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <span id="axis-scale-indicator" class="font-mono text-[11px] text-slate-300 bg-[#0b1120] px-2.5 py-0.5 rounded border border-[#1e293b]">
            Scale: Auto-Scaled
          </span>
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> AVG</span>
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-sky-400"></span> OBP</span>
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-purple-400"></span> SLG</span>
          <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span> OPS</span>
        </div>
      </div>

    </div>

    <!-- Detailed Game Log Table Section -->
    <div class="bg-[#131d31] border border-[#1e293b] rounded-xl p-5 md:p-6 shadow-xl space-y-4">
      
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1e293b] pb-3">
        <div>
          <h3 class="text-base md:text-lg font-bold text-white flex items-center gap-2">
            <span>📋</span>
            <span>Regular Season Game Log</span>
            <span id="gamelog-count-badge" class="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-[#334155]">13 Games</span>
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Chronological record matching your selected game window.</p>
        </div>

        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">Sort:</span>
          <select id="log-sort" onchange="renderGameLogTable()" class="bg-[#0b1120] border border-[#334155] rounded-lg px-2.5 py-1 text-xs text-slate-200">
            <option value="chronological">Game 1 → Last (Earliest to Latest)</option>
            <option value="reverse">Last → Game 1 (Latest to Earliest)</option>
          </select>
        </div>
      </div>

      <!-- Table Container -->
      <div class="overflow-x-auto rounded-lg border border-[#1e293b]">
        <table class="w-full text-left text-xs whitespace-nowrap">
          <thead class="bg-[#0b1120] text-slate-400 uppercase tracking-wider text-[11px] border-b border-[#1e293b]">
            <tr>
              <th class="py-3 px-3 font-semibold text-center w-12">#</th>
              <th class="py-3 px-3 font-semibold">Date</th>
              <th class="py-3 px-3 font-semibold">Opponent</th>
              <th class="py-3 px-3 font-semibold text-center">Score</th>
              <th class="py-3 px-2 font-semibold text-center text-slate-200">AB</th>
              <th class="py-3 px-2 font-semibold text-center text-slate-200">R</th>
              <th class="py-3 px-2 font-semibold text-center text-slate-200">H</th>
              <th class="py-3 px-2 font-semibold text-center">2B</th>
              <th class="py-3 px-2 font-semibold text-center">3B</th>
              <th class="py-3 px-2 font-semibold text-center">HR</th>
              <th class="py-3 px-2 font-semibold text-center">RBI</th>
              <th class="py-3 px-2 font-semibold text-center">BB</th>
              <th class="py-3 px-2 font-semibold text-center">SO</th>
              <th class="py-3 px-3 font-semibold">Performance</th>
              <th class="py-3 px-3 font-semibold text-right text-emerald-400 font-mono">Cum AVG</th>
              <th class="py-3 px-3 font-semibold text-right text-sky-400 font-mono">Cum OBP</th>
              <th class="py-3 px-3 font-semibold text-right text-purple-400 font-mono">Cum SLG</th>
              <th class="py-3 px-3 font-semibold text-right text-amber-400 font-mono">Cum OPS</th>
            </tr>
          </thead>
          <tbody id="gamelog-tbody" class="divide-y divide-[#1e293b] font-medium text-slate-300">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>

      <div class="text-[11px] text-slate-500 italic">
        Tip: Click any row in the game log to highlight the corresponding performance dot on the trajectory graph.
      </div>

    </div>

    <!-- Footer -->
    <footer class="border-t border-[#1e293b] pt-6 pb-8 text-center text-xs text-slate-500">
      <p>Canadian Baseball League (CBL) Official Stats • 2026 Regular Season Progression Visualizer</p>
      <p class="mt-1 text-slate-600">Calculated from 215 regular season box scores & pitch-by-pitch feeds.</p>
    </footer>

  </div>

  <!-- Embedded Dataset & Logic -->
  <script>
    const RAW_DATA = {json_str};

    // Application State
    let currentTeam = "ALL";
    let currentCohort = "ALL";
    let currentPlayerId = null;
    let chartMode = "cumulative"; // 'cumulative' or 'rolling'
    let scaleMode = "autofit";    // 'autofit' (sliding tight scale) or 'fixed' (0 to 1.000)
    
    let rangeStart = 1;
    let rangeEnd = 1;
    let maxPlayerGames = 1;

    let activeMetrics = {{
      avg: true,
      obp: true,
      slg: true,
      ops: true
    }};
    let chartInstance = null;

    // Initialize application
    window.addEventListener('DOMContentLoaded', () => {{
      initTeamFilter();
      populateInitialPlayer();
    }});

    function initTeamFilter() {{
      const select = document.getElementById('team-filter');
      select.innerHTML = '<option value="ALL">All Teams (173 Players)</option>';
      RAW_DATA.teams.forEach(t => {{
        const opt = document.createElement('option');
        opt.value = t;
        opt.innerText = t;
        select.appendChild(opt);
      }});
    }}

    function populateInitialPlayer() {{
      const players = Object.values(RAW_DATA.players);
      // Prefer Hayden Jaco or Machibroda
      const found = players.find(p => p.fullName.includes("Machibroda")) || players.find(p => p.fullName.includes("Jaco")) || players[0];
      selectPlayer(found.playerId);
    }}

    function onTeamFilterChange() {{
      currentTeam = document.getElementById('team-filter').value;
      const filtered = getFilteredPlayersList();
      if (filtered.length > 0) {{
        const stillInList = filtered.some(p => p.playerId === currentPlayerId);
        if (!stillInList) {{
          selectPlayer(filtered[0].playerId);
        }}
      }}
      filterPlayerDropdown();
    }}

    function setCohort(cohort) {{
      currentCohort = cohort;
      ['all', 'qualified', 'ops-leaders'].forEach(c => {{
        const btn = document.getElementById(`pill-${{c}}`);
        btn.className = "flex-1 py-1.5 px-2 rounded-md text-xs font-medium transition-colors text-slate-400 hover:text-white text-center";
      }});
      if (cohort === 'ALL') {{
        document.getElementById('pill-all').className = "flex-1 py-1.5 px-2 rounded-md text-xs font-medium transition-colors bg-blue-600 text-white shadow-sm text-center";
      }} else if (cohort === 'QUALIFIED') {{
        document.getElementById('pill-qualified').className = "flex-1 py-1.5 px-2 rounded-md text-xs font-medium transition-colors bg-blue-600 text-white shadow-sm text-center";
      }} else if (cohort === 'OPS_LEADERS') {{
        document.getElementById('pill-ops-leaders').className = "flex-1 py-1.5 px-2 rounded-md text-xs font-medium transition-colors bg-blue-600 text-white shadow-sm text-center";
      }}
      
      const filtered = getFilteredPlayersList();
      if (filtered.length > 0) {{
        const stillInList = filtered.some(p => p.playerId === currentPlayerId);
        if (!stillInList) {{
          selectPlayer(filtered[0].playerId);
        }}
      }}
      filterPlayerDropdown();
    }}

    function getFilteredPlayersList() {{
      let list = Object.values(RAW_DATA.players);

      if (currentTeam !== 'ALL') {{
        list = list.filter(p => p.teamName === currentTeam);
      }}

      if (currentCohort === 'QUALIFIED') {{
        list = list.filter(p => (p.officialStats.plateAppearances || 0) >= 80);
      }} else if (currentCohort === 'OPS_LEADERS') {{
        list = list.filter(p => (p.officialStats.ops || 0) >= 0.850);
      }}

      list.sort((a, b) => (b.officialStats.ops || 0) - (a.officialStats.ops || 0));
      return list;
    }}

    function openPlayerSearch() {{
      filterPlayerDropdown();
      document.getElementById('player-dropdown').classList.remove('hidden');
    }}

    function clearPlayerSearch() {{
      const input = document.getElementById('player-search-input');
      input.value = '';
      document.getElementById('clear-search-btn').classList.add('hidden');
      filterPlayerDropdown();
      input.focus();
    }}

    document.addEventListener('click', (e) => {{
      const wrap = document.getElementById('player-search-input');
      const drop = document.getElementById('player-dropdown');
      if (wrap && drop && !wrap.contains(e.target) && !drop.contains(e.target)) {{
        drop.classList.add('hidden');
      }}
    }});

    function filterPlayerDropdown() {{
      const query = (document.getElementById('player-search-input').value || '').trim().toLowerCase();
      const clearBtn = document.getElementById('clear-search-btn');
      if (query.length > 0) {{
        clearBtn.classList.remove('hidden');
      }} else {{
        clearBtn.classList.add('hidden');
      }}

      const dropdown = document.getElementById('player-dropdown');
      dropdown.innerHTML = '';

      let list = getFilteredPlayersList();
      if (query.length > 0) {{
        list = list.filter(p => 
          p.fullName.toLowerCase().includes(query) ||
          p.teamName.toLowerCase().includes(query) ||
          p.position.toLowerCase().includes(query)
        );
      }}

      if (list.length === 0) {{
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'p-4 text-center text-xs text-slate-400';
        emptyDiv.innerText = 'No hitters matching criteria';
        dropdown.appendChild(emptyDiv);
      }} else {{
        list.slice(0, 30).forEach(p => {{
          const item = document.createElement('div');
          item.className = `p-2.5 px-3.5 hover:bg-blue-600/20 cursor-pointer flex items-center justify-between transition-colors ${{p.playerId === currentPlayerId ? 'bg-blue-600/15 border-l-2 border-blue-500' : ''}}`;
          item.onclick = () => {{
            selectPlayer(p.playerId);
            dropdown.classList.add('hidden');
          }};

          item.innerHTML = `
            <div class="flex items-center gap-2.5 truncate">
              <span class="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-bold text-blue-400">
                ${{p.position || 'UTIL'}}
              </span>
              <div class="truncate">
                <div class="text-sm font-semibold text-white truncate">${{p.fullName}}</div>
                <div class="text-[11px] text-slate-400 truncate">${{p.teamName}} • ${{p.officialStats.games || p.gamesPlayedCount}} G</div>
              </div>
            </div>
            <div class="text-right flex-shrink-0 font-mono text-xs">
              <div class="text-amber-400 font-bold">${{p.officialStats.ops ? p.officialStats.ops.toFixed(3) : '.000'}} <span class="text-[10px] text-slate-500 font-sans font-normal">OPS</span></div>
              <div class="text-slate-400">${{p.officialStats.battingAvg ? p.officialStats.battingAvg.toFixed(3) : '.000'}} <span class="text-[10px] text-slate-500 font-sans font-normal">AVG</span></div>
            </div>
          `;
          dropdown.appendChild(item);
        }});
      }}
      dropdown.classList.remove('hidden');
    }}

    function selectPlayer(playerId) {{
      currentPlayerId = playerId;
      const player = RAW_DATA.players[playerId];
      if (!player) return;

      document.getElementById('player-search-input').value = player.fullName;

      // Update Game Range Limits
      const totalG = Math.max(1, (player.timeline || []).length);
      maxPlayerGames = totalG;
      rangeStart = 1;
      rangeEnd = totalG;
      syncRangeUI();

      // Render Player Spotlight
      renderPlayerSpotlight(player);

      // Render Chart
      renderChart(player);

      // Render Game Log Table
      renderGameLogTable();
    }}

    function pickRandomPlayer() {{
      const list = getFilteredPlayersList();
      if (list.length > 0) {{
        const rand = list[Math.floor(Math.random() * list.length)];
        selectPlayer(rand.playerId);
      }}
    }}

    function handleHeadshotError(img) {{
      img.onerror = null;
      img.src = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="%2364748b"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/></svg>';
    }}

    function renderPlayerSpotlight(player) {{
      const st = player.officialStats;
      const timeline = player.timeline || [];

      document.getElementById('player-name').innerText = player.fullName;
      document.getElementById('player-team-name').innerText = player.teamName;
      document.getElementById('player-pos-badge').innerText = player.position || 'UTIL';
      document.getElementById('player-games-badge').innerText = `${{st.games || timeline.length}} Games Played`;

      document.getElementById('player-pa').innerText = st.plateAppearances || '-';
      document.getElementById('player-ab').innerText = st.atBats;
      document.getElementById('player-h').innerText = st.hits;
      document.getElementById('player-hr').innerText = st.homeRuns;
      document.getElementById('player-rbi').innerText = st.rbi;

      // 4 Main Stats
      document.getElementById('stat-avg').innerText = st.battingAvg !== undefined ? st.battingAvg.toFixed(3) : '.000';
      document.getElementById('stat-obp').innerText = st.obp !== undefined ? st.obp.toFixed(3) : '.000';
      document.getElementById('stat-slg').innerText = st.slg !== undefined ? st.slg.toFixed(3) : '.000';
      document.getElementById('stat-ops').innerText = st.ops !== undefined ? st.ops.toFixed(3) : '.000';

      // Secondary details
      document.getElementById('sub-2b').innerText = st.doubles;
      document.getElementById('sub-3b').innerText = st.triples;
      document.getElementById('sub-bb').innerText = st.walks;
      document.getElementById('sub-so').innerText = st.strikeouts;
      document.getElementById('sub-r').innerText = st.runs;

      // Images
      const headshot = document.getElementById('player-headshot');
      headshot.src = player.headshotUrl || '';
      if (!player.headshotUrl) {{
        handleHeadshotError(headshot);
      }}

      const teamLogo = document.getElementById('player-team-logo');
      teamLogo.src = player.teamLogoUrl || '';
      if (!player.teamLogoUrl) {{
        teamLogo.style.display = 'none';
      }} else {{
        teamLogo.style.display = 'block';
      }}

      // Calculate Peak and Low OPS in timeline
      if (timeline.length > 0) {{
        let peak = timeline[0];
        let low = timeline[0];
        timeline.forEach(g => {{
          if (g.cumOps > peak.cumOps) peak = g;
          if (g.cumOps < low.cumOps) low = g;
        }});
        document.getElementById('peak-ops-val').innerText = peak.cumOps.toFixed(3);
        document.getElementById('peak-ops-date').innerText = `(${'{'}peak.gameDate{'}'} vs ${'{'}peak.opponentShort{'}'})`;
        document.getElementById('low-ops-val').innerText = low.cumOps.toFixed(3);
        document.getElementById('low-ops-date').innerText = `(${'{'}low.gameDate{'}'} vs ${'{'}low.opponentShort{'}'})`;
      }} else {{
        document.getElementById('peak-ops-val').innerText = '-';
        document.getElementById('peak-ops-date').innerText = '';
        document.getElementById('low-ops-val').innerText = '-';
        document.getElementById('low-ops-date').innerText = '';
      }}
    }}

    // ==========================================
    // RANGE FILTERING & PRESETS
    // ==========================================
    function syncRangeUI() {{
      const startInp = document.getElementById('range-start-input');
      const endInp = document.getElementById('range-end-input');
      const startSlider = document.getElementById('range-slider-start');
      const endSlider = document.getElementById('range-slider-end');

      startInp.min = 1;
      startInp.max = maxPlayerGames;
      startInp.value = rangeStart;

      endInp.min = 1;
      endInp.max = maxPlayerGames;
      endInp.value = rangeEnd;

      startSlider.min = 1;
      startSlider.max = maxPlayerGames;
      startSlider.value = rangeStart;

      endSlider.min = 1;
      endSlider.max = maxPlayerGames;
      endSlider.value = rangeEnd;

      document.getElementById('slider-start-val').innerText = rangeStart;
      document.getElementById('slider-end-val').innerText = rangeEnd;

      const pill = document.getElementById('range-count-pill');
      const count = rangeEnd - rangeStart + 1;
      if (rangeStart === 1 && rangeEnd === maxPlayerGames) {{
        pill.innerText = `All ${'{'}maxPlayerGames{'}'} Games`;
        pill.className = "px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20";
        document.getElementById('window-summary-bar').classList.add('hidden');
      }} else {{
        pill.innerText = `Games ${'{'}rangeStart{'}'}–${'{'}rangeEnd{'}'} (${'{'}count{'}'} Games)`;
        pill.className = "px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20";
        document.getElementById('window-summary-bar').classList.remove('hidden');
      }}
    }}

    function onRangeInputChange() {{
      let s = parseInt(document.getElementById('range-start-input').value) || 1;
      let e = parseInt(document.getElementById('range-end-input').value) || maxPlayerGames;

      s = Math.max(1, Math.min(s, maxPlayerGames));
      e = Math.max(1, Math.min(e, maxPlayerGames));

      if (s > e) {{
        s = e;
      }}

      rangeStart = s;
      rangeEnd = e;
      syncRangeUI();
      triggerRangeUpdate();
    }}

    function onSliderStartInput() {{
      let s = parseInt(document.getElementById('range-slider-start').value) || 1;
      if (s > rangeEnd) {{
        rangeEnd = s;
      }}
      rangeStart = s;
      syncRangeUI();
      triggerRangeUpdate();
    }}

    function onSliderEndInput() {{
      let e = parseInt(document.getElementById('range-slider-end').value) || maxPlayerGames;
      if (e < rangeStart) {{
        rangeStart = e;
      }}
      rangeEnd = e;
      syncRangeUI();
      triggerRangeUpdate();
    }}

    function setRangePreset(preset) {{
      if (preset === 'all') {{
        rangeStart = 1;
        rangeEnd = maxPlayerGames;
      }} else if (preset === 'last5') {{
        rangeStart = Math.max(1, maxPlayerGames - 4);
        rangeEnd = maxPlayerGames;
      }} else if (preset === 'last10') {{
        rangeStart = Math.max(1, maxPlayerGames - 9);
        rangeEnd = maxPlayerGames;
      }} else if (preset === 'last20') {{
        rangeStart = Math.max(1, maxPlayerGames - 19);
        rangeEnd = maxPlayerGames;
      }} else if (preset === 'firstHalf') {{
        rangeStart = 1;
        rangeEnd = Math.max(1, Math.floor(maxPlayerGames / 2));
      }} else if (preset === 'secondHalf') {{
        rangeStart = Math.max(1, Math.floor(maxPlayerGames / 2) + 1);
        rangeEnd = maxPlayerGames;
      }}
      syncRangeUI();
      triggerRangeUpdate();
    }}

    function triggerRangeUpdate() {{
      if (currentPlayerId && RAW_DATA.players[currentPlayerId]) {{
        const player = RAW_DATA.players[currentPlayerId];
        renderChart(player);
        renderGameLogTable();
      }}
    }}

    // ==========================================
    // Y-AXIS SCALE MODE (AUTOFIT SLIDING VS FIXED)
    // ==========================================
    function setScaleMode(mode) {{
      scaleMode = mode;
      const btnFit = document.getElementById('btn-scale-autofit');
      const btnFix = document.getElementById('btn-scale-fixed');

      if (mode === 'autofit') {{
        btnFit.className = "px-2.5 py-1.5 rounded-md font-semibold transition-all bg-emerald-600 text-white shadow-sm flex items-center gap-1.5";
        btnFix.className = "px-2.5 py-1.5 rounded-md font-semibold transition-all text-slate-400 hover:text-white flex items-center gap-1.5";
      }} else {{
        btnFix.className = "px-2.5 py-1.5 rounded-md font-semibold transition-all bg-emerald-600 text-white shadow-sm flex items-center gap-1.5";
        btnFit.className = "px-2.5 py-1.5 rounded-md font-semibold transition-all text-slate-400 hover:text-white flex items-center gap-1.5";
      }}

      if (currentPlayerId && RAW_DATA.players[currentPlayerId]) {{
        renderChart(RAW_DATA.players[currentPlayerId]);
      }}
    }}

    function setChartMode(mode) {{
      chartMode = mode;
      const btnCum = document.getElementById('btn-mode-cum');
      const btnRoll = document.getElementById('btn-mode-roll');
      if (mode === 'cumulative') {{
        btnCum.className = "px-3 py-1.5 rounded-md font-semibold transition-all bg-blue-600 text-white shadow-sm";
        btnRoll.className = "px-3 py-1.5 rounded-md font-semibold transition-all text-slate-400 hover:text-white";
        document.getElementById('chart-main-title').innerText = "Season Progression Trajectory (Cumulative)";
        document.getElementById('chart-subtitle').innerText = "Running cumulative slash line across the selected game window.";
      }} else {{
        btnRoll.className = "px-3 py-1.5 rounded-md font-semibold transition-all bg-blue-600 text-white shadow-sm";
        btnCum.className = "px-3 py-1.5 rounded-md font-semibold transition-all text-slate-400 hover:text-white";
        document.getElementById('chart-main-title').innerText = "5-Game Rolling Trend (Hot / Cold Streaks)";
        document.getElementById('chart-subtitle').innerText = "Rolling 5-game window performance across the selected game window.";
      }}
      if (currentPlayerId) {{
        renderChart(RAW_DATA.players[currentPlayerId]);
      }}
    }}

    function toggleMetric(metric) {{
      activeMetrics[metric] = !activeMetrics[metric];
      updateMetricChips();
      if (currentPlayerId && RAW_DATA.players[currentPlayerId]) {{
        // Re-render chart to dynamically adjust sliding Y-axis scale based on remaining visible metrics
        renderChart(RAW_DATA.players[currentPlayerId]);
      }}
    }}

    function showAllMetrics() {{
      activeMetrics.avg = true;
      activeMetrics.obp = true;
      activeMetrics.slg = true;
      activeMetrics.ops = true;
      updateMetricChips();
      if (currentPlayerId && RAW_DATA.players[currentPlayerId]) {{
        renderChart(RAW_DATA.players[currentPlayerId]);
      }}
    }}

    function updateMetricChips() {{
      ['avg', 'obp', 'slg', 'ops'].forEach(m => {{
        const chip = document.getElementById(`chip-${{m}}`);
        if (activeMetrics[m]) {{
          chip.classList.remove('inactive');
          chip.classList.add('active');
        }} else {{
          chip.classList.remove('active');
          chip.classList.add('inactive');
        }}
      }});
    }}

    // ==========================================
    // CHART RENDERING (DYNAMIC SLIDING Y-AXIS)
    // ==========================================
    function renderChart(player) {{
      const fullTimeline = player.timeline || [];
      const ctx = document.getElementById('progressionChart').getContext('2d');

      if (chartInstance) {{
        chartInstance.destroy();
      }}

      // Slice timeline to selected game range
      const visibleTimeline = fullTimeline.filter(g => g.gameIndex >= rangeStart && g.gameIndex <= rangeEnd);

      // Compute In-Window isolated performance split
      computeWindowSummary(visibleTimeline);

      const labels = visibleTimeline.map(g => `G${{g.gameIndex}} (${{g.gameDate.slice(5)}})`);
      const isCum = (chartMode === 'cumulative');

      const avgData = visibleTimeline.map(g => isCum ? g.cumAvg : g.roll5Avg);
      const obpData = visibleTimeline.map(g => isCum ? g.cumObp : g.roll5Obp);
      const slgData = visibleTimeline.map(g => isCum ? g.cumSlg : g.roll5Slg);
      const opsData = visibleTimeline.map(g => isCum ? g.cumOps : g.roll5Ops);

      // Datasets - All mapped to the unified 'y' scale so OPS is always in true visual alignment (above OBP and SLG)
      const datasets = [
        {{
          metricKey: 'avg',
          label: isCum ? 'Cumulative AVG' : '5G Rolling AVG',
          data: avgData,
          borderColor: '#10b981', // emerald
          backgroundColor: '#10b981',
          borderWidth: 2.5,
          tension: 0.25,
          pointRadius: visibleTimeline.length > 25 ? 2.5 : 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#10b981',
          pointBorderColor: '#0b1120',
          pointBorderWidth: 2,
          yAxisID: 'y',
          hidden: !activeMetrics.avg
        }},
        {{
          metricKey: 'obp',
          label: isCum ? 'Cumulative OBP' : '5G Rolling OBP',
          data: obpData,
          borderColor: '#0ea5e9', // sky blue
          backgroundColor: '#0ea5e9',
          borderWidth: 2.5,
          tension: 0.25,
          pointRadius: visibleTimeline.length > 25 ? 2.5 : 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#0ea5e9',
          pointBorderColor: '#0b1120',
          pointBorderWidth: 2,
          yAxisID: 'y',
          hidden: !activeMetrics.obp
        }},
        {{
          metricKey: 'slg',
          label: isCum ? 'Cumulative SLG' : '5G Rolling SLG',
          data: slgData,
          borderColor: '#a855f7', // purple
          backgroundColor: '#a855f7',
          borderWidth: 2.5,
          tension: 0.25,
          pointRadius: visibleTimeline.length > 25 ? 2.5 : 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#a855f7',
          pointBorderColor: '#0b1120',
          pointBorderWidth: 2,
          yAxisID: 'y',
          hidden: !activeMetrics.slg
        }},
        {{
          metricKey: 'ops',
          label: isCum ? 'Cumulative OPS' : '5G Rolling OPS',
          data: opsData,
          borderColor: '#f59e0b', // amber
          backgroundColor: '#f59e0b',
          borderWidth: 3,
          borderDash: isCum ? [] : [4, 2],
          tension: 0.25,
          pointRadius: visibleTimeline.length > 25 ? 3 : 4.5,
          pointHoverRadius: 7.5,
          pointBackgroundColor: '#f59e0b',
          pointBorderColor: '#0b1120',
          pointBorderWidth: 2,
          yAxisID: 'y',
          hidden: !activeMetrics.ops
        }}
      ];

      // ==========================================
      // UNIFIED SLIDING Y-AXIS DYNAMIC SCALE
      // ==========================================
      // Gather visible values from active metrics
      const visibleValues = [];
      if (activeMetrics.avg) visibleValues.push(...avgData);
      if (activeMetrics.obp) visibleValues.push(...obpData);
      if (activeMetrics.slg) visibleValues.push(...slgData);
      if (activeMetrics.ops) visibleValues.push(...opsData);

      let yMin = 0.000;
      let yMax = 1.000;

      if (visibleValues.length > 0) {{
        const minVal = Math.min(...visibleValues);
        const maxVal = Math.max(...visibleValues);

        if (scaleMode === 'autofit') {{
          let span = maxVal - minVal;
          if (span < 0.04) span = 0.06;
          const pad = Math.max(0.015, span * 0.10);

          // Round min down to nearest .010, max up to nearest .010
          yMin = Math.max(0, Math.floor((minVal - pad) * 100) / 100);
          yMax = Math.ceil((maxVal + pad) * 100) / 100;

          if (yMin >= yMax) {{
            yMin = Math.max(0, yMin - 0.05);
            yMax = yMax + 0.05;
          }}
        }} else {{
          // Fixed 0-baseline scale
          yMin = 0.000;
          yMax = Math.max(1.000, Math.ceil((maxVal + 0.05) * 10) / 10);
        }}
      }}

      // Update indicator text in footer
      const scaleInd = document.getElementById('axis-scale-indicator');
      if (scaleMode === 'autofit') {{
        scaleInd.innerText = `Sliding Axis: [${{yMin.toFixed(3)}} – ${{yMax.toFixed(3)}}]`;
        scaleInd.className = "font-mono text-[11px] text-emerald-400 bg-emerald-950/40 px-2.5 py-0.5 rounded border border-emerald-500/30";
      }} else {{
        scaleInd.innerText = `Fixed 0-Baseline: [0.000 – ${{yMax.toFixed(3)}}]`;
        scaleInd.className = "font-mono text-[11px] text-slate-400 bg-[#0b1120] px-2.5 py-0.5 rounded border border-[#1e293b]";
      }}

      chartInstance = new Chart(ctx, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: datasets
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{
            mode: 'index',
            intersect: false
          }},
          plugins: {{
            legend: {{
              display: false
            }},
            tooltip: {{
              backgroundColor: '#0f172a',
              titleColor: '#f8fafc',
              bodyColor: '#cbd5e1',
              borderColor: '#334155',
              borderWidth: 1,
              padding: 12,
              boxPadding: 4,
              usePointStyle: true,
              callbacks: {{
                title: function(items) {{
                  const idx = items[0].dataIndex;
                  const g = visibleTimeline[idx];
                  return `Game #${{g.gameIndex}} • ${{g.gameDate}} (${{g.result}})`;
                }},
                beforeBody: function(items) {{
                  const idx = items[0].dataIndex;
                  const g = visibleTimeline[idx];
                  return [
                    `Matchup: ${{g.opponent}}`,
                    `Game Line: ${{g.statSummary}} (${{g.gameH}}-for-${{g.gameAb}})`
                  ];
                }},
                label: function(item) {{
                  const val = item.raw !== undefined && item.raw !== null ? item.raw.toFixed(3) : '.000';
                  return ` ${{item.dataset.label}}: ${{val}}`;
                }}
              }}
            }}
          }},
          scales: {{
            x: {{
              grid: {{
                color: '#1e293b',
                drawBorder: false
              }},
              ticks: {{
                color: '#64748b',
                maxRotation: 45,
                autoSkip: true,
                maxTicksLimit: 15,
                font: {{
                  size: 11
                }}
              }}
            }},
            y: {{
              type: 'linear',
              position: 'left',
              min: yMin,
              max: yMax,
              grid: {{
                color: '#1e293b',
                drawBorder: false
              }},
              ticks: {{
                color: '#94a3b8',
                callback: function(val) {{
                  return val.toFixed(3);
                }},
                font: {{
                  family: 'monospace',
                  size: 11
                }}
              }}
            }}
          }},
          onClick: (evt, elements) => {{
            if (elements.length > 0) {{
              const index = elements[0].index;
              const targetGame = visibleTimeline[index];
              if (targetGame) {{
                highlightTableRow(targetGame.gameIndex - 1);
              }}
            }}
          }}
        }}
      }});
    }}

    function computeWindowSummary(visibleTimeline) {{
      const summaryBar = document.getElementById('window-summary-bar');
      if (rangeStart === 1 && rangeEnd === maxPlayerGames) {{
        summaryBar.classList.add('hidden');
        return;
      }}
      summaryBar.classList.remove('hidden');

      let wAb = 0, wR = 0, wH = 0, w2b = 0, w3b = 0, wHr = 0, wRbi = 0, wBb = 0, wSo = 0, wHbp = 0, wSf = 0, wTb = 0;
      visibleTimeline.forEach(g => {{
        wAb += g.gameAb;
        wR += g.gameR;
        wH += g.gameH;
        w2b += g.game2b;
        w3b += g.game3b;
        wHr += g.gameHr;
        wRbi += g.gameRbi;
        wBb += g.gameBb;
        wSo += g.gameSo;
        wHbp += (g.hbp || 0);
        wSf += (g.sf || 0);
        const tb = (g.gameH - g.game2b - g.game3b - g.gameHr) + 2*g.game2b + 3*g.game3b + 4*g.gameHr;
        wTb += tb;
      }});

      const wAvg = wAb > 0 ? (wH / wAb) : 0;
      const obpDenom = (wAb + wBb + wHbp + wSf);
      const wObp = obpDenom > 0 ? ((wH + wBb + wHbp) / obpDenom) : 0;
      const wSlg = wAb > 0 ? (wTb / wAb) : 0;
      const wOps = wObp + wSlg;

      document.getElementById('window-slash-line').innerText = `${{wAvg.toFixed(3)}} AVG | ${{wObp.toFixed(3)}} OBP | ${{wSlg.toFixed(3)}} SLG | ${{wOps.toFixed(3)}} OPS`;
      document.getElementById('window-counting-stats').innerText = `(${'{'}wH{'}'}-for-${'{'}wAb{'}'}, ${'{'}wHr{'}'} HR, ${'{'}wRbi{'}'} RBI, ${'{'}wBb{'}'} BB, ${'{'}wR{'}'} R across ${'{'}visibleTimeline.length{'}'} games)`;
    }}

    // ==========================================
    // GAME LOG TABLE (FILTERED TO WINDOW)
    // ==========================================
    function renderGameLogTable() {{
      const player = RAW_DATA.players[currentPlayerId];
      if (!player) return;

      const fullTimeline = player.timeline || [];
      const visibleTimeline = fullTimeline.filter(g => g.gameIndex >= rangeStart && g.gameIndex <= rangeEnd);

      const countBadge = document.getElementById('gamelog-count-badge');
      if (rangeStart === 1 && rangeEnd === maxPlayerGames) {{
        countBadge.innerText = `${{fullTimeline.length}} Games`;
      }} else {{
        countBadge.innerText = `${{visibleTimeline.length}} Games (G${{rangeStart}} – G${{rangeEnd}})`;
      }}

      const tbody = document.getElementById('gamelog-tbody');
      tbody.innerHTML = '';

      const sortOrder = document.getElementById('log-sort').value;
      const displayList = sortOrder === 'reverse' ? [...visibleTimeline].reverse() : [...visibleTimeline];

      displayList.forEach(g => {{
        const tr = document.createElement('tr');
        tr.id = `row-game-${{g.gameIndex - 1}}`;
        tr.className = "log-row transition-colors";
        tr.onclick = () => {{
          highlightChartPoint(g.gameIndex);
        }};

        const isWin = g.result.startsWith('W');
        const resClass = isWin ? 'text-emerald-400 font-semibold' : 'text-slate-400';

        const isMultiHit = g.gameH >= 2;
        const hasHr = g.gameHr > 0;
        let hClass = isMultiHit ? 'text-emerald-400 font-bold' : (g.gameH > 0 ? 'text-slate-200' : 'text-slate-500');

        tr.innerHTML = `
          <td class="py-2.5 px-3 text-center font-mono text-slate-500">${{g.gameIndex}}</td>
          <td class="py-2.5 px-3 text-slate-300 font-medium">${{g.gameDate}}</td>
          <td class="py-2.5 px-3 text-slate-200 truncate max-w-[160px]">${{g.opponent}}</td>
          <td class="py-2.5 px-3 text-center ${{resClass}} font-mono">${{g.result}}</td>
          <td class="py-2.5 px-2 text-center text-slate-300">${{g.gameAb}}</td>
          <td class="py-2.5 px-2 text-center text-slate-300">${{g.gameR}}</td>
          <td class="py-2.5 px-2 text-center ${{hClass}}">${{g.gameH}}</td>
          <td class="py-2.5 px-2 text-center text-slate-400">${{g.game2b || '-'}}</td>
          <td class="py-2.5 px-2 text-center text-slate-400">${{g.game3b || '-'}}</td>
          <td class="py-2.5 px-2 text-center ${{hasHr ? 'text-amber-400 font-bold' : 'text-slate-400'}}">${{g.gameHr || '-'}}</td>
          <td class="py-2.5 px-2 text-center text-slate-300">${{g.gameRbi}}</td>
          <td class="py-2.5 px-2 text-center text-slate-400">${{g.gameBb || '-'}}</td>
          <td class="py-2.5 px-2 text-center text-slate-500">${{g.gameSo}}</td>
          <td class="py-2.5 px-3 text-slate-300 truncate max-w-[160px]">${{g.statSummary}}</td>
          <td class="py-2.5 px-3 text-right font-mono text-emerald-400 font-bold">${{g.cumAvg.toFixed(3)}}</td>
          <td class="py-2.5 px-3 text-right font-mono text-sky-400">${{g.cumObp.toFixed(3)}}</td>
          <td class="py-2.5 px-3 text-right font-mono text-purple-400">${{g.cumSlg.toFixed(3)}}</td>
          <td class="py-2.5 px-3 text-right font-mono text-amber-400 font-bold">${{g.cumOps.toFixed(3)}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function highlightTableRow(gameIndex0) {{
      document.querySelectorAll('.log-row').forEach(r => r.classList.remove('highlighted'));
      const row = document.getElementById(`row-game-${{gameIndex0}}`);
      if (row) {{
        row.classList.add('highlighted');
        row.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
    }}

    function highlightChartPoint(gameIndex1) {{
      highlightTableRow(gameIndex1 - 1);
      if (chartInstance && chartInstance.data && chartInstance.data.labels) {{
        const labelTarget = `G${{gameIndex1}} `;
        const chartIdx = chartInstance.data.labels.findIndex(l => l.startsWith(labelTarget));
        if (chartIdx !== -1) {{
          chartInstance.setActiveElements([
            {{ datasetIndex: 0, index: chartIdx }},
            {{ datasetIndex: 1, index: chartIdx }},
            {{ datasetIndex: 2, index: chartIdx }},
            {{ datasetIndex: 3, index: chartIdx }}
          ]);
          chartInstance.tooltip.setActiveElements([
            {{ datasetIndex: 0, index: chartIdx }}
          ]);
          chartInstance.update();
        }}
      }}
    }}

    function exportCurrentPlayerCsv() {{
      const player = RAW_DATA.players[currentPlayerId];
      if (!player || !player.timeline || player.timeline.length === 0) return;

      const visibleTimeline = player.timeline.filter(g => g.gameIndex >= rangeStart && g.gameIndex <= rangeEnd);

      const headers = ["Game#", "Date", "Opponent", "Result", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "Summary", "Cum_AVG", "Cum_OBP", "Cum_SLG", "Cum_OPS"];
      const rows = visibleTimeline.map(g => [
        g.gameIndex,
        g.gameDate,
        `"${{g.opponent}}"`,
        `"${{g.result}}"`,
        g.gameAb,
        g.gameR,
        g.gameH,
        g.game2b,
        g.game3b,
        g.gameHr,
        g.gameRbi,
        g.gameBb,
        g.gameSo,
        `"${{g.statSummary}}"`,
        g.cumAvg.toFixed(3),
        g.cumObp.toFixed(3),
        g.cumSlg.toFixed(3),
        g.cumOps.toFixed(3)
      ]);

      const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\\n");
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      const rangeSuffix = (rangeStart === 1 && rangeEnd === maxPlayerGames) ? 'full_season' : `games_${{rangeStart}}_to_${{rangeEnd}}`;
      link.setAttribute("download", `${{player.fullName.replace(/\\s+/g, '_')}}_2026_${{rangeSuffix}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}
  </script>
</body>
</html>
"""

    out_file = 'cbl_2026_player_progression_interactive.html'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Also sync index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Successfully generated {out_file} and index.html (size: {os.path.getsize(out_file) / 1024:.1f} KB)")

if __name__ == '__main__':
    generate_interactive_html()
