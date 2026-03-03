import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as mticker               
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator

plt.rcParams['axes.linewidth'] = 1.5           

                    
base_dir = r"E:/2025_Methanol_synthesis/3_GAMS/P2_Cost_vs_ED"
              
year_ei_levels = {
    'PEM': {
        2030: ['25%', '50%', '75%', '100%'],
        2040: ['25%', '55%', '75%', '100%'],
        2050: ['25%', '50%', '76%', '100%'],
    },
    'SOE': {
        2030: ['25%', '50%', '75%', '100%'],
        2040: ['21%', '50%', '75%', '100%'],
        2050: ['25%', '59%', '75%', '100%'],
    }
}
      
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

      

def load_data(el):
    file_path = os.path.join(base_dir, 'pycode', el, 'bar_allyears', 'merged_CB_UE_NEW.xlsx')
    df_cb, df_lcce = {}, {}
    for year in year_ei_levels[el]:
        df_cb[year] = pd.read_excel(file_path, sheet_name=f"{year}_CB", index_col=0, engine="openpyxl").fillna(0) / 1e6
        df_lcce[year] = pd.read_excel(file_path, sheet_name=f"{year}_LCCE", index_col=0, engine="openpyxl")
    return df_cb, df_lcce


def load_cityprov_data(el):
    file_path = os.path.join(base_dir, 'pycode', el, 'bar_allyears', 'merged_CB_CityProv.xlsx')
    df_cb, df_lcce = {}, {}
    for year in ['2040', '2050']:
        df_cb_all = pd.read_excel(file_path, sheet_name=f"{year}_CB", index_col=0, engine="openpyxl").fillna(0) / 1e6
        df_lcce_all = pd.read_excel(file_path, sheet_name=f"{year}_LCCE", index_col=0, engine="openpyxl")
        for region in ['City', 'Prov']:
            df_cb[f"{year}_{region.lower()}"] = df_cb_all[[region]]
            df_lcce[f"{year}_{region.lower()}"] = df_lcce_all.loc[[region]]
    return df_cb, df_lcce

                     

def plot_combined(el, df_cb, df_lcce, df_cb_cp, df_lcce_cp, ax1, ax2):
    ax1b = ax1.twinx()
    ax2b = ax2.twinx()
               
    width = 0.6
    x_labels, x_map, x_pos = [], {}, 0
    y1p, y1n, y2p, y2n = -np.inf, np.inf, -np.inf, np.inf
    for i, year in enumerate(year_ei_levels[el]):
        labels = ['BAU'] + year_ei_levels[el][year]
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
                                                     

            if lab != 'BAU':
                ei = int(lab.replace('%', ''))
                try:
                    val = lc.loc[ei, 'VALUE']
                    num = float(val)
                    ax1b.scatter(x_pos, num, color='blue', s=30, zorder=10,
                                label='Decarbonization cost' if (i, j) == (0, 1) else '')
                    ax1b.text(x_pos, num + 4 , f"{num:.1f}", ha='center', va='bottom', color='blue')
                    y2p = max(y2p, num); y2n = min(y2n, num)
                except (ValueError, TypeError):
                                                
                    y1_lim = ax1.get_ylim()[1]
                                   
                    ax1b.text(x_pos+0.01, y1_lim * 0.13, "Infeas.",
                            ha='center', va='bottom', color='blue', fontsize=14)
                except KeyError:
                    pass

            x_pos += x_spacing_scale
        x_labels.append(''); x_pos += x_spacing_scale
          
    x_labels = x_labels[:-1]
    ax1.set_ylim(
        y1n * 1.15 if y1n < 0 else 0,
        y1p * 1.15
    )
    ax1.set_ylabel("TAC (Billion 2025 USD)", fontsize=20)
    ax1.tick_params(axis='y', labelcolor='black', labelsize=16)

    ax1b.set_ylabel("LCCR (2025 USD/ton CO₂)", fontsize=20, color='blue')
    ax1b.tick_params(axis='y', labelcolor='blue', labelsize=16)
    ax1b.yaxis.set_major_locator(MultipleLocator(25))              

    ax1.set_xticks(range(len(x_labels)))
    ax1.set_xticklabels(x_labels, rotation=90, fontsize=16)

            
    fig = ax1.get_figure()
    fig.text(0.205, 0.06, "2030", ha='center', va='top', fontsize=16, fontweight='bold')
    fig.text(0.36, 0.06, "2040", ha='center', va='top', fontsize=16, fontweight='bold')
    fig.text(0.51, 0.06, "2050", ha='center', va='top', fontsize=16, fontweight='bold')


    ax1b.set_ylim(
        y2n * 1.3 if y2n < 0 else 0,
        y2p * 1.3
    )
               
    tags = list(df_cb_cp.keys())
    tag_labels = ["City", "Prov", "City", "Prov"]

    x_locs = [0, 1, 2.2, 3.2]
    y3p, y3n = -np.inf, np.inf
    y4p, y4n = -np.inf, np.inf

    for tag, x in zip(tags, x_locs):
        df2, lc2 = df_cb_cp[tag], df_lcce_cp[tag]
        bp, bn = 0, 0
        for cat in category_order:
            if cat in df2.index:
                v = df2.loc[cat].values[0]; base = bp if v >= 0 else bn
                ax2.bar(x, v, 0.6, bottom=base, color=color_map[cat])
                if v >= 0: bp += v
                else: bn += v
        ax2.scatter(x, bp + bn, color='#33720EFF', s=30, marker='s')

        try:
            val = lc2.loc[tag.split('_')[1].capitalize()].values[0]
            num = float(val)
            ax2b.scatter(x, num, color='blue', s=30)
            ax2b.text(x, num + 1, f"{num:.1f}", ha='center', va='bottom', color='blue')
            y4p = max(y4p, num); y4n = min(y4n, num)
        except (ValueError, TypeError):
            y2_lim = ax2.get_ylim()[1]
            ax2b.text(x+0.1, y2_lim * 0.03, "Infeas.", ha='center', va='bottom', color='blue', fontsize=14)
        except KeyError:
            pass

    ax2.set_xticks(x_locs)
    ax2.set_xticklabels(tag_labels, rotation=90, fontsize=16)
    ax2.set_ylabel("TAC (Billion 2025 USD)", fontsize=20)
    ax2.yaxis.set_tick_params(labelleft=True)
    ax2.spines['left'].set_visible(True)
    ax2.tick_params(axis='y', labelcolor='black', labelsize=16)
    ax2b.set_ylabel("LCCR (2025 USD/ton CO₂)", fontsize=20, color='blue')
    ax2b.tick_params(axis='y', labelcolor='blue', labelsize=16)
    ax2b.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))

              
    fig.text(0.782, 0.06, "2040", ha='center', va='top', fontsize=16, fontweight='bold')
    fig.text(0.865, 0.06, "2050", ha='center', va='top', fontsize=16, fontweight='bold')
    ax2b.set_ylim(
    y4n * 1.2 if y4n < 0 else 0,
    y4p * 1.6
    )


    if el == 'PEM':
            
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
                ncol=6, bbox_to_anchor=(0.85, 1.32), frameon=False, fontsize=14  )


if __name__ == '__main__':
    fig, axes = plt.subplots(2, 2, figsize=(18, 15), sharey='row',
                             gridspec_kw={'width_ratios': [12, 4], 'hspace': 0.15, 'wspace': 0.5})
    for i, el in enumerate(['PEM', 'SOE']):
        df_cb, df_lcce = load_data(el)
        df_cb_cp, df_lcce_cp = load_cityprov_data(el)
        ax1, ax2 = axes[i]
        plot_combined(el, df_cb, df_lcce, df_cb_cp, df_lcce_cp, ax1, ax2)
    plt.tight_layout()

                  
    output_path = os.path.join(base_dir, 'Figure', 'PEM_and_SOE_comparison.png')
    fig.savefig(output_path, dpi=1000, bbox_inches='tight', pad_inches=0.2)
    print(f"Saved figure to {output_path}")

    plt.show()

