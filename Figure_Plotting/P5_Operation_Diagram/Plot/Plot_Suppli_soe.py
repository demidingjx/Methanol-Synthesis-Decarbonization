import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter


plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'

base = r"E:\2025_Methanol_synthesis\3_GAMS\P5_Operation_Diagram\Excel"
EN_colors = {
    "PEM": "#254750",            
    "SOE": "#E07400"                 
}

months = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

scenarios = [
    ("SOE", 2040, "25"),
    ("SOE", 2040, "100"),
    ("SOE", 2050, "25"),
    ("SOE", 2050, "100"),
]


h = np.arange(1, 25)

                                                             
figw, figh = 28 / 2.54, 18*2 / 2.54
fig, ax = plt.subplots(nrows=4, ncols=12, figsize=(figw, figh),
                       sharex=True, sharey=False)

for row, (mode, year, ED) in enumerate(scenarios):
    if mode == "PEM":
        chg_col = "Hour_ChgP_HST_Value"
        dis_col = "Hour_DisP_HST_Value"
        EN_col  = "Hour_EN_HST_Value"
        storage_label = "HST"
    elif mode == "SOE":
        chg_col = "Hour_ChgP_SST_Value"
        dis_col = "Hour_DisP_SST_Value"
        EN_col  = "Hour_EN_SST_Value"
        storage_label = "SST"
    row_max = 0.0

    EN_color = EN_colors[mode]
                                          
    file = fr"{base}\SplitByMonthSOE_{year}_ED{ED}.xlsx"
    for m in range(12):
                            
        a = ax[row, m]                                 
        if m == 0:
                            
            a.set_ylabel(f"{year}, EI={ED}%", fontsize=10)
        df = pd.read_excel(file, sheet_name=m, header=0)

        PV   = df["Hour_PV_Value"].fillna(0).to_numpy()
        WT   = df["Hour_WT_Value"].fillna(0).to_numpy()
        Grid = df["Hour_Grid_Value"].fillna(0).to_numpy()
        ChgS = df[chg_col].fillna(0).to_numpy()
        DisS = df[dis_col].fillna(0).to_numpy()
        EnS = df[EN_col].fillna(0).to_numpy()
        EL   = df["Hour_EL_Value"].fillna(0).to_numpy()
        MeOH = df["Hour_MeOH_Value"].fillna(0).to_numpy()
        MeOH_coal = df["MeOH_coal_hr_Value"].fillna(0).to_numpy()
        LCOM_Hr = df["LCOM_Hr_Value"].fillna(0).to_numpy()


        stack_max = (df["Hour_PV_Value"]+df["Hour_WT_Value"]+df["Hour_Grid_Value"]).max()
        line_maxs = [
            df["Hour_EN_SST_Value"].max(),
            df["Hour_EL_Value"].max(),
            df["MeOH_coal_hr_Value"].max(),
            df["Hour_MeOH_Value"].max()
        ]
        row_max = max(row_max, stack_max, *line_maxs)

        a = ax[row, m]
        a2 = a.twinx()
        

        if row == 0:
            a.set_title(months[m], fontsize=10, pad=3)

        a.set_xlim(1, 24)
        a.margins(x=0)
        a.set_xticks([1, 8, 16, 24])

        colors = ["#f5d44b", "#afcfa6", "#8b8b8b"]
        l_stack = a.stackplot(h, PV, WT, Grid, colors=colors)

                                                     
        l_EN, = a.plot(h, EnS, color=EN_color, linestyle="dotted")
        l_EL, = a.plot(h, EL, color="#2F601E")
        l_MeOHcoal, = a.plot(h, MeOH_coal, color="#000000", linestyle="dashed")
        l_MeOH, = a.plot(h, MeOH, color="#002aff", linestyle="dashed")
        l_LCOM, = a2.plot(h, LCOM_Hr, color="#189C93")

        a2.yaxis.set_major_formatter(FormatStrFormatter('%.3g'))

        if m != 11:
            a2.set_yticks([])
            a2.set_ylabel("")
        else:
            a2.tick_params(axis="y", labelsize=10)
    
    top = row_max * 1.1 
    for subax in ax[row, :]:
        subax.set_ylim(0, top)



                                   
for row in range(ax.shape[0]):
    for col in range(1, ax.shape[1]):
        ax[row, col].tick_params(
            labelleft=False,                     
            left=True                     
        )
        ax[row, col].spines["left"].set_visible(True)


                             
l_EN_HST = Line2D(
    [0], [0],
    color=EN_colors["PEM"],
    linestyle="dotted",
    linewidth=1.2
)

l_EN_SST = Line2D(
    [0], [0],
    color=EN_colors["SOE"],
    linestyle="dotted",
    linewidth=1.2
)



labels = [
    "PV", "WT", "Grid",
    "SST energy",
    "Electrolysis",
    "Coal-based methanol",
    "Methanol production",
    "LCOM"
]


legend_handles = (
    list(l_stack)
    + [l_EN_SST, l_EL, l_MeOHcoal, l_MeOH, l_LCOM]
)


fig.legend(
    legend_handles, labels,
    ncol=4, fontsize=12,
    loc="upper center", bbox_to_anchor=(0.5, 0.98),
    frameon=False
)

fig.subplots_adjust(
    top=0.92, bottom=0.06,
    left=0.04, right=0.99,
    wspace=0.35, hspace=0.05
)

                                    
fig.text(
    -0.05, 0.5,
    "Energy generation and utilization (GWh)",
    va="center",
    rotation="vertical",
    fontsize=16
)

fig.text(
    1.03, 0.5,
    "LCOM (2025 USD/ton)",
    va="center",
    rotation="vertical",
    fontsize=16
)

                
fig.text(
    0.52, 0.03,
    "Time (h)",
    ha="center",
    fontsize=16
)


fig.savefig(
    r"E:\2025_Methanol_synthesis\3_GAMS\P5_Operation_Diagram\fIGS\SOE_SUPP.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
