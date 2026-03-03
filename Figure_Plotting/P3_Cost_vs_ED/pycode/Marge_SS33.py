import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as mticker  # 确保开头导入了这个模块
import matplotlib.patches as mpatches
import re
from matplotlib.ticker import MultipleLocator

plt.rcParams['axes.linewidth'] = 1.5  # 坐标轴边框宽度

# —————— 用户配置 ——————
base_dir = r"F:/2025_Methanol_synthesis/3_GAMS/P2_Cost_vs_ED"
# 各电解槽类型 EI 水平
year_ei_levels = {
    'PEM': {
        2030: ['25%', '100%'],
        2040: ['25%', '100%'],
        2050: ['25%', '100%'],
    },
    'SOE': {
        2030: ['25%', '100%'],
        2040: ['25%', '100%'],
        2050: ['25%', '100%'],
    }
}
# 颜色映射
color_map = {
    'Coal': "#4B4B4BDB", 'OM_coal': "#9F9F9F", 'OM_Msyn': '#607D8B',
    'CO2e':"#E8DADA", 'CO2c':"#C0C6DE", 'CO2p':"#D3DAB8", 
    'Grid': '#FFEB3B', 'PV_CAP': '#FF9800',
    'PV_OM': "#FFB74B", 'WT_CAP': '#8BC34A', 'WT_OM': '#DCEDC8', 'TNS': "#A9EBE9", 
    'SOE_CAP': '#E91E63', 'SOE_OM': '#F8BBD0', 'PEM_CAP': '#FE6F37',
    'PEM_OM': '#FF966C', 'Lib_CAP':"#399988",'Lib_OM':"#44E8CA",'HST_CAP': '#55D6C9', 'HST_OM': '#B9FFF8',
    'SST_CAP': '#673AB7', 'SST_OM': '#D1C4E9', 
    'RWS_CAP': "#BC6400",    'RWS_OM': "#C08C51", 'H2O': '#E2F6FF', 'O2': "#0BAEC4",
}
category_order = list(color_map.keys())
x_spacing_scale = 1.0

# 数据加载
def _sf(x):
    try:
        if isinstance(x, str):
            x = x.replace(',', '').strip()
        return float(x)
    except Exception:
        return np.nan

def load_data(el):
    file_path = os.path.join(base_dir, 'pycode', el, 'bar_allyears', 'Supplementary_CityProv.xlsx')
    df_cb, df_lcce = {}, {}
    for year in year_ei_levels[el]:          # 2030/2040/2050
        cb_parts = []
        lcce_dict = {}

        for ei_str in year_ei_levels[el][year]:   # ['25%','100%']
            ei = ei_str.rstrip('%')               # '25' / '100'

            # —— CB：{year}_ED{ei}_CB，取 City/Prov/State 三列 → 重命名为 C{ei}/P{ei}/S{ei}
            cb_sheet = f"{year}_ED{ei}_CB"
            tmp = pd.read_excel(file_path, sheet_name=cb_sheet, index_col=0).fillna(0) / 1e6
            cb_parts.append(tmp[['City','Prov','State']].rename(columns={
                'City': f'City{ei}', 'Prov': f'Prov{ei}', 'State': f'State{ei}'
            }))

            # —— LCCE：{year}_ED{ei}_LCCE，稳健读取 City/Prov/State
            lc_sheet = f"{year}_ED{ei}_LCCE"
            t = pd.read_excel(file_path, sheet_name=lc_sheet, header=0)
            t.columns = [str(c).strip() for c in t.columns]  # 去空格
            rename_map = {'city':'City','prov':'Prov','state':'State',
                        '城市':'City','省':'Prov','州':'State'}
            t = t.rename(columns={c: rename_map.get(str(c).strip().lower(), c) for c in t.columns})

            if {'City','Prov','State'}.issubset(t.columns):
                # 固定取第二列（iloc[1]），若不足两行则取最后一行
                row_idx = 1 if len(t) > 1 else len(t)-1
                row = t.iloc[row_idx]
                lcce_dict[f'City{ei}'] = _sf(row['City'])
                lcce_dict[f'Prov{ei}'] = _sf(row['Prov'])
                lcce_dict[f'State{ei}'] = _sf(row['State'])
            else:
                # 回退：索引为 City/Prov/State 格式
                t2 = pd.read_excel(file_path, sheet_name=lc_sheet, index_col=0)
                t2.index = [str(i).strip() for i in t2.index]
                col = 'VALUE' if 'VALUE' in t2.columns else t2.columns[0]
                lcce_dict[f'City{ei}'] = _sf(t2.loc['City', col])
                lcce_dict[f'Prov{ei}'] = _sf(t2.loc['Prov', col])
                lcce_dict[f'State{ei}'] = _sf(t2.loc['State', col])



        df_cb[year] = pd.concat(cb_parts, axis=1)   # 列顺序：C25 P25 S25 C100 P100 S100
        df_lcce[year] = lcce_dict                   # 字典：{列名: 数值}

    return df_cb, df_lcce


# 绘制函数：接受传入的 ax1, ax2

def plot_combined(el, df_cb, df_lcce, ax1, ax2=None):
    ax1b = ax1.twinx()
    # —— LHS ——
    width = 0.6
    x_labels, x_map, x_pos = [], {}, 0
    y1p, y1n, y2p, y2n = -np.inf, np.inf, -np.inf, np.inf
    for i, year in enumerate(year_ei_levels[el]):
        ei_list = [e.rstrip('%') for e in year_ei_levels[el][year]]   # ['25','100']
        labels = [f'{r}{ei}' for ei in ei_list for r in ['City','Prov','State']]
        df, lc = df_cb[year], df_lcce[year]
        for j, lab in enumerate(labels):
            x_labels.append(lab)
            x_map[(year, lab)] = x_pos
            bp, bn, tot = 0, 0, 0
            for cat in category_order:
                if cat in df.index and lab in df.columns:
                    v = df.loc[cat, lab]; tot += v
                    base = bp if v >= 0 else bn
                    ax1.bar(x_pos, v, width, bottom=base, color=color_map[cat],
                            label=cat if (i, j) == (0, 1) else '')
                    if v >= 0:
                        bp += v; y1p = max(y1p, bp)
                    else:
                        bn += v; y1n = min(y1n, bn)
            ax1.scatter(x_pos, tot, color="#33720EFF", s=30, marker='s', zorder=10,
                        label='Total cost' if (i, j) == (0, 1) else '')
            # …… 在 plot_combined 内，对 LCCE 部分做如下替换 ———
            val = df_lcce[year].get(lab, np.nan)
            num = float(val) if pd.notna(val) else np.nan

            if np.isfinite(num):
                ax1b.scatter(x_pos, num, color='blue', s=30, zorder=10,
                            label='Decarbonization cost' if (i, j) == (0, 1) else '')
                ax1b.text(x_pos, num + 15, f"{num:.1f}", ha='center', va='bottom', color='blue')
                y2p = max(y2p, num); y2n = min(y2n, num)
            else:
                y1_lim = ax1.get_ylim()[1]
                ax1b.text(x_pos+0.01, y1_lim * 6.0, "Infeas.",
                        ha='center', va='bottom', color='blue', fontsize=14)

                
            x_pos += x_spacing_scale
        x_labels.append(''); x_pos += x_spacing_scale
    # 设置坐标
    x_labels = x_labels[:-1]
    ax1.set_ylim(
        y1n * 1.15 if y1n < 0 else 0,
        y1p * 1.15
    )
    ax1.set_ylabel("TAC (Billion 2025 USD)", fontsize=20)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=16)

    ax1b.set_ylabel("LCCR (2025 USD/ton CO₂)", fontsize=20, color='blue')
    ax1b.tick_params(axis='y', labelcolor='blue', labelsize=16)

    ax1.set_xticks(range(len(x_labels)))
    ax1b.yaxis.set_major_locator(MultipleLocator(25))   # 每 25 一个刻度

    tick_lbls = []
    for s in x_labels:
        if not s:
            tick_lbls.append('')
            continue
        base = re.sub(r'\d+', '', s)  # 去掉数字，得到 City / Prov / State
        if base == 'State':
            base = 'Nation'           # 只在显示层面改成 Nation
        tick_lbls.append(base)
    ax1.set_xticklabels(tick_lbls, rotation=90, fontsize=16, ha='center')


    # 在每组三个柱(C,P,S)下方居中标注 EI（25%/100%）
    group_size = 3
    per_year = 6 + 1   # 6个标签 + 1个空位
    for i, year in enumerate(year_ei_levels[el]):     # 2030/2040/2050
        ei_list = [e.rstrip('%') for e in year_ei_levels[el][year]]  # ['25','100']
        base = i * per_year
        for k, ei in enumerate(ei_list):              # k=0→25, k=1→100
            mid = base + k * group_size + 1           # C,P,S 的中点
            ax1.text(mid, -0.102, f"{ei}%",
                    transform=ax1.get_xaxis_transform(),  # x 用数据坐标，y 用轴坐标
                    ha='center', va='top', fontsize=15, fontweight='bold')

    # 添加年份标注
    fig = ax1.get_figure()
    fig.text(0.263, 0.06, "2030", ha='center', va='top', fontsize=18, fontweight='bold')
    fig.text(0.513, 0.06, "2040", ha='center', va='top', fontsize=18, fontweight='bold')
    fig.text(0.768, 0.06, "2050", ha='center', va='top', fontsize=18, fontweight='bold')


    ax1b.set_ylim(
        y2n * 1.3 if y2n < 0 else 0,
        y2p * 1.3
    )
    ax1b.yaxis.set_major_locator(MultipleLocator(50))


    if el == 'PEM':
        # 图例
        legend_name_map = {
            'O2': 'O₂ revenue',
            'Total cost': 'TAC',
            'Decarbonization cost': 'LCCR',
            'OM_coal': 'Coal processing O&M',
            'OM_Msyn': 'Methanol synthesis O&M',
            'Grid': 'Electricity purchase',
            'PV_CAP': 'PV CapEx',
            'PV_OM': 'PV O&M',
            'WT_CAP': 'WT CapEx',
            'WT_OM': 'WT O&M',
            'Lib_CAP': 'LiB CapEx',
            'Lib_OM': 'LiB O&M',
            'SOE_CAP': 'SOEC CapEx',
            'SOE_OM': 'SOEC O&M',
            'PEM_CAP': 'PEME CapEx',
            'PEM_OM': 'PEME O&M',
            'RWS_CAP': 'RWGS CapEx',
            'RWS_OM': 'RWGS O&M',
            'HST_CAP': 'HST CapEx',
            'HST_OM': 'HST O&M',
            'SST_CAP': 'SST CapEx',
            'SST_OM': 'SST O&M',
            'H2O': 'Water consumption',
            'TNS': 'Transmission O&M',
            'Coal': 'Raw coal consumption',
            'CO2e':'Carbon emission',
            'CO2p':'Carbon purchase',
            'CO2c':'Carbon capture'           
        }

        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax1b.get_legend_handles_labels()

        blue_handle = None
        for h, l in zip(handles1, labels1):
            if l == 'Total cost':
                blue_handle = h
                break
        handles1 = [h for h, l in zip(handles1, labels1) if l != 'Total cost']
        labels1 = [l for l in labels1 if l != 'Total cost']

        manual_legend_keys = ['SOE_CAP', 'SOE_OM', 'SST_CAP', 'SST_OM','Lib_CAP','Lib_OM']
        manual_handles = [mpatches.Patch(color=color_map[k], label=k) for k in manual_legend_keys]
        manual_labels = manual_legend_keys

        handles = handles1 + manual_handles + handles2 + [blue_handle]
        labels = labels1 + manual_labels + labels2 + ['Total cost']
        labels = [legend_name_map.get(l, l) for l in labels]
        uniq = dict(zip(labels, handles))

        ax1.legend(uniq.values(), uniq.keys(), loc='upper center',
                ncol=6, bbox_to_anchor=(0.5, 1.28), frameon=False, fontsize=14  )


if __name__ == '__main__':
    # 将右侧对比图删掉，只保留主图（TAC + LCCR）
    fig, axes = plt.subplots(2, 1, figsize=(18, 18), sharey='row',
                             gridspec_kw={'hspace': 0.10, 'wspace': 0.2})  # <<< 修改：改为 2x1
    for i, el in enumerate(['PEM', 'SOE']):
        df_cb, df_lcce = load_data(el)
        # df_cb_cp, df_lcce_cp = load_cityprov_data(el)  # <<< 删除：不再加载 City/Prov 数据
        ax = axes[i]  # <<< 修改：只取一个 ax
        plot_combined(el, df_cb, df_lcce, ax)
    # —— 保存图片 ——  
    output_path = os.path.join(base_dir, 'Figure', 'Suppli.png')
    fig.savefig(output_path, dpi=1000, bbox_inches='tight', pad_inches=0.2)
    print(f"Saved figure to {output_path}")

