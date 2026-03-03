import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# —————— 用户自定义路径与参数 ——————
el = "PEM"
base_dir = r"D:/GAMS_optimization/Statewide/Updated_Gams/P2_Cost_vs_ED"
file_path = os.path.join(base_dir, "pycode", el, "bar_allyears", "merged_CB_UE.xlsx")
output_path = os.path.join(base_dir, "Figure")

# —————— 各年份实际的 EI 列表 ——————
year_ei_levels = {
    2030: ["25%", "50%", "75%", "100%"],
    2040: ["25%", "60%", "75%", "100%"],
    2050: ["25%", "50%", "75%", "94%"],
}

# —————— 图形配色与顺序 ——————
color_map = {
    'Coal': "#000000",
    'OM_coal': "#c0c0c0",
    'OM_Msyn': "#607D8B",
    'CO2': "#3F51B5",
    'Grid': "#FFEB3B",
    'PV_CAP': "#FF9800",
    'PV_OM': "#FFCC80",
    'WT_CAP': "#8BC34A",
    'WT_OM': "#DCEDC8",
    f'{el}_CAP': "#E91E63",
    f'{el}_OM': "#F8BBD0",
    'HST_CAP': "#673AB7",
    'HST_OM': "#D1C4E9",
    'RWS_CAP': "#4FB477",
    'RWS_OM': "#C4E9C7",
    'H2O': "#E2F6FF",
    'O2': "#4DD0E1",
    'TNS': "#695546",
    'Lib_CAP': "#B0BEC5",
    'Lib_OM': "#78909C"
}
category_order = list(color_map.keys())
x_spacing_scale = 1.0

def load_data():
    df_cb = {}
    df_lcce = {}
    for year in year_ei_levels:
        df_cb[year] = pd.read_excel(file_path, sheet_name=f"{year}_CB", index_col=0).fillna(0) / 1e6
        df_lcce[year] = pd.read_excel(file_path, sheet_name=f"{year}_LCCE", index_col=0).fillna(0)
    return df_cb, df_lcce

def plot_cost_decarbonization(df_dict, lcce_dict):
    width = 0.6
    fig, ax1 = plt.subplots(figsize=(14, 8.5))
    ax2 = ax1.twinx()

    x_labels = []
    x_pos_map = {}
    x_pos = 0
    y_pos_max = float('-inf')
    y_neg_min = float('inf')
    y2_pos_max = float('-inf')
    y2_neg_min = float('inf')
    x_blue, y_blue = [], []

    for year in year_ei_levels:
        ei_list = ["BAU"] + year_ei_levels[year]
        df = df_dict[year]
        lcce = lcce_dict[year]

        for label in ei_list:
            x_labels.append(label)
            x_pos_map[(year, label)] = x_pos
            bottom_pos = 0
            bottom_neg = 0
            total_val = 0

            for cat in category_order:
                if cat in df.index and label in df.columns:
                    val = df.loc[cat, label]
                    total_val += val
                    if val >= 0:
                        ax1.bar(x_pos, val, width, bottom=bottom_pos, color=color_map.get(cat,"#ccc"),
                                label=cat if x_pos==0 else "")
                        bottom_pos += val
                        y_pos_max = max(y_pos_max, bottom_pos)
                    else:
                        ax1.bar(x_pos, val, width, bottom=bottom_neg, color=color_map.get(cat,"#ccc"),
                                label=cat if x_pos==0 else "")
                        bottom_neg += val
                        y_neg_min = min(y_neg_min, bottom_neg)

            ax1.scatter(x_pos, total_val, color='blue', s=25, zorder=10, marker='s', label='Total cost')
            x_blue.append(x_pos)
            y_blue.append(total_val)
            x_pos += x_spacing_scale
        x_labels.append("")
        x_pos += x_spacing_scale

    x_labels = x_labels[:-1]
    ax1.set_ylim(y_neg_min * 1.25 if y_neg_min < 0 else 0, y_pos_max * 1.1)

    ax1.set_ylabel("TAC (Billions 2025 USD)", fontsize=20)
    ax2.set_ylabel("Unit Emission (Tonne CO₂/Tonne)", fontsize=20, color='red')
    ax1.tick_params(axis='y', labelcolor='black', labelsize = 16)
    ax2.tick_params(axis='y', labelcolor='red', labelsize = 16)

    ax1.set_xticks(range(len(x_labels)))
    ax1.set_xticklabels(x_labels, rotation=90, fontsize=14)

    # 添加年份标注
    fig.text(0.25, 0.02, "2030", ha='center', va='top', fontsize=18, fontweight='bold')
    fig.text(0.50, 0.02, "2040", ha='center', va='top', fontsize=18, fontweight='bold')
    fig.text(0.78, 0.02, "2050", ha='center', va='top', fontsize=18, fontweight='bold')

    # Plot LCEC 点
    for i, year in enumerate(year_ei_levels):
        ei_list = ["BAU"] + year_ei_levels[year]
        lcce_df = lcce_dict[year]
        ei_list = year_ei_levels[year]
        for j, label in enumerate(ei_list):
            ei_val = int(label.replace("%", ""))
            x_idx = (i * 6 + j + 1) * x_spacing_scale
            try:
                val = lcce_df.loc[ei_val, "VALUE"]
            except KeyError:
                print(f"[Warning] Missing LCCE for {year} {ei_val}%")
                continue

            if i == 0 and j == 0:
                ax2.scatter(x_idx, val, color='red', s=30, zorder=10, label='Decarbonization cost')
            else:
                ax2.scatter(x_idx, val, color='red', s=30, zorder=10)

            y2_pos_max = max(y2_pos_max, val)
            y2_neg_min = min(y2_neg_min, val)
            ax2.text(x_idx, val + (abs(val) * 0.05 ), f"{val:.1f}", color='red',
                     fontsize=10, ha='center', va='bottom')



    ax2.set_ylim(y2_neg_min * 1.25 if y2_neg_min < 0 else 0, y2_pos_max * 1.1)

    # 图例
    legend_name_map = {
        'CO2': 'CO₂ emission/consumption',
        'O2': 'O₂ revenue',
        'Total cost': 'TAC',
        'Decarbonization cost': 'Unit Emission',
        'OM_coal': 'Coal processing O&M',
        'OM_Msyn': 'Methanol synthesis O&M',
        'Grid': 'Electricity purchase',
        'PV_CAP': 'PV CapEx',
        'PV_OM': 'PV O&M',
        'WT_CAP': 'Wind CapEx',
        'WT_OM': 'Wind O&M',
        f'{el}_CAP': f'{el} CapEx',
        f'{el}_OM': f'{el} O&M',
        'RWS_CAP': 'RWGS CapEx',
        'RWS_OM': 'RWGS O&M',
        'HST_CAP': 'Storage CapEx',
        'HST_OM': 'Storage O&M',
        'H2O': 'Water consumption',
        'TNS': 'Transmission O&M',
        'Coal': 'Raw coal consumption',
    }

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    blue_handle, blue_label = None, None
    for h, l in zip(handles1, labels1):
        if l == 'Total cost':
            blue_handle = h
            blue_label = l
            break
    handles1 = [h for h, l in zip(handles1, labels1) if l != 'Total cost']
    labels1 = [l for l in labels1 if l != 'Total cost']
    handles = handles1 + handles2 + [blue_handle]
    labels = labels1 + labels2 + [blue_label]
    labels = [legend_name_map.get(l, l) for l in labels]
    uniq = dict(zip(labels, handles))

    ax1.legend(uniq.values(), uniq.keys(), loc='upper center', ncol=5, bbox_to_anchor=(0.5, 1.18),
               fontsize=12, frameon=False)

    plt.subplots_adjust(bottom=0.12)
    fig.savefig(os.path.join(output_path, f"Cost_DEC_AllYears_{el}.png"), dpi=600)
    print("Saved figure to:", output_path)

# —————— 执行入口 ——————
if __name__ == "__main__":
    df_dict, df_decarb = load_data()
    plot_cost_decarbonization(df_dict, df_decarb)
