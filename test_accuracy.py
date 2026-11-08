import json
import glob
from collections import defaultdict

with open('cbl_2026_batting_official.json', 'r', encoding='utf-8') as f:
    official = json.load(f)
off_by_id = {p['playerId']: p for p in official}

files = glob.glob('../Run Matrix/data/games/*.json')

games_data = []
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        try:
            d = json.load(fp)
            if not isinstance(d, dict): continue
            # check if regular season
            if d.get('eventType') == 'playoff_game' or d.get('playoffBranding'):
                continue
            games_data.append(d)
        except Exception as e:
            pass

print(f'Total regular season games found: {len(games_data)}')

player_totals = defaultdict(lambda: {'ab': 0, 'h': 0, '2b': 0, '3b': 0, 'hr': 0, 'bb': 0, 'hbp': 0, 'sf': 0, 'sh': 0, 'rbi': 0, 'r': 0, 'games': 0})

for g in games_data:
    live = g.get('snapshot', {}).get('liveGame', {})
    ats = live.get('atBats', [])
    game_players = set()
    runs_scored_in_game = defaultdict(int)
    for a in ats:
        for r_id in a.get('runsScored', []):
            runs_scored_in_game[r_id] += 1
            
    for a in ats:
        b_id = a.get('batterId')
        if not b_id: continue
        game_players.add(b_id)
        out = a.get('outcome')
        rbi = a.get('rbiCount', 0)
        player_totals[b_id]['rbi'] += rbi
        
        if out in ['single']:
            player_totals[b_id]['h'] += 1
            player_totals[b_id]['ab'] += 1
        elif out in ['double', 'ground_rule_double']:
            player_totals[b_id]['h'] += 1
            player_totals[b_id]['2b'] += 1
            player_totals[b_id]['ab'] += 1
        elif out in ['triple']:
            player_totals[b_id]['h'] += 1
            player_totals[b_id]['3b'] += 1
            player_totals[b_id]['ab'] += 1
        elif out in ['home_run']:
            player_totals[b_id]['h'] += 1
            player_totals[b_id]['hr'] += 1
            player_totals[b_id]['ab'] += 1
        elif out in ['walk', 'intentional_walk']:
            player_totals[b_id]['bb'] += 1
        elif out in ['hit_by_pitch']:
            player_totals[b_id]['hbp'] += 1
        elif out in ['sacrifice_fly']:
            player_totals[b_id]['sf'] += 1
        elif out in ['sacrifice_bunt']:
            player_totals[b_id]['sh'] += 1
        elif out in ['catcher_interference']:
            pass
        else:
            player_totals[b_id]['ab'] += 1
            
    for p_id in game_players:
        player_totals[p_id]['games'] += 1
        player_totals[p_id]['r'] += runs_scored_in_game[p_id]

matched_perfect = 0
diffs = []
for p_id, p_off in off_by_id.items():
    p_calc = player_totals.get(p_id)
    if not p_calc:
        diffs.append((p_off['fullName'], 'No calculated games'))
        continue
    ab_match = (p_calc['ab'] == p_off['atBats'])
    h_match = (p_calc['h'] == p_off['hits'])
    hr_match = (p_calc['hr'] == p_off['homeRuns'])
    if ab_match and h_match and hr_match:
        matched_perfect += 1
    else:
        diffs.append((p_off['fullName'], f"Calc: AB={p_calc['ab']} H={p_calc['h']} HR={p_calc['hr']} | Off: AB={p_off['atBats']} H={p_off['hits']} HR={p_off['homeRuns']}"))

print(f"Matched perfectly on AB, H, HR: {matched_perfect} / {len(off_by_id)}")
if diffs:
    print(f"Sample diffs (first 10 of {len(diffs)}):")
    for name, d in diffs[:10]:
        print(f"  {name}: {d}")
