import os
import re
from pathlib import Path
import pandas as pd
import numpy as np

                          
EL = "PEM"                     
base_root = Path(r"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Results_M12_0812") / EL
out_dir = Path(r"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Processing")
out_dir.mkdir(parents=True, exist_ok=True)
out_xlsx = out_dir / f"LCOM_{EL}_CitytoState.xlsx"

years = [2030, 2040, 2050]
sheet_names = {
    2030: {'line': '2030_LCOM', 'prov': '2030_Prov_LCOM_j', 'city': '2030_City_LCOM_j'},
    2040: {'line': '2040_LCOM', 'prov': '2040_Prov_LCOM_j', 'city': '2040_City_LCOM_j'},
    2050: {'line': '2050_LCOM', 'prov': '2050_Prov_LCOM_j', 'city': '2050_City_LCOM_j'}
}

                           
ed_dirs = sorted([p for p in base_root.glob("ED*") if p.is_dir()],
                 key=lambda p: int(re.sub(r"\D", "", p.name) or 0))
eds = sorted({int(re.search(r"ED(\d+)", p.name).group(1)) for p in ed_dirs if re.search(r"ED(\d+)", p.name)})
if not eds:
    raise RuntimeError(f"No ED folders found under: {base_root}")
print(f"[Info] EL={EL}, found EDs={eds}")

                           
city_minus_state = pd.DataFrame(index=years, columns=eds, dtype=float)
prov_minus_state = pd.DataFrame(index=years, columns=eds, dtype=float)
coal_baseline = pd.DataFrame(index=years, columns=eds, dtype=float)
state_baseline = pd.DataFrame(index=years, columns=eds, dtype=float)

                          
def read_line_values(xls, y, fpath):
    sname = sheet_names[y]['line']
    try:
        df = pd.read_excel(xls, sheet_name=sname)
    except Exception as e:
        print(f"[Warn] Missing sheet '{sname}' in {fpath}: {e}")
        return None, None, None, None

    def pick(label):
        try:
            v = df.loc[df['Levelized_cost'] == label, 'Value'].values
            return float(v[0]) if len(v) else np.nan
        except Exception:
            return np.nan

    city = pick('City_LCOM')
    prov = pick('Prov_LCOM')
    state = pick('State_LCOM')
    coal = pick('Coal_LCOM')
    if pd.isna(state):
        state = coal
    return city, prov, state, coal

def get_minmax_with_name(df, find_max=True):
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    if df.empty:
        return np.nan, None
    row = df.loc[df['Value'].idxmax() if find_max else df['Value'].idxmin()]
    name_col = next((col for col in ['City_LCOM_j', 'Prov_LCOM_j', 'Province', 'City'] if col in df.columns), None)
    return float(row['Value']), row.get(name_col) if name_col else None

def read_extrema(xls, y, fpath):
    s_prov = sheet_names[y]['prov']
    s_city = sheet_names[y]['city']

    def get_sheet_minmax(sheet, find_max=True):
        try:
            df = pd.read_excel(xls, sheet_name=sheet)
            return get_minmax_with_name(df, find_max=find_max)
        except Exception as e:
            print(f"[Warn] Missing sheet '{sheet}' in {fpath}: {e}")
            return np.nan, None

    city_max, city_max_name = get_sheet_minmax(s_city, find_max=True)
    city_min, city_min_name = get_sheet_minmax(s_city, find_max=False)
    prov_max, prov_max_name = get_sheet_minmax(s_prov, find_max=True)
    prov_min, prov_min_name = get_sheet_minmax(s_prov, find_max=False)

    return (city_max, city_min, prov_max, prov_min,
            city_max_name, city_min_name, prov_max_name, prov_min_name)

                         
flat_rows = []
city_max_rows, city_min_rows = [], []
prov_max_rows, prov_min_rows = [], []

for ed in eds:
    f = base_root / f"ED{ed}" / f"LCOM_{EL}_ED{ed}.xlsx"
    if not f.exists():
        print(f"[Warn] File not found: {f}")
        continue
    xls = pd.ExcelFile(f)
    for y in years:
        city, prov, state, coal = read_line_values(xls, y, f)
        if city is None and prov is None and state is None:
            print(f"[Warn] Skip (no line values): {f.name} | {y}")
            continue

        if pd.notna(city) and pd.notna(state):
            city_minus_state.loc[y, ed] = city - state
        if pd.notna(prov) and pd.notna(state):
            prov_minus_state.loc[y, ed] = prov - state
        if pd.notna(coal):
            coal_baseline.loc[y, ed] = coal
        if pd.notna(state):
            state_baseline.loc[y, ed] = state

        diff = state - coal if pd.notna(state) and pd.notna(coal) else np.nan
        flat_rows.append({'Year': y, 'ED': ed, 'Coal_LCOM': coal, 'State_LCOM': state, 'Difference': diff})

        city_max, city_min, prov_max, prov_min, city_max_name, city_min_name, prov_max_name, prov_min_name = read_extrema(xls, y, f)
        city_max_rows.append({'Year': y, 'ED': ed, 'CityMax': city_max, 'Difference': city_max - state if pd.notna(city_max) and pd.notna(state) else np.nan, 'Prov': city_max_name})
        city_min_rows.append({'Year': y, 'ED': ed, 'CityMin': city_min, 'Difference': city_min - state if pd.notna(city_min) and pd.notna(state) else np.nan, 'Prov': city_min_name})
        prov_max_rows.append({'Year': y, 'ED': ed, 'ProvMax': prov_max, 'Difference': prov_max - state if pd.notna(prov_max) and pd.notna(state) else np.nan, 'Prov': prov_max_name})
        prov_min_rows.append({'Year': y, 'ED': ed, 'ProvMin': prov_min, 'Difference': prov_min - state if pd.notna(prov_min) and pd.notna(state) else np.nan, 'Prov': prov_min_name})

                               
avg_rows_city = []
avg_rows_prov = []

for y in years:
    for ed in eds:
        state = state_baseline.loc[y, ed]
        city_val = state + city_minus_state.loc[y, ed] if pd.notna(state) and pd.notna(city_minus_state.loc[y, ed]) else np.nan
        prov_val = state + prov_minus_state.loc[y, ed] if pd.notna(state) and pd.notna(prov_minus_state.loc[y, ed]) else np.nan
        avg_rows_city.append({'Year': y, 'ED': ed, 'CityAvg': city_val, 'Difference': city_val - state if pd.notna(city_val) and pd.notna(state) else np.nan})
        avg_rows_prov.append({'Year': y, 'ED': ed, 'ProvAvg': prov_val, 'Difference': prov_val - state if pd.notna(prov_val) and pd.notna(state) else np.nan})

df_city_avg = pd.DataFrame(avg_rows_city)
df_prov_avg = pd.DataFrame(avg_rows_prov)

                                       
def add_diff_ratio(df, value_col):
    df = df.copy()
    df['DiffRatio'] = np.nan
    for idx, row in df.iterrows():
        val = row[value_col]
        diff = row['Difference']
        if pd.notna(val) and val != 0 and pd.notna(diff):
            df.at[idx, 'DiffRatio'] = (diff / val) * 100
    return df

df_city_max = add_diff_ratio(pd.DataFrame(city_max_rows), 'CityMax')
df_city_min = add_diff_ratio(pd.DataFrame(city_min_rows), 'CityMin')
df_prov_max = add_diff_ratio(pd.DataFrame(prov_max_rows), 'ProvMax')
df_prov_min = add_diff_ratio(pd.DataFrame(prov_min_rows), 'ProvMin')
df_city_avg = add_diff_ratio(df_city_avg, 'CityAvg')
df_prov_avg = add_diff_ratio(df_prov_avg, 'ProvAvg')

                             
summary_frames = {
    'City_Max_Flat': df_city_max,
    'City_Min_Flat': df_city_min,
    'Prov_Max_Flat': df_prov_max,
    'Prov_Min_Flat': df_prov_min,
    'City_Avg_Flat': df_city_avg,
    'Prov_Avg_Flat': df_prov_avg
}

summary_data = []
for name, df in summary_frames.items():
    value_col = [c for c in df.columns if c not in ['Year', 'ED', 'Difference', 'DiffRatio', 'Prov']][0]
    summary_data.append({
        'Sheet': name,
        'Average value': df[value_col].mean(),
        'Average difference': df['Difference'].mean(),
        'Average portion': df['DiffRatio'].mean()
    })

df_summary = pd.DataFrame(summary_data)

                               
with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    coal_baseline.to_excel(writer, sheet_name="coal_raw")
    state_baseline.to_excel(writer, sheet_name="state_raw")
    pd.DataFrame(flat_rows).to_excel(writer, sheet_name="Coal_BAU", index=False)
    df_city_max.to_excel(writer, sheet_name="City_Max_Flat", index=False)
    df_city_min.to_excel(writer, sheet_name="City_Min_Flat", index=False)
    df_prov_max.to_excel(writer, sheet_name="Prov_Max_Flat", index=False)
    df_prov_min.to_excel(writer, sheet_name="Prov_Min_Flat", index=False)
    df_city_avg.to_excel(writer, sheet_name="City_Avg_Flat", index=False)
    df_prov_avg.to_excel(writer, sheet_name="Prov_Avg_Flat", index=False)
    df_summary.to_excel(writer, sheet_name="Summary", index=False)

print(f"[Done] Saved summary to: {out_xlsx}")
