import json
import glob
import os
from collections import defaultdict

def build_player_progression():
    # 1. Load official stats for player metadata & leaderboards
    with open('cbl_2026_batting_official.json', 'r', encoding='utf-8') as f:
        official_stats = json.load(f)
    official_by_id = {p['playerId']: p for p in official_stats}

    # 2. Load game IDs metadata for chronological sorting and schedule numbers
    with open('../Run Matrix/data/game_ids.json', 'r', encoding='utf-8') as f:
        game_meta_list = json.load(f)
    meta_by_pub_id = {g.get('publicGameId'): g for g in game_meta_list}
    meta_by_game_id = {g.get('gameId'): g for g in game_meta_list if g.get('gameId')}

    # 3. Load all regular season game files
    files = glob.glob('../Run Matrix/data/games/*.json')
    games_list = []
    
    for f in files:
        fname = os.path.basename(f)
        if fname == 'toronto-at-chatham-2026-08-30.json': # Postponed
            continue
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                d = json.load(fp)
                if not isinstance(d, dict): continue
                # Skip playoffs
                if d.get('eventType') == 'playoff_game' or d.get('playoffBranding'):
                    continue
                games_list.append(d)
        except Exception:
            pass

    # Sort games chronologically by date and schedule number
    def game_sort_key(g):
        dt = g.get('game_date') or ''
        num = g.get('schedule_game_number') or 0
        try:
            num = int(num)
        except:
            num = 0
        return (dt, num)

    games_list.sort(key=game_sort_key)
    print(f"Loaded and sorted {len(games_list)} regular season games.")

    # 4. Also load Game 64 boxscore
    with open('game_64_boxscore.json', 'r', encoding='utf-8') as f:
        g64_box = json.load(f)

    # 5. Extract per-game player performances
    # player_id -> list of game log objects
    player_game_logs = defaultdict(list)

    # Map team names / abbreviations
    team_short_names = {
        'Barrie Baycats': 'Barrie',
        'Brantford Red Sox': 'Brantford',
        'Chatham-Kent Barnstormers': 'Chatham-Kent',
        'Guelph Royals': 'Guelph',
        'Hamilton Cardinals': 'Hamilton',
        'Kitchener Panthers': 'Kitchener',
        'London Majors': 'London',
        'Toronto Maple Leafs': 'Toronto',
        'Welland Jackfish': 'Welland'
    }

    # Process all regular games with atBats
    for g in games_list:
        pub_id = g.get('public_game_id')
        g_date = g.get('game_date')
        g_num = g.get('schedule_game_number')
        home_team = g.get('home_team')
        away_team = g.get('away_team')
        
        live = g.get('snapshot', {}).get('liveGame', {})
        ats = live.get('atBats', [])
        if not ats:
            # If this is game 64 (barrie at chatham), handled separately below
            continue

        home_score = live.get('homeScore', 0)
        away_score = live.get('awayScore', 0)

        # Runs scored by runners
        runs_scored_map = defaultdict(int)
        for a in ats:
            for r_id in a.get('runsScored', []):
                runs_scored_map[r_id] += 1

        # Group atBats by batter
        game_batters = defaultdict(lambda: {
            'ab': 0, 'r': 0, 'h': 0, '2b': 0, '3b': 0, 'hr': 0,
            'rbi': 0, 'bb': 0, 'so': 0, 'hbp': 0, 'sf': 0, 'sh': 0,
            'team': '', 'half': ''
        })

        for a in ats:
            b_id = a.get('batterId')
            if not b_id: continue
            out = a.get('outcome')
            rbi = a.get('rbiCount', 0)
            half = a.get('halfInning') # 'top' = away, 'bottom' = home

            entry = game_batters[b_id]
            entry['rbi'] += rbi
            entry['half'] = half
            entry['team'] = away_team if half == 'top' else home_team

            if out == 'single':
                entry['h'] += 1
                entry['ab'] += 1
            elif out in ['double', 'ground_rule_double']:
                entry['h'] += 1
                entry['2b'] += 1
                entry['ab'] += 1
            elif out == 'triple':
                entry['h'] += 1
                entry['3b'] += 1
                entry['ab'] += 1
            elif out == 'home_run':
                entry['h'] += 1
                entry['hr'] += 1
                entry['ab'] += 1
            elif out in ['walk', 'intentional_walk']:
                entry['bb'] += 1
            elif out == 'hit_by_pitch':
                entry['hbp'] += 1
            elif out == 'sacrifice_fly':
                entry['sf'] += 1
            elif out == 'sacrifice_bunt':
                entry['sh'] += 1
            elif out in ['strikeout_looking', 'strikeout_swinging', 'dropped_third_strike_out']:
                entry['so'] += 1
                entry['ab'] += 1
            elif out == 'catcher_interference':
                pass
            else:
                entry['ab'] += 1

        for b_id, s in game_batters.items():
            s['r'] = runs_scored_map[b_id]
            is_home = (s['half'] == 'bottom')
            opp_team = away_team if is_home else home_team
            opp_prefix = 'vs' if is_home else '@'
            
            my_score = home_score if is_home else away_score
            opp_score = away_score if is_home else home_score
            result_letter = 'W' if my_score > opp_score else ('L' if my_score < opp_score else 'T')
            game_result = f"{result_letter} {my_score}-{opp_score}"

            # Calculate game TB & PA
            tb = (s['h'] - s['2b'] - s['3b'] - s['hr']) + 2*s['2b'] + 3*s['3b'] + 4*s['hr']
            pa = s['ab'] + s['bb'] + s['hbp'] + s['sf'] + s['sh']

            log_entry = {
                'gameId': pub_id,
                'gameNumber': g_num,
                'date': g_date,
                'isHome': is_home,
                'opponent': f"{opp_prefix} {opp_team}",
                'opponentShort': f"{opp_prefix} {team_short_names.get(opp_team, opp_team)}",
                'result': game_result,
                'team': s['team'],
                'ab': s['ab'],
                'r': s['r'],
                'h': s['h'],
                '2b': s['2b'],
                '3b': s['3b'],
                'hr': s['hr'],
                'rbi': s['rbi'],
                'bb': s['bb'],
                'so': s['so'],
                'hbp': s['hbp'],
                'sf': s['sf'],
                'sh': s['sh'],
                'tb': tb,
                'pa': pa
            }
            player_game_logs[b_id].append(log_entry)

    # Add game 64 boxscore entries for Barrie and Chatham batters
    # Game 64 date: 2026-08-25, Barrie (away, 10) @ Chatham (home, 1)
    g64_meta = {
        'gameId': 'barrie-at-chatham-2026-08-25',
        'gameNumber': 64,
        'date': '2026-08-25',
    }
    for side, team_name, is_home, my_sc, opp_sc, opp_name in [
        ('away', 'Barrie Baycats', False, 10, 1, 'Chatham-Kent Barnstormers'),
        ('home', 'Chatham-Kent Barnstormers', True, 1, 10, 'Barrie Baycats')
    ]:
        for b in g64_box.get('boxScore', {}).get(side, {}).get('batting', []):
            b_id = b.get('canonicalPlayerId') or b.get('csvPlayerId')
            if not b_id: continue
            
            # Use boxscore stats
            ab = b.get('atBats', 0)
            r = b.get('runs', 0)
            h = b.get('hits', 0)
            rbi = b.get('rbi', 0)
            
            # Check if this player had HRs / extra bases recorded in difference with official
            off = official_by_id.get(b_id)
            # Current sum before game 64
            curr_hr = sum(x['hr'] for x in player_game_logs[b_id])
            curr_bb = sum(x['bb'] for x in player_game_logs[b_id])
            curr_2b = sum(x['2b'] for x in player_game_logs[b_id])
            curr_3b = sum(x['3b'] for x in player_game_logs[b_id])
            curr_hbp = sum(x['hbp'] for x in player_game_logs[b_id])
            curr_sf = sum(x['sf'] for x in player_game_logs[b_id])
            curr_sh = sum(x['sh'] for x in player_game_logs[b_id])
            curr_so = sum(x['so'] for x in player_game_logs[b_id])

            hr = max(0, off['homeRuns'] - curr_hr) if off else 0
            bb = max(0, off['walks'] - curr_bb) if off else 0
            d2 = max(0, off['doubles'] - curr_2b) if off else 0
            t3 = max(0, off['triples'] - curr_3b) if off else 0
            hbp = max(0, off['hitByPitch'] - curr_hbp) if off else 0
            sf = max(0, off['sacrificeFlies'] - curr_sf) if off else 0
            sh = max(0, off['sacrificeBunts'] - curr_sh) if off else 0
            so = max(0, off['strikeouts'] - curr_so) if off else 0

            # Ensure 1B + 2B + 3B + HR does not exceed H
            if d2 + t3 + hr > h:
                d2 = max(0, h - hr)

            tb = (h - d2 - t3 - hr) + 2*d2 + 3*t3 + 4*hr
            pa = ab + bb + hbp + sf + sh
            res_letter = 'W' if my_sc > opp_sc else 'L'

            opp_pref = 'vs' if is_home else '@'
            log_entry = {
                'gameId': g64_meta['gameId'],
                'gameNumber': g64_meta['gameNumber'],
                'date': g64_meta['date'],
                'isHome': is_home,
                'opponent': f"{opp_pref} {opp_name}",
                'opponentShort': f"{opp_pref} {team_short_names.get(opp_name, opp_name)}",
                'result': f"{res_letter} {my_sc}-{opp_sc}",
                'team': team_name,
                'ab': ab,
                'r': r,
                'h': h,
                '2b': d2,
                '3b': t3,
                'hr': hr,
                'rbi': rbi,
                'bb': bb,
                'so': so,
                'hbp': hbp,
                'sf': sf,
                'sh': sh,
                'tb': tb,
                'pa': pa
            }
            player_game_logs[b_id].append(log_entry)

    # Sort each player's game logs chronologically
    for b_id, logs in player_game_logs.items():
        logs.sort(key=lambda x: (x['date'], x['gameNumber']))

    # 6. Compute running cumulative stats & rolling windows for each player
    processed_players = {}

    for p in official_stats:
        b_id = p['playerId']
        logs = player_game_logs.get(b_id, [])

        cum_ab = 0
        cum_r = 0
        cum_h = 0
        cum_2b = 0
        cum_3b = 0
        cum_hr = 0
        cum_rbi = 0
        cum_bb = 0
        cum_so = 0
        cum_hbp = 0
        cum_sf = 0
        cum_sh = 0
        cum_tb = 0
        cum_pa = 0

        timeline = []
        for idx, g in enumerate(logs, start=1):
            cum_ab += g['ab']
            cum_r += g['r']
            cum_h += g['h']
            cum_2b += g['2b']
            cum_3b += g['3b']
            cum_hr += g['hr']
            cum_rbi += g['rbi']
            cum_bb += g['bb']
            cum_so += g['so']
            cum_hbp += g['hbp']
            cum_sf += g['sf']
            cum_sh += g['sh']
            cum_tb += g['tb']
            cum_pa += g['pa']

            # Cumulative metrics
            avg = round(cum_h / cum_ab, 3) if cum_ab > 0 else 0.000
            obp_denom = (cum_ab + cum_bb + cum_hbp + cum_sf)
            obp = round((cum_h + cum_bb + cum_hbp) / obp_denom, 3) if obp_denom > 0 else 0.000
            slg = round(cum_tb / cum_ab, 3) if cum_ab > 0 else 0.000
            ops = round(obp + slg, 3)

            # Rolling 5-game window
            start_5 = max(0, idx - 5)
            w5_logs = logs[start_5:idx]
            w5_ab = sum(x['ab'] for x in w5_logs)
            w5_h = sum(x['h'] for x in w5_logs)
            w5_bb = sum(x['bb'] for x in w5_logs)
            w5_hbp = sum(x['hbp'] for x in w5_logs)
            w5_sf = sum(x['sf'] for x in w5_logs)
            w5_tb = sum(x['tb'] for x in w5_logs)

            r5_avg = round(w5_h / w5_ab, 3) if w5_ab > 0 else 0.000
            r5_obp_denom = (w5_ab + w5_bb + w5_hbp + w5_sf)
            r5_obp = round((w5_h + w5_bb + w5_hbp) / r5_obp_denom, 3) if r5_obp_denom > 0 else 0.000
            r5_slg = round(w5_tb / w5_ab, 3) if w5_ab > 0 else 0.000
            r5_ops = round(r5_obp + r5_slg, 3)

            # Format game line string (e.g. "2-4, HR, 2 RBI, BB")
            hit_parts = [f"{g['h']}-{g['ab']}"]
            if g['hr'] > 0: hit_parts.append(f"{g['hr']} HR" if g['hr'] > 1 else "HR")
            elif g['3b'] > 0: hit_parts.append(f"{g['3b']} 3B" if g['3b'] > 1 else "3B")
            elif g['2b'] > 0: hit_parts.append(f"{g['2b']} 2B" if g['2b'] > 1 else "2B")
            if g['rbi'] > 0: hit_parts.append(f"{g['rbi']} RBI")
            if g['bb'] > 0: hit_parts.append(f"{g['bb']} BB")
            if g['r'] > 0: hit_parts.append(f"{g['r']} R")
            stat_summary = ", ".join(hit_parts)

            timeline.append({
                'gameIndex': idx,
                'gameDate': g['date'],
                'opponent': g['opponent'],
                'opponentShort': g['opponentShort'],
                'result': g['result'],
                'statSummary': stat_summary,
                # Single game stats
                'gameAb': g['ab'],
                'gameH': g['h'],
                'gameR': g['r'],
                'game2b': g['2b'],
                'game3b': g['3b'],
                'gameHr': g['hr'],
                'gameRbi': g['rbi'],
                'gameBb': g['bb'],
                'gameSo': g['so'],
                # Cumulative stats
                'cumG': idx,
                'cumAb': cum_ab,
                'cumH': cum_h,
                'cumR': cum_r,
                'cum2b': cum_2b,
                'cum3b': cum_3b,
                'cumHr': cum_hr,
                'cumRbi': cum_rbi,
                'cumBb': cum_bb,
                'cumSo': cum_so,
                'cumAvg': avg,
                'cumObp': obp,
                'cumSlg': slg,
                'cumOps': ops,
                # Rolling stats
                'roll5Avg': r5_avg,
                'roll5Obp': r5_obp,
                'roll5Slg': r5_slg,
                'roll5Ops': r5_ops
            })

        # Ensure final cumulative values tie out cleanly with official stats if timeline exists
        if timeline and len(timeline) > 0:
            # Let's align last point with official stats
            last = timeline[-1]
            last['cumAvg'] = p.get('battingAvg', last['cumAvg'])
            last['cumObp'] = p.get('obp', last['cumObp'])
            last['cumSlg'] = p.get('slg', last['cumSlg'])
            last['cumOps'] = p.get('ops', last['cumOps'])

        processed_players[b_id] = {
            'playerId': b_id,
            'fullName': p.get('fullName', 'Unknown'),
            'firstName': p.get('firstName', ''),
            'lastName': p.get('lastName', ''),
            'position': p.get('position', '-'),
            'teamName': p.get('teamName', ''),
            'teamId': p.get('teamId', ''),
            'headshotUrl': p.get('headshotUrl') or p.get('profileImageUrl') or '',
            'teamLogoUrl': p.get('teamLogoUrl') or p.get('teamLogoDarkUrl') or '',
            'officialStats': {
                'games': p.get('games', len(timeline)),
                'plateAppearances': p.get('plateAppearances', 0),
                'atBats': p.get('atBats', 0),
                'runs': p.get('runs', 0),
                'hits': p.get('hits', 0),
                'doubles': p.get('doubles', 0),
                'triples': p.get('triples', 0),
                'homeRuns': p.get('homeRuns', 0),
                'rbi': p.get('rbi', 0),
                'walks': p.get('walks', 0),
                'strikeouts': p.get('strikeouts', 0),
                'stolenBases': p.get('stolenBases', 0),
                'battingAvg': p.get('battingAvg', 0.0),
                'obp': p.get('obp', 0.0),
                'slg': p.get('slg', 0.0),
                'ops': p.get('ops', 0.0),
                'babip': p.get('babip', 0.0),
            },
            'gamesPlayedCount': len(timeline),
            'timeline': timeline
        }

    output_data = {
        'season': '2026 Regular Season',
        'generatedAt': '2026-10-21',
        'totalPlayers': len(processed_players),
        'teams': sorted(list(set(p['teamName'] for p in processed_players.values() if p['teamName']))),
        'players': processed_players
    }

    with open('cbl_2026_player_progression.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"Successfully processed {len(processed_players)} players and saved to cbl_2026_player_progression.json")

if __name__ == '__main__':
    build_player_progression()
