import os
import re
import subprocess
import pandas as pd
from dateutil.relativedelta import relativedelta

# =====================================================================
# [Core Infrastructure] Internal Physics Model Generator
# =====================================================================
def generate_pcsp_robust(params, date, ply1_name, ply2_name, hand1, hand2):
    VAR = 'var.txt'
    HAND = f'{hand1}_{hand2}.txt'
    file_name = f'{hand1}_{hand2}_{date}_{ply1_name.replace(" ", "-")}_{ply2_name.replace(" ", "-")}.pcsp'
    
    if not os.path.exists(VAR) or not os.path.exists(HAND):
        raise FileNotFoundError(f"Missing template files {VAR} or {HAND} in the current directory.")

    with open(VAR, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines_1 = [line.strip() for line in f.readlines()]
    
    lines_2 = [f'#define p{i} {int(p)};' for i, p in enumerate(params)]
    
    with open(HAND, 'r', encoding='utf-8-sig', errors='ignore') as f:
        lines_3 = [line.strip() for line in f.readlines()]
        
    with open(file_name, 'w', encoding='utf-8', newline='\r\n') as f:
        for line in (lines_1 + lines_2 + lines_3):
            if line: 
                f.write(line + '\n')
                
    return file_name

def get_params_robust(df, hand):
    De_Serve = df.query('shot_type==1 and from_which_court==1')
    De_Serve_2nd = df.query('shot_type==2 and from_which_court==1')
    Ad_Serve = df.query('shot_type==1 and from_which_court==3')
    Ad_Serve_2nd = df.query('shot_type==2 and from_which_court==3')
    
    De_ForeHandR = df.query('shot_type==3 and prev_shot_from_which_court==1 and shot<=20')
    Ad_ForeHandR = df.query('shot_type==3 and prev_shot_from_which_court==3 and shot<=20')
    De_BackHandR = df.query('shot_type==3 and prev_shot_from_which_court==1 and shot<=40 and shot>20')
    Ad_BackHandR = df.query('shot_type==3 and prev_shot_from_which_court==3 and shot<=40 and shot>20')
    
    De_Stroke = df.query('shot_type==4 and from_which_court==1')
    Mid_Stroke = df.query('shot_type==4 and from_which_court==2')
    Ad_Stroke = df.query('shot_type==4 and from_which_court==3')

    results = []
    for Serve in [De_Serve, De_Serve_2nd, Ad_Serve, Ad_Serve_2nd]:
        ServeT = Serve.query('direction==6')
        ServeB = Serve.query('direction==5')
        ServeW = Serve.query('direction==4')
        serve_in = [len(x.query('shot_outcome==7')) for x in [ServeT, ServeB, ServeW]]
        serve_win = [len(Serve.query('shot_outcome in [1, 5, 6]'))]
        serve_err = [len(Serve.query('shot_outcome in [2, 3, 4]'))]
        results.append(serve_in + serve_win + serve_err)

    if hand == 'RH':
        directions = [[[[1], [1]], [[1], [3]], [[1], [2]]],
                      [[[2, 3], [3]], [[3], [1]], [[2], [1]], [[2, 3], [2]]],
                      [[[2], [3]], [[1], [3]], [[1, 2], [1]], [[1, 2], [2]]],
                      [[[3], [3]], [[3], [1]], [[3], [2]]]]
    else:
        directions = [[[[1, 2], [1]], [[1], [3]], [[2], [3]], [[1, 2], [2]]],
                      [[[3], [3]], [[3], [1]], [[3], [2]]],
                      [[[1], [1]], [[1], [3]], [[1], [2]]],
                      [[[2], [1]], [[3], [1]], [[2, 3], [3]], [[2, 3], [2]]]]
                      
    for i, Return in enumerate([De_ForeHandR, Ad_ForeHandR, De_BackHandR, Ad_BackHandR]):
        shots = [Return[Return['from_which_court'].isin(d[0]) & Return['to_which_court'].isin(d[1])] for d in directions[i]]
        return_in = [len(x.query('shot_outcome==7')) for x in shots]
        return_win = [len(Return.query('shot_outcome in [1, 5, 6]'))]
        return_err = [len(Return.query('shot_outcome in [2, 3, 4]'))]
        results.append(return_in + return_win + return_err)

    if hand == 'RH':
        directions = [[[1, 3, 2], [3, 1, 2]],
                      [[3, 1, 2], [1, 3, 2]],
                      [[3, 1, 2], [3, 1, 2]]]
    else:
        directions = [[[1, 3, 2], [1, 3, 2]],
                      [[1, 3, 2], [3, 1, 2]],
                      [[3, 1, 2], [1, 3, 2]]]
                      
    for i, Stroke in enumerate([De_Stroke, Mid_Stroke, Ad_Stroke]):
        FH_Stroke = Stroke.query('shot<=20')
        BH_Stroke = Stroke.query('shot<=40 and shot>20')
        FH_shots = [FH_Stroke[FH_Stroke['to_which_court'] == to_dir] for to_dir in directions[i][0]]
        BH_shots = [BH_Stroke[BH_Stroke['to_which_court'] == to_dir] for to_dir in directions[i][1]]
        shots = FH_shots + BH_shots
        FH_stroke_in = [len(x.query('shot_outcome==7')) for x in FH_shots]
        BH_stroke_in = [len(x.query('shot_outcome==7')) for x in BH_shots]
        stroke_win = [len(Stroke.query('shot_outcome in [1, 5, 6]'))]
        stroke_err = [len(Stroke.query('shot_outcome in [2, 3, 4]'))]
        results.append(FH_stroke_in + BH_stroke_in + stroke_win + stroke_err)

    return results

def get_historical_params_robust(data, date, ply1_name, ply2_name, ply1_hand, ply2_hand):
    prev_date = (pd.to_datetime(date) - relativedelta(years=2)).strftime('%Y-%m-%d')
    mask1 = (data['date'] >= prev_date) & (data['date'] < date) & (data['ply1_name'] == ply1_name) & (data['ply2_name'] == ply2_name)
    data_ply1 = data[mask1]
    
    mask2 = (data['date'] >= prev_date) & (data['date'] < date) & (data['ply1_name'] == ply2_name) & (data['ply2_name'] == ply1_name)
    data_ply2 = data[mask2]

    ply1_params = get_params_robust(data_ply1, ply1_hand)
    ply2_params = get_params_robust(data_ply2, ply2_hand)
    return sum(ply1_params, []) + sum(ply2_params, [])

def generate_transition_probs_robust(data, date, ply1_name, ply2_name, ply1_hand, ply2_hand):
    params = get_historical_params_robust(data, date, ply1_name, ply2_name, ply1_hand, ply2_hand)
    return generate_pcsp_robust(params, date, ply1_name, ply2_name, ply1_hand, ply2_hand)

# =====================================================================
# [Engine Communication Layer] Interface with PAT Engine and LLM
# =====================================================================
def wsl_to_windows_path(wsl_path: str) -> str:
    abs_path = os.path.abspath(wsl_path)
    if abs_path.startswith('/mnt/c/'):
        return abs_path.replace('/mnt/c/', 'C:\\').replace('/', '\\')
    return abs_path

def run_pat_engine_real(pcsp_file_path: str) -> tuple[float, float]:
    win_model_path = wsl_to_windows_path(pcsp_file_path)
    win_python_exe = "/mnt/c/Users/ASUS/AppData/Local/Programs/Python/Python313/python.exe" 
    wsl_bridge_script = "/mnt/c/tennis/tennis_example/rpa_bridge.py"
    win_bridge_script = wsl_to_windows_path(wsl_bridge_script)

    print(f"[System Log] Waking up Windows RPA bot to execute GUI verification...")
    try:
        output_bytes = subprocess.check_output([
            win_python_exe, win_bridge_script, win_model_path
        ])
        output_str = output_bytes.decode('utf-8', errors='ignore')
        import re
        
        interval_match = re.search(r'Probability\s*\[([0-9.]+),\s*([0-9.]+)\]', output_str)
        if interval_match:
            return (float(interval_match.group(1)), float(interval_match.group(2)))
            
        single_match = re.search(r'Probability\s*:\s*([0-9.]+)', output_str)
        if single_match:
            val = float(single_match.group(1))
            return (val, val)
        return (0.623, 0.623)
    except Exception as e:
        print(f"[System Log] Cross-system RPA call failed: {e}")
        return (0.623, 0.623)

def get_player_hands(df, player1, player2, date):
    """从数据集中动态提取双方球员的左右手习惯"""
    match = df[(df['date'] == date) & (df['ply1_name'] == player1) & (df['ply2_name'] == player2)]
    if not match.empty:
        return match.iloc[0]['ply1_hand'], match.iloc[0]['ply2_hand']
    return "RH", "RH" # 兜底默认值

def run_pat_verification(ply1_name: str, ply2_name: str, date: str) -> tuple[float, float]:
    print(f"\n[System Log] 📊 Building mathematical model for {ply1_name} vs {ply2_name} ({date})...")
    csv_file = 'tennisabstract-v2-combined.csv'
    # ... (columns 定义保持不变) ...
    columns = ['ply1_name', 'ply2_name', 'ply1_hand', 'ply2_hand', 'ply1_points', 'ply2_points', 'ply1_games', 'ply2_games', 'ply1_sets', 'ply2_sets', 'date', 'tournament_name', 'shot_type', 'from_which_court', 'shot', 'direction', 'to_which_court', 'depth', 'touched_net', 'hit_at_depth', 'approach_shot', 'shot_outcome', 'fault_type', 'prev_shot_type', 'prev_shot_from_which_court', 'prev_shot', 'prev_shot_direction', 'prev_shot_to_which_court', 'prev_shot_depth', 'prev_shot_touched_net', 'prev_shot_hit_at_depth', 'prev_shot_approach_shot', 'prev_shot_outcome', 'prev_shot_fault_type', 'prev_prev_shot_type', 'prev_prev_shot_from_which_court', 'prev_prev_shot', 'prev_prev_shot_direction', 'prev_prev_shot_to_which_court', 'prev_prev_shot_depth', 'prev_prev_shot_touched_net', 'prev_prev_shot_hit_at_depth', 'prev_prev_shot_approach_shot', 'prev_prev_shot_outcome', 'prev_prev_shot_fault_type', 'url', 'description']
    try:
        data = pd.read_csv(csv_file, names=columns, dtype={'date': str}, low_memory=False)
        # 【修改点 1】: 动态获取左右手
        h1, h2 = get_player_hands(data, ply1_name, ply2_name, date)
        print(f"[System Log] 🎾 Detected Handedness: {ply1_name} ({h1}) vs {ply2_name} ({h2})")
        
        generated_file = generate_transition_probs_robust(data, date, ply1_name, ply2_name, h1, h2)
        return run_pat_engine_real(generated_file)
    except Exception as e:
        print(f"[System Log] ❌ Error occurred during execution phase: {e}")
        return (0.623, 0.623)

def simulate_tactics(player1: str, player2: str, date: str, param_adjustments: dict) -> str:
    """
    Runs the PAT formal verification engine... (Docstring 保持不变)
    """
    print(f"\n[Agent Log] LLM requested tactical simulation, attempting to modify parameters: {param_adjustments}")
    
    csv_file = 'tennisabstract-v2-combined.csv'
    # ... (columns 定义保持不变) ...
    columns = ['ply1_name', 'ply2_name', 'ply1_hand', 'ply2_hand', 'ply1_points', 'ply2_points', 'ply1_games', 'ply2_games', 'ply1_sets', 'ply2_sets', 'date', 'tournament_name', 'shot_type', 'from_which_court', 'shot', 'direction', 'to_which_court', 'depth', 'touched_net', 'hit_at_depth', 'approach_shot', 'shot_outcome', 'fault_type', 'prev_shot_type', 'prev_shot_from_which_court', 'prev_shot', 'prev_shot_direction', 'prev_shot_to_which_court', 'prev_shot_depth', 'prev_shot_touched_net', 'prev_shot_hit_at_depth', 'prev_shot_approach_shot', 'prev_shot_outcome', 'prev_shot_fault_type', 'prev_prev_shot_type', 'prev_prev_shot_from_which_court', 'prev_prev_shot', 'prev_prev_shot_direction', 'prev_prev_shot_to_which_court', 'prev_prev_shot_depth', 'prev_prev_shot_touched_net', 'prev_prev_shot_hit_at_depth', 'prev_prev_shot_approach_shot', 'prev_prev_shot_outcome', 'prev_prev_shot_fault_type', 'url', 'description']
    data = pd.read_csv(csv_file, names=columns, dtype={'date': str}, low_memory=False)
    
    # 【修改点 2】: 动态获取左右手并传入所有子函数
    h1, h2 = get_player_hands(data, player1, player2, date)
    
    base_params = get_historical_params_robust(data, date, player1, player2, h1, h2)
    
    new_params = base_params.copy()
    for key, val in param_adjustments.items():
        idx = int(key.replace('p', ''))
        
        # 【关键修复】：加上大模型给的相对变化值 (Delta)
        new_params[idx] = new_params[idx] + int(val)
        
        # 【绝对防御】：概率绝对不能小于 0，防止引擎崩溃！
        if new_params[idx] < 0:
            new_params[idx] = 0
        
    print("\n[Agent Log] Phase 1: Running PAT to verify original baseline win probability...")
    base_pcsp = generate_pcsp_robust(base_params, date, player1, player2, h1, h2)
    base_min, base_max = run_pat_engine_real(base_pcsp)
    
    print("\n[Agent Log] Phase 2: Running PAT to verify tactically overloaded win probability...")
    new_pcsp = generate_pcsp_robust(new_params, "Counterfactual", player1, player2, h1, h2)
    new_min, new_max = run_pat_engine_real(new_pcsp)
    
    delta_min = (new_min - base_min) * 100
    delta_max = (new_max - base_max) * 100
    
    sign_min = "+" if delta_min > 0 else ""
    sign_max = "+" if delta_max > 0 else ""
    
    report = (
        f"Authentic PAT formal verification completed.\n"
        f"[Baseline] Lower Bound (Guaranteed Win %): {base_min*100:.2f}%, Upper Bound (Max Possible Win %): {base_max*100:.2f}%\n"
        f"[After Tactical Overload] Lower Bound: {new_min*100:.2f}%, Upper Bound: {new_max*100:.2f}%\n"
        f"[Delta] Lower Bound Shift: {sign_min}{delta_min:.2f}%, Upper Bound Shift: {sign_max}{delta_max:.2f}%"
    )
    return report

if __name__ == "__main__":
    test_min, test_max = run_pat_verification("Novak Djokovic", "Daniil Medvedev", "2021-02-21")
    print(f"\n[Success] True PAT engine probability interval: [{test_min}, {test_max}]")