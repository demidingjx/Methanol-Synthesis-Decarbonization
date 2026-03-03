import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from PIL import Image

                    
color_map = {
    2030: ("#C16E71", "#DDAEAB"),
    2040: ("#6E8FB2", "#B5C3D7"),
    2050: ("#7DA494", "#6C9C90")
}
TITLE_FS   = 18                 
TICK_FS    = 14            
ANNOT_FS   = 20           
LEGEND_FS  = 20          

                      
province_abbr = {
    "Anhui": "AH", "Gansu": "GS", "Guangxi": "GX", "Guizhou": "GZ",
    "Hainan": "HI", "Hebei": "HB", "Henan": "HN", "Heilongjiang": "HL",
    "Hubei": "HU", "Jilin": "JL", "Jiangsu": "JS", "Jiangxi": "JX",
    "Liaoning": "LN", "E_InnerMongo": "EIM", "W_InnerMongo": "WIM",
    "Ningxia": "NX", "Qinghai": "QH", "Shandong": "SD", "Shanxi": "SN",
    "Shaanxi": "SX", "Shanghai": "SH", "Sichuan": "SC", "Tianjin": "TJ",
    "Sinkiang": "XJ", "Yunnan": "YN", "Zhejiang": "ZJ", "Chongqing": "CQ"
}

                            
sheet_names = {
    2030: {'line': '2030_LCOM',   'prov': '2030_Prov_LCOM_j', 'city': '2030_City_LCOM_j'},
    2040: {'line': '2040_LCOM',   'prov': '2040_Prov_LCOM_j', 'city': '2040_City_LCOM_j'},
    2050: {'line': '2050_LCOM',   'prov': '2050_Prov_LCOM_j', 'city': '2050_City_LCOM_j'}
}

def plot_all(EL):
    years = [2030, 2040, 2050]
    eds   = [25, 50, 75, 100]
    
                  
    fig, axes = plt.subplots(
        nrows=len(years), ncols=len(eds),
        figsize=(4*len(eds), 7*len(years)),
        sharey=True,
        gridspec_kw={'hspace': 0.07, 'wspace': 0.0}
    )

                      
    for ax_row in axes[:, 1:]:
        for ax in ax_row:
            ax.yaxis.set_tick_params(labelleft=False)

                         
    xls_cache = {}

    for i, year in enumerate(years):
        for j, ed in enumerate(eds):
            ax = axes[i, j]

            if i == 0:
                ax.set_title(f"EI = {ed}%", fontsize=TITLE_FS + 2)

            color_A, color_B = color_map[year]
            color_coal = 'grey'
            
                      
            if ed not in xls_cache:
                path = fr"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Results_M12_0812\{EL}\ED{ed}\LCOM_{EL}_ED{ed}.xlsx"
                xls_cache[ed] = pd.ExcelFile(path)
            xls = xls_cache[ed]

                 
            df_line = pd.read_excel(xls, sheet_name=sheet_names[year]['line'])
            df_prov = pd.read_excel(xls, sheet_name=sheet_names[year]['prov'])
            df_city = pd.read_excel(xls, sheet_name=sheet_names[year]['city'])
            
                    
            df_prov['Prov_LCOM_j'] = df_prov['Prov_LCOM_j'].map(province_abbr).fillna(df_prov['Prov_LCOM_j'])
            df_city['City_LCOM_j'] = df_city['City_LCOM_j'].map(province_abbr).fillna(df_city['City_LCOM_j'])

                      
            provinces = sorted(set(df_prov['Prov_LCOM_j']) | set(df_city['City_LCOM_j']))
            ax.set_yticks(range(len(provinces)))
            ax.set_yticklabels(provinces, fontsize=TICK_FS)

                  
            for lvl, style in [
                ('Coal_LCOM', '--'),
                ('State_LCOM', '-'),
                                      
                                    
            ]:
                val = df_line.loc[df_line['Levelized_cost'] == lvl, 'Value'].values[0]
                c = color_coal if lvl == 'Coal_LCOM' else color_A
                ax.axvline(val, color=c, linestyle=style, linewidth=2.5)

                
            prov_x = df_prov['Value'].values
            prov_y = [provinces.index(p) for p in df_prov['Prov_LCOM_j']]
            city_x = df_city['Value'].values
            city_y = [provinces.index(p) for p in df_city['City_LCOM_j']]

            ax.scatter(city_x, city_y, color=color_A, marker='s', s=80)
            ax.scatter(prov_x, prov_y, facecolors=color_B, edgecolors=color_A, marker='o', s=80)

                  
            def draw_hull(xs, ys, fc):
                if len(xs) >= 3:
                    pts = np.column_stack((xs, ys))
                    hull = ConvexHull(pts)
                    poly = Polygon(pts[hull.vertices], closed=True, facecolor=fc, alpha=0.1)
                    ax.add_patch(poly)

            draw_hull(city_x, city_y, color_B)
            draw_hull(prov_x, prov_y, color_A)
                           
            all_x = np.concatenate([
                prov_x, city_x,
                df_line.loc[df_line['Levelized_cost']
                            .isin(['Coal_LCOM','State_LCOM','Prov_LCOM','City_LCOM']), 'Value'].values
            ])

                 
            all_x = all_x[all_x != 0]

            mn, mx = all_x.min(), all_x.max()
            margin = (mx - mn) * 0.36
            x_min = max(mn - margin, 120)
            x_max = mx + margin
            ax.set_xlim(x_min, x_max)
                         
            ax.margins(x=0.02)

                                   
            ticks = ax.get_xticks()
            if len(ticks) >= 2:
                diffs = np.diff(ticks)
                avg = np.median(diffs)
                if diffs[-1] < 0.5 * avg:
                    ax.set_xticks(ticks[:-1])

                           
            ax.tick_params(axis='both', labelsize=TICK_FS, direction='in')


                     
        axes[i, 0].annotate(
            f"{year}",
            xy=(-0.15, 0.5),
            xycoords='axes fraction',
            ha='right', va='center',
            fontsize=ANNOT_FS, rotation=90
        )

          
    legend_elements = [
        Line2D([0], [0], color='grey', linestyle='--', label='BAU'),
        Line2D([0], [0], color='k', linestyle='-',   label='National integration'),
                                                                    
                                                                    
        Line2D([0], [0], marker='o', color='k', markerfacecolor='w',
               linestyle='None', markersize=8, label='Provincial integration'),
        Line2D([0], [0], marker='s', color='k',
               linestyle='None', markersize=8, label='Municipal integration'),
    ]
    fig.legend(
        handles=legend_elements,
        loc='upper center',
        bbox_to_anchor=(0.505, 0.97),                  
        ncol=len(legend_elements),
        frameon=False,
        fontsize=LEGEND_FS
    )
               
    plt.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.05)
    fig.text(0.5, 0.02, "LCOM (2025 USD/ton)", ha='center', fontsize=TITLE_FS + 2)        
    outpath = fr"E:\2025_Methanol_synthesis\3_GAMS\P1_Processing_LCOM\Processing\LCOM_{EL}_Grid.png"
    fig.savefig(outpath, dpi=600, bbox_inches='tight')
    plt.close(fig)
    print(f"save: {outpath}")
    plt.show()

if __name__ == "__main__":
    plot_all("SOE")            
