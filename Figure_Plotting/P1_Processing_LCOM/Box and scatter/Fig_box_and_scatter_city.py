import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from collections import OrderedDict
import matplotlib as mpl

mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['font.sans-serif'] = ['Arial']
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.rm'] = 'Arial'
mpl.rcParams['mathtext.it'] = 'Arial:italic'
mpl.rcParams['mathtext.bf'] = 'Arial:bold'



mode       = 'SOE' 

year_ei_levels = {
    'PEM': {
        2030: ['25%', '50%', '75%', '100%'],
        2040: ['25%', '55%', '75%', '100%'],
        2050: ['25%', '50%', '76%', '100%'],
    },
    'SOE': {
        2030: ['25%', '50%', '75%', '100%'],
        2040: ['21%',  '50%', '75%', '100%'],
        2050: ['25%', '59%', '75%', '100%'],
    }
}
years      = sorted(year_ei_levels[mode].keys())      
EI_levels  = [ei.rstrip('%') for year in years for ei in year_ei_levels[mode][year]]
 
base_dir = rf"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Results_M12_0812\{mode}"
save_dir = r"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Box and scatter"
os.makedirs(save_dir, exist_ok=True)
merged_file = os.path.join(base_dir, f"Collected_LCOM_results_{mode}.xlsx")
excel = pd.ExcelFile(merged_file)

all_data = []

for year in years:
    for ei_pct in year_ei_levels[mode][year]:
        ei = ei_pct.rstrip('%')   
        sheet_name = f"{year}_{mode}_ED{ei}"

        if sheet_name not in excel.sheet_names:
            print(f"Missing sheet: {sheet_name}")
            continue

        df = excel.parse(sheet_name)
        df = df.rename(columns={
            df.columns[0]: 'Province',
            df.columns[1]: 'City',
            df.columns[2]: 'Value'
        })

        df['LCOM'] = df['Value']
        df['Year'] = str(year)
        df['Group'] = f"{year}\n{ei}%"   
        df = df[['Province','LCOM','Year','Group']]

        all_data.append(df)

df_all = pd.concat(all_data, ignore_index=True)

sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(10, 10))
ax.grid(False)

groups = df_all['Group'].unique().tolist()  
df_all['x_pos'] = df_all['Group'].map({g:i for i,g in enumerate(groups)})

hex_colors = ["#FFCC79", "#F99735", "#E96812"] 

palette = dict(zip([str(y) for y in years], hex_colors))

box_data = [df_all.loc[df_all['Group']==grp, 'LCOM'].values
            for grp in groups]
positions = list(range(len(groups)))


bp = ax.boxplot(
    box_data,
    positions=positions,
    widths=0.3,
    showfliers=False,
    whis=[5, 95],
    patch_artist=True,
)

for idx, box in enumerate(bp['boxes']):
    grp = groups[idx]
    if grp == '':
        continue
    year = grp.split('\n')[0]
    col = palette[year]
    box.set_facecolor(col)
    box.set_alpha(0.7)
    box.set_edgecolor('black')
    box.set_linewidth(1)

for part in ['whiskers','caps','medians']:
    for artist in bp[part]:
        artist.set_color('black')
        artist.set_linewidth(1)


for i, grp in enumerate(groups):
    sub = df_all[df_all['Group']==grp]
    for yr, col in palette.items():
        y = sub.loc[sub['Year']==yr, 'LCOM'].values
        if len(y)==0: continue
        x = np.random.normal(loc=i-0.3, scale=0.08, size=len(y))
        ax.scatter(x, y, color=col, alpha=0.6, s=18, edgecolors='none')


summary_wb = pd.ExcelFile(
     os.path.join(base_dir, f"ED{EI_levels[0]}", f"LCOM_{mode}_ED{EI_levels[0]}.xlsx")
 ) 
coal_vals  = {str(year): {} for year in years}
state_vals = {str(year): {} for year in years}

for year in years:
     for ei_pct in year_ei_levels[mode][year]:
         ei = ei_pct.rstrip('%')
         summary_file = os.path.join(
             base_dir,
             f"ED{ei}",
             f"LCOM_{mode}_ED{ei}.xlsx"
         )
         wb = pd.ExcelFile(summary_file)
         df_sum = wb.parse(f"{year}_LCOM", index_col=0)
         coal_vals[str(year)][ei]  = df_sum.loc['Coal_LCOM',  'Value']
         state_vals[str(year)][ei] = df_sum.loc['State_LCOM','Value']
for idx, grp in enumerate(groups):
    year, ei = grp.split('\n')
    ei = ei.rstrip('%')               
    x0 = positions[idx]
    y_coal  = coal_vals[year][ei]      
    y_state = state_vals[year][ei]
    ax.scatter(x0, y_coal,
               color='black', marker='s', s=40, zorder=20,
               label='Coal LCOM' if idx==0 else "")
    ax.scatter(x0, y_state,
               facecolors='white', edgecolors='black',
               marker='D', s=80, zorder=20,
               label='Nation LCOM' if idx==0 else "")    

offset = 0
ylim = ax.get_ylim()
for year in years:
    eis = year_ei_levels[mode][year]
    n = len(eis)
    xs = positions[offset:offset+n]
    center = (xs[0] + xs[-1]) / 2
    ax.text(center, ylim[0] - 0.14*(ylim[1]-ylim[0]),
            str(year), ha='center', va='top',
            fontsize=24, fontweight='bold')
    offset += n



legend_handles = [
    Line2D([], [], marker='o', color='black', linestyle='None',
           markersize=6, label='Data'),
    Patch(facecolor='lightgray', edgecolor='black', alpha=0.7,
          label='Box: 25%–75%'),
    Line2D([], [], color='black', linewidth=1,
           label='Whisker: 5%–95%'),
    Line2D([], [], marker='s', color='black', linestyle='None',
           markersize=6, label='Coal LCOM'),
    Line2D([], [], marker='D', markerfacecolor='white', markeredgecolor='black',
           linestyle='None', markersize=8, label='National LCOM'),
]

ax.legend(handles=legend_handles,
          loc='upper right',
          fontsize=22,
          frameon=False)

ax.set_ylabel("LCOM (2025 USD/ton)", fontsize=24)
ax.tick_params(axis='y', labelsize=22)
ax.set_xlabel("")
ax.set_xlim(-0.8, positions[-1] + 0.8)

                           
                         
                                                                    
real_positions = [i for i, g in enumerate(groups) if g]  
ax.set_xticks(real_positions)
ax.set_xticklabels([])
ax.tick_params(axis='x',
                which='major',
                bottom=True, top=False,
                direction='in',
                length=6)
ax.tick_params(axis='y', which='major', left=True, right=False, direction='in', length=6)
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.5)

unique_groups = df_all['Group'].unique().tolist()
ei_labels = [g.split('\n')[1] for g in unique_groups]

ylim = ax.get_ylim()
for idx, grp in enumerate(groups):
    if not grp: 
        continue
    ei = grp.split('\n')[1]
    ax.text(idx, ylim[0] - 0.02*(ylim[1]-ylim[0]),
            ei, ha='center', va='top',rotation=90, fontsize=22)

n_ei = len(EI_levels)
for year in years:
    idxs = [i for i, g in enumerate(groups) if g.startswith(str(year))]
    if not idxs:
        continue
    center = (idxs[0] + idxs[-1]) / 2
    ax.text(center, ylim[0] - 0.14*(ylim[1]-ylim[0]),
            str(year), ha='center', va='top', fontsize=24, fontweight='bold')

plt.tight_layout()

png_path = os.path.join(save_dir, f"{mode}_LCOM_C_BoxScatter.png")
pdf_path = os.path.join(save_dir, f"{mode}_LCOM_C_BoxScatter.pdf")

plt.savefig(png_path, dpi=300)
plt.savefig(pdf_path)
print(f"saved: \n{png_path}\n{pdf_path}")

plt.show()
