import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as mticker  # 确保开头导入了这个模块
import matplotlib.patches as mpatches

plt.rcParams['axes.linewidth'] = 1.5 # 坐标轴边框宽度


# —————— 用户自定义路径与参数 ——————
el = "PEM"
base_dir = r"D:/GAMS_optimization/Statewide/Updated_Gams/P2_Cost_vs_ED"
file_path = os.path.join(base_dir, "pycode", el, "bar_allyears", "merged_CB_UE.xlsx")
file_path_cityprov = os.path.join(base_dir, "pycode", el, "bar_allyears", "merged_CB_CityProv.xlsx")
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
    'SOE_CAP': "#E91E63",
    'SOE_OM': "#F8BBD0",
    'PEM_CAP': "#FE6F37",
    'PEM_OM': "#FF966C",
    'HST_CAP': "#55D6C9",
    'HST_OM': "#B9FFF8",
    'SST_CAP': "#673AB7",
    'SST_OM': "#D1C4E9",
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

def load_cityprov_data(file_path_cityprov):
    df_cb = {}
    df_lcce = {}
    for year in ["2040", "2050"]:
        df_cb_all = pd.read_excel(file_path_cityprov, sheet_name=f"{year}_CB", index_col=0).fillna(0) / 1e6
        df_lcce_all = pd.read_excel(file_path_cityprov, sheet_name=f"{year}_LCCE", index_col=0).fillna(0)
        for region in ["City", "Prov"]:
            cb_filtered = df_cb_all[[region]]
            if region in df_lcce_all.index:
                lcce_filtered = df_lcce_all.loc[[region]]
                df_cb[f"{year}_{region.lower()}"] = cb_filtered
                df_lcce[f"{year}_{region.lower()}"] = lcce_filtered
    return df_cb, df_lcce

def plot_combined_two_diagrams(df_cb_dict, df_lcce_dict, df_cb_cityprov, df_lcce_cityprov):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5), width_ratios=[4, 1])
    ax1b = ax1.twinx()

# LHS
    width = 0.6
    x_labels = []
    x_pos_map = {}
    x_pos = 0

    y_pos_max = float('-inf')
    y_neg_min = float('inf')
    y2_pos_max = float('-inf')
    y2_neg_min = float('inf')

    x_blue, y_blue = [], []

    for i, year in enumerate(year_ei_levels):
        ei_list_full = ["BAU"] + year_ei_levels[year]
        df = df_cb_dict[year]
        lcce_df = df_lcce_dict[year]

        for j, label in enumerate(ei_list_full):
            x_labels.append(label)
            x_pos_map[(year, label)] = x_pos

            bottom_pos = 0
            bottom_neg = 0
            total_val = 0

            # ax1 堆叠柱状图
            for cat in category_order:
                if cat in df.index and label in df.columns:
                    val = df.loc[cat, label]
                    total_val += val

                    if val >= 0:
                        ax1.bar(
                            x_pos, val, width, bottom=bottom_pos,
                            color=color_map.get(cat, "#ccc"),
                            label=cat if x_pos == 0 else ""
                        )
                        bottom_pos += val
                        y_pos_max = max(y_pos_max, bottom_pos)
                    else:
                        ax1.bar(
                            x_pos, val, width, bottom=bottom_neg,
                            color=color_map.get(cat, "#ccc"),
                            label=cat if x_pos == 0 else ""
                        )
                        bottom_neg += val
                        y_neg_min = min(y_neg_min, bottom_neg)

            # ax1 total cost 蓝点
            ax1.scatter(
                x_pos, total_val, color='blue', s=25, zorder=10,
                marker='s', label='Total cost'
            )
            x_blue.append(x_pos)
            y_blue.append(total_val)

            # ax1b decarbonization cost 红点
            if label != "BAU":
                ei_val = int(label.replace("%", ""))
                x_idx = x_pos_map[(year, label)]  # 用柱状图的位置
                try:
                    val = lcce_df.loc[ei_val, "VALUE"]
                    if i == 0 and j == 1:
                        ax1b.scatter(x_idx, val, color='red', s=30, zorder=10, label='Decarbonization cost')
                    else:
                        ax1b.scatter(x_idx, val, color='red', s=30, zorder=10)

                    y2_pos_max = max(y2_pos_max, val)
                    y2_neg_min = min(y2_neg_min, val)

                    ax1b.text(
                        x_idx, val + 0.15,
                        f"{val:.1f}", color='red',
                        fontsize=10, ha='center', va='bottom'
                    )
                except KeyError:
                    print(f"[Warning] Missing LCCE for {year} {ei_val}%")
            x_pos += x_spacing_scale

        x_labels.append("")
        x_pos += x_spacing_scale

    x_labels = x_labels[:-1]

    ax1.set_ylim(
        y_neg_min * 1.15 if y_neg_min < 0 else 0,
        y_pos_max * 1.15
    )
    ax1.set_ylabel("TAC (Billions 2025 USD)", fontsize=20)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=16)

    ax1b.set_ylabel("Unit Emission (Tonne CO₂/Tonne)", fontsize=20, color='red')
    ax1b.tick_params(axis='y', labelcolor='red', labelsize=16)

    ax1.set_xticks(range(len(x_labels)))
    ax1.set_xticklabels(x_labels, rotation=90, fontsize=16)

    # 添加年份标注
    fig.text(0.21, 0.06, "2030", ha='center', va='top', fontsize=16, fontweight='bold')
    fig.text(0.37, 0.06, "2040", ha='center', va='top', fontsize=16, fontweight='bold')
    fig.text(0.53, 0.06, "2050", ha='center', va='top', fontsize=16, fontweight='bold')

    ax1b.set_ylim(
        y2_neg_min * 1.15 if y2_neg_min < 0 else 0,
        y2_pos_max * 1.15
    )


#RHS
    # —————— 右图部分 ——————
    tags = list(df_cb_cityprov.keys())
    tag_labels = ["City", "Prov", "City", "Prov"]
    ax2b = ax2.twinx()
    y2_pos_max_rhs = float('-inf')
    y2_neg_min_rhs = float('inf')

    # 自定义 x 坐标，给 2040 两个条形位置 0, 1，给 2050 两个条形位置 3, 4（中间跳过2）
    x_locs = [0, 1, 2.2, 3.2]  # ← 更紧凑，空隙小但仍可区分

    for i, (tag, x) in enumerate(zip(tags, x_locs)):
        df = df_cb_cityprov[tag]
        year, region = tag.split("_")
        lcce_df = df_lcce_cityprov[tag]
        bottom_pos = 0
        bottom_neg = 0
        for cat in category_order:
            if cat in df.index:
                val = df.loc[cat].values[0]
                if val >= 0:
                    ax2.bar(x, val, width=0.6, bottom=bottom_pos, color=color_map.get(cat, "#ccc"))
                    bottom_pos += val
                else:
                    ax2.bar(x, val, width=0.6, bottom=bottom_neg, color=color_map.get(cat, "#ccc"))
                    bottom_neg += val
        total_val = bottom_pos + bottom_neg
        ax2.scatter(x, total_val, color='blue', s=30, marker='s')
        try:
            val = lcce_df.loc[region.capitalize()].values[0]
            ax2b.scatter(x, val, color='red', s=30)
            ax2b.text(x, val + (abs(val) * 0.05), f"{val:.1f}", color='red', fontsize=10, ha='center')
            y2_pos_max_rhs = max(y2_pos_max_rhs, val)
            y2_neg_min_rhs = min(y2_neg_min_rhs, val)
        except:
            pass

    ax2.set_xticks(x_locs)
    ax2.set_xticklabels(tag_labels, rotation=90, fontsize=16)
    ax2.set_ylabel("TAC (Billions 2025 USD)", fontsize=20)
    ax2.set_ylim(ax1.get_ylim())  # ← 添加这一行同步主轴Y范围
    ax2.tick_params(axis='y', labelcolor='black', labelsize=16)
    ax2b.set_ylabel("Unit Emission (Tonne CO₂/Tonne)", fontsize=20, color='red')
    ax2b.tick_params(axis='y', labelcolor='red', labelsize=16)
    ax2b.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))

    # 添加右图年份标注
    fig.text(0.81, 0.06, "2040", ha='center', va='top', fontsize=16, fontweight='bold')
    fig.text(0.87, 0.06, "2050", ha='center', va='top', fontsize=16, fontweight='bold')
    ax2b.set_ylim(
    y2_neg_min_rhs * 1.15 if y2_neg_min_rhs < 0 else 0,
    y2_pos_max_rhs * 1.15
    )


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
        'Lib_CAP':'LiB CapEX',
        'Lib_OM':'LiB O&M',     
        'SOE_CAP': 'SOE CapEx',
        'SOE_OM': 'SOE O&M',
        'PEM_CAP': 'PEM CapEx',
        'PEM_OM': 'PEM O&M',
        'RWS_CAP': 'RWGS CapEx',
        'RWS_OM': 'RWGS O&M',
        'HST_CAP': 'Storage CapEx',
        'HST_OM': 'Storage O&M',
        'H2O': 'Water consumption',
        'TNS': 'Transmission O&M',
        'Coal': 'Raw coal consumption',
    }

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax1b.get_legend_handles_labels()

    blue_handle, blue_label = None, None
    for h, l in zip(handles1, labels1):
        if l == 'Total cost':
            blue_handle = h
            blue_label = l
            break
    handles1 = [h for h, l in zip(handles1, labels1) if l != 'Total cost']
    labels1 = [l for l in labels1 if l != 'Total cost']


    # 加入虚拟 PEM legend
    manual_legend_keys = ['SOE_CAP', 'SOE_OM', 'SST_CAP', 'SST_OM']
    manual_handles = [mpatches.Patch(color=color_map[k], label=k) for k in manual_legend_keys]
    manual_labels = manual_legend_keys

    handles = handles1 + manual_handles + handles2 + [blue_handle]
    labels = labels1 + manual_labels + labels2  + [blue_label]
    labels = [legend_name_map.get(l, l) for l in labels]
    uniq = dict(zip(labels, handles))


    ax1.legend(uniq.values(), uniq.keys(), loc='upper center', ncol=6, bbox_to_anchor=(0.75, 1.29),
               fontsize=12, frameon=False)

    plt.subplots_adjust(top=0.83, bottom=0.16, wspace=0.4)
    fig.savefig(
        os.path.join(output_path, f"Cost_DEC_AllYears_{el}.png"),
        dpi=600,
        bbox_inches='tight',
        pad_inches=0.2
    )
    print("Saved figure to:", output_path)

    plt.show()


if __name__ == "__main__":
    df_dict, df_decarb = load_data()
    df_cb_cityprov, df_lcce_cityprov = load_cityprov_data(file_path_cityprov)
    plot_combined_two_diagrams(df_dict, df_decarb, df_cb_cityprov, df_lcce_cityprov)
