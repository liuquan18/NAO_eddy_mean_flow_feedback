# %%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

from matplotlib.lines import Line2D

from matplotlib.lines import Line2D
from matplotlib.gridspec import GridSpec

#%%
# Load dataframes from saved CSV files

def _load_csv(name, anomaly=False):
    load_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0eddy_momentum_pd/non_anomaly"
    return pd.read_csv(os.path.join(load_dir, f"{name}.csv"))



# #%%
Fdiv_phi_transient_high_pos_first_df = _load_csv("Fdiv_phi_transient_high_pos_first_df")
Fdiv_phi_transient_high_neg_first_df = _load_csv("Fdiv_phi_transient_high_neg_first_df")
Fdiv_phi_transient_high_pos_last_df = _load_csv("Fdiv_phi_transient_high_pos_last_df")
Fdiv_phi_transient_high_neg_last_df = _load_csv("Fdiv_phi_transient_high_neg_last_df")

Fdiv_phi_transient_lower_pos_first_df = _load_csv("Fdiv_phi_transient_lower_pos_first_df")
Fdiv_phi_transient_lower_neg_first_df = _load_csv("Fdiv_phi_transient_lower_neg_first_df")
Fdiv_phi_transient_lower_pos_last_df = _load_csv("Fdiv_phi_transient_lower_pos_last_df")
Fdiv_phi_transient_lower_neg_last_df = _load_csv("Fdiv_phi_transient_lower_neg_last_df")


Fdiv_p_transient_high_pos_first_df = _load_csv("Fdiv_p_transient_high_pos_first_df")
Fdiv_p_transient_high_neg_first_df = _load_csv("Fdiv_p_transient_high_neg_first_df")
Fdiv_p_transient_high_pos_last_df = _load_csv("Fdiv_p_transient_high_pos_last_df")
Fdiv_p_transient_high_neg_last_df = _load_csv("Fdiv_p_transient_high_neg_last_df")

Fdiv_p_transient_lower_pos_first_df = _load_csv("Fdiv_p_transient_lower_pos_first_df")
Fdiv_p_transient_lower_neg_first_df = _load_csv("Fdiv_p_transient_lower_neg_first_df")
Fdiv_p_transient_lower_pos_last_df = _load_csv("Fdiv_p_transient_lower_pos_last_df")
Fdiv_p_transient_lower_neg_last_df = _load_csv("Fdiv_p_transient_lower_neg_last_df")
#%%
Fdiv_transient_high_pos_first_df = Fdiv_phi_transient_high_pos_first_df.merge(Fdiv_p_transient_high_pos_first_df, on=["event","time", "phase", "decade"])
Fdiv_transient_high_pos_first_df['div'] = Fdiv_transient_high_pos_first_df['Fdiv_phi_transient'] - Fdiv_transient_high_pos_first_df['Fdiv_p_transient']

Fdiv_transient_high_neg_first_df = Fdiv_phi_transient_high_neg_first_df.merge(Fdiv_p_transient_high_neg_first_df, on=["event","time", "phase", "decade"])
Fdiv_transient_high_neg_first_df['div'] = Fdiv_transient_high_neg_first_df['Fdiv_phi_transient'] - Fdiv_transient_high_neg_first_df['Fdiv_p_transient']

Fdiv_transient_high_pos_last_df = Fdiv_phi_transient_high_pos_last_df.merge(Fdiv_p_transient_high_pos_last_df, on=["event","time", "phase", "decade"])  
Fdiv_transient_high_pos_last_df['div'] = Fdiv_transient_high_pos_last_df['Fdiv_phi_transient'] - Fdiv_transient_high_pos_last_df['Fdiv_p_transient']

Fdiv_transient_high_neg_last_df = Fdiv_phi_transient_high_neg_last_df.merge(Fdiv_p_transient_high_neg_last_df, on=["event","time", "phase", "decade"])
Fdiv_transient_high_neg_last_df['div'] = Fdiv_transient_high_neg_last_df['Fdiv_phi_transient'] - Fdiv_transient_high_neg_last_df['Fdiv_p_transient']

Fdiv_transient_lower_pos_first_df = Fdiv_phi_transient_lower_pos_first_df.merge(Fdiv_p_transient_lower_pos_first_df, on=["event","time", "phase", "decade"])
Fdiv_transient_lower_pos_first_df['div'] = Fdiv_transient_lower_pos_first_df['Fdiv_phi_transient'] - Fdiv_transient_lower_pos_first_df['Fdiv_p_transient']

Fdiv_transient_lower_neg_first_df = Fdiv_phi_transient_lower_neg_first_df.merge(Fdiv_p_transient_lower_neg_first_df, on=["event","time", "phase", "decade"])
Fdiv_transient_lower_neg_first_df['div'] = Fdiv_transient_lower_neg_first_df['Fdiv_phi_transient'] - Fdiv_transient_lower_neg_first_df['Fdiv_p_transient']

Fdiv_transient_lower_pos_last_df = Fdiv_phi_transient_lower_pos_last_df.merge(Fdiv_p_transient_lower_pos_last_df, on=["event","time", "phase", "decade"])
Fdiv_transient_lower_pos_last_df['div'] = Fdiv_transient_lower_pos_last_df['Fdiv_phi_transient'] - Fdiv_transient_lower_pos_last_df['Fdiv_p_transient']

Fdiv_transient_lower_neg_last_df = Fdiv_phi_transient_lower_neg_last_df.merge(Fdiv_p_transient_lower_neg_last_df, on=["event","time", "phase", "decade"])
Fdiv_transient_lower_neg_last_df['div'] = Fdiv_transient_lower_neg_last_df['Fdiv_phi_transient'] - Fdiv_transient_lower_neg_last_df['Fdiv_p_transient']
#%%

Fdiv_phi_steady_pos_first_df = _load_csv("Fdiv_phi_steady_pos_first_df")
Fdiv_phi_steady_neg_first_df = _load_csv("Fdiv_phi_steady_neg_first_df")
Fdiv_phi_steady_pos_last_df = _load_csv("Fdiv_phi_steady_pos_last_df")
Fdiv_phi_steady_neg_last_df = _load_csv("Fdiv_phi_steady_neg_last_df")

Fdiv_p_steady_pos_first_df = _load_csv("Fdiv_p_steady_pos_first_df")
Fdiv_p_steady_neg_first_df = _load_csv("Fdiv_p_steady_neg_first_df")
Fdiv_p_steady_pos_last_df = _load_csv("Fdiv_p_steady_pos_last_df")
Fdiv_p_steady_neg_last_df = _load_csv("Fdiv_p_steady_neg_last_df")

Fdiv_steady_high_pos_first_df = Fdiv_phi_steady_pos_first_df.merge(Fdiv_p_steady_pos_first_df, on=["event","time", "phase", "decade"])
Fdiv_steady_high_pos_first_df['div'] = Fdiv_steady_high_pos_first_df['Fdiv_phi_steady'] - Fdiv_steady_high_pos_first_df['Fdiv_p_steady']

Fdiv_steady_high_neg_first_df = Fdiv_phi_steady_neg_first_df.merge(Fdiv_p_steady_neg_first_df, on=["event","time", "phase", "decade"])
Fdiv_steady_high_neg_first_df['div'] = Fdiv_steady_high_neg_first_df['Fdiv_phi_steady'] - Fdiv_steady_high_neg_first_df['Fdiv_p_steady']

Fdiv_steady_high_pos_last_df = Fdiv_phi_steady_pos_last_df.merge(Fdiv_p_steady_pos_last_df, on=["event","time", "phase", "decade"])
Fdiv_steady_high_pos_last_df['div'] = Fdiv_steady_high_pos_last_df['Fdiv_phi_steady'] - Fdiv_steady_high_pos_last_df['Fdiv_p_steady']

Fdiv_steady_high_neg_last_df = Fdiv_phi_steady_neg_last_df.merge(Fdiv_p_steady_neg_last_df, on=["event","time", "phase", "decade"])
Fdiv_steady_high_neg_last_df['div'] = Fdiv_steady_high_neg_last_df['Fdiv_phi_steady'] - Fdiv_steady_high_neg_last_df['Fdiv_p_steady']
#%%

eke_pos_first_df = _load_csv("eke_pos_first_df")
eke_neg_first_df = _load_csv("eke_neg_first_df")
eke_pos_last_df = _load_csv("eke_pos_last_df")
eke_neg_last_df = _load_csv("eke_neg_last_df")

baroc_pos_first_df = _load_csv("baroc_pos_first_df")    
baroc_neg_first_df = _load_csv("baroc_neg_first_df")
baroc_pos_last_df = _load_csv("baroc_pos_last_df")    
baroc_neg_last_df = _load_csv("baroc_neg_last_df")
#%%
eke_core_pos_first_df = _load_csv("eke_core_pos_first_df")
eke_core_neg_first_df = _load_csv("eke_core_neg_first_df")
eke_core_pos_last_df = _load_csv("eke_core_pos_last_df")
eke_core_neg_last_df = _load_csv("eke_core_neg_last_df")    
#%%
def mean_diff_vs_1std(first_df, last_df, var_name):
    """Return mean(last)-mean(first) per time step.
    Significance threshold: 95% CI half-width of first (1.96 * SEM),
    consistent with the seaborn errorbar=("ci", 95) shading.
    """
    first_stats = (
        first_df.groupby("time")[var_name]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    first_stats.columns = ["time", "first_mean", "first_std", "first_n"]
    # 95% CI half-width (matches seaborn shading for large n)
    first_stats["ci95"] = 1.96 * first_stats["first_std"] / first_stats["first_n"].pow(0.5)

    last_mean = last_df.groupby("time")[var_name].mean().reset_index()
    last_mean.columns = ["time", "last_mean"]

    result = first_stats.merge(last_mean, on="time")
    result["diff"] = result["last_mean"] - result["first_mean"]
    return result

fig = plt.figure(figsize=(10, 8))
gs = GridSpec(
    5, 2, figure=fig,
    height_ratios=[3, 1, 0.5, 3, 1, ],
    hspace=0.08, wspace=0.35,
)

# Main axes (rows 0,3,6,9) and bar axes (rows 1,4,7,10); rows 2,5,8 are spacers
main_axes = [[fig.add_subplot(gs[3 * r, c]) for c in range(2)] for r in range(2)]
bar_axes  = [[fig.add_subplot(gs[3 * r + 1, c], sharex=main_axes[r][c]) for c in range(2)] for r in range(2)]

# Share y-axis within row 1 (momentum) and row 3 (heat)
# main_axes[0][1].sharey(main_axes[0][0])
# main_axes[1][1].sharey(main_axes[1][0])
# main_axes[1][1].sharey(main_axes[1][0])
# bar_axes[0][1].sharey(bar_axes[0][0])
# bar_axes[1][1].sharey(bar_axes[1][0])

COLOR_POS = "#E57200"  # MPI orange
COLOR_NEG = "#006C66"  # MPI green

def _plot_quartet(ax, pos_first, neg_first, pos_last, neg_last, y):
    """Plot 4 lines (pos/neg × first/last) on one axis."""
    kw = dict(x="time", errorbar=("ci", 95), lw=2, legend=False)
    sns.lineplot(data=pos_first, y=y, color=COLOR_POS, linestyle="solid",  ax=ax, **kw)
    sns.lineplot(data=neg_first, y=y, color=COLOR_NEG, linestyle="solid",  ax=ax, **kw)
    sns.lineplot(data=pos_last,  y=y, color=COLOR_POS, linestyle="dashed", ax=ax, **kw)
    sns.lineplot(data=neg_last,  y=y, color=COLOR_NEG, linestyle="dashed", ax=ax, **kw)

def _plot_diff_bars(ax, pos_first, neg_first, pos_last, neg_last, var_name):
    """Bar subplot: mean(last)-mean(first) per time step.
    Both phases: significant if |diff| > 95% CI half-width of first.
    This handles flipped cases (e.g. neg phase with positive anomaly).
    Non-significant bars use alpha=0.2.
    """
    pos_diff = mean_diff_vs_1std(pos_first, pos_last, var_name)
    neg_diff = mean_diff_vs_1std(neg_first, neg_last, var_name)
    for _, row in pos_diff.iterrows():
        significant = abs(row["diff"]) > row["ci95"]
        ax.bar(row["time"], row["diff"],
               color=COLOR_POS if significant else "none",
               alpha=0.5 if significant else 1.0,
               edgecolor=COLOR_POS, linewidth=0.8, width=1.0)
    for _, row in neg_diff.iterrows():
        significant = abs(row["diff"]) > row["ci95"]
        ax.bar(row["time"], row["diff"],
               color=COLOR_NEG if significant else "none",
               alpha=0.5 if significant else 1.0,
               edgecolor=COLOR_NEG, linewidth=0.8, width=1.0)
    ax.axhline(0, color="k", lw=0.5)
    sns.despine(ax=ax, bottom=True)
    ax.tick_params(bottom=False)

# ===== Row 1: Transient momentum / Steady momentum =====
_plot_quartet(main_axes[0][0], Fdiv_transient_high_pos_first_df, Fdiv_transient_high_neg_first_df, Fdiv_transient_high_pos_last_df, Fdiv_transient_high_neg_last_df, "div")
_plot_quartet(main_axes[0][1], baroc_pos_first_df, baroc_neg_first_df, baroc_pos_last_df, baroc_neg_last_df, "baroclinicity")
_plot_diff_bars(bar_axes[0][0], Fdiv_transient_high_pos_first_df, Fdiv_transient_high_neg_first_df, Fdiv_transient_high_pos_last_df, Fdiv_transient_high_neg_last_df, "div")
_plot_diff_bars(bar_axes[0][1], baroc_pos_first_df, baroc_neg_first_df, baroc_pos_last_df, baroc_neg_last_df, "baroclinicity")

# ===== Row 2: EKE / Baroclinicity =====
_plot_quartet(main_axes[1][0], eke_pos_first_df, eke_neg_first_df, eke_pos_last_df, eke_neg_last_df, "eke")
_plot_quartet(main_axes[1][1], eke_core_pos_first_df, eke_core_neg_first_df, eke_core_pos_last_df, eke_core_neg_last_df, "eke")
_plot_diff_bars(bar_axes[1][0], eke_pos_first_df, eke_neg_first_df, eke_pos_last_df, eke_neg_last_df, "eke")
_plot_diff_bars(bar_axes[1][1], eke_core_pos_first_df, eke_core_neg_first_df, eke_core_pos_last_df, eke_core_neg_last_df, "eke")


# ===== Titles =====
main_axes[0][0].set_title("EP flux divergence \n (higher latitude)")
main_axes[0][1].set_title("Eady growth rate / day$^{-1}$")
main_axes[1][0].set_title("EKE northern flank")
main_axes[1][1].set_title("EKE jet core")

# ===== y-labels =====
main_axes[0][0].set_ylabel(r"$\nabla \cdot F$ / m $s^{-1}$ day$^{-1}$")
main_axes[0][1].set_ylabel(r"$\sigma_E$ / day$^{-1}$")
main_axes[1][0].set_ylabel("EKE / m$^2$ s$^{-2}$")
main_axes[1][1].set_ylabel("EKE / m$^2$ s$^{-2}$")


# ===== x-labels: only bottom bar row =====
for r in range(2):
    for c in range(2):
        main_axes[r][c].set_xlabel("")
        plt.setp(main_axes[r][c].get_xticklabels(), visible=False)
        if r < 1:
            bar_axes[r][c].set_xlabel("")
            plt.setp(bar_axes[r][c].get_xticklabels(), visible=False)
        else:
            bar_axes[r][c].set_xlabel("Days relative to extreme onset")

# ===== Styling =====
for r in range(2):
    for c in range(2):
        sns.despine(ax=main_axes[r][c], bottom=True)
        main_axes[r][c].tick_params(bottom=False)
        main_axes[r][c].axvline(0, color="gray", linestyle="dotted", lw=1)

# ===== Legend (top-right main panel) =====
decade_handles = [
    Line2D([0], [0], color="gray",  lw=2, linestyle="-",  label="1850s"),
    Line2D([0], [0], color="gray",  lw=2, linestyle="--", label="2090s"),
]
phase_handles = [
    Line2D([0], [0], color=COLOR_POS, lw=2, label="pos NAO"),
    Line2D([0], [0], color=COLOR_NEG, lw=2, label="neg NAO"),
]
decade_legend = main_axes[0][0].legend(
    handles=decade_handles, title="decade",
    loc="lower left", bbox_to_anchor=(0.1, 0.7), frameon=False,
)
main_axes[0][0].add_artist(decade_legend)
main_axes[0][0].legend(
    handles=phase_handles, title="phase",
    loc="lower left", bbox_to_anchor=(0.7, 0.7), frameon=False,
)

# ===== Panel labels =====
panel_idx = 0
for r in range(2):
    for c in range(2):
        main_axes[r][c].text(
            -0.08, 1.02, chr(97 + panel_idx),
            transform=main_axes[r][c].transAxes,
            fontsize=14, fontweight="bold", va="bottom", ha="right",
        )
        panel_idx += 1
# for all axes, xlim -20, 20
for r in range(2):
    for c in range(2):
        main_axes[r][c].set_xlim(-20, 20.5)
        bar_axes[r][c].set_xlim(-20, 20.5)

# make bar axes y-limits symmetric
for r in range(2):
    for c in range(2):
        ax = bar_axes[r][c]
        abs_max = max(abs(ax.get_ylim()[0]), abs(ax.get_ylim()[1]))
        ax.set_ylim(-abs_max, abs_max)

plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/feedback_lines_nonano.pdf",
    dpi=300, bbox_inches="tight",
)





# %%
Fdiv_transient_high_pos_first_df['ratio'] = Fdiv_transient_high_pos_first_df['Fdiv_phi_transient'] / (baroc_pos_first_df['baroclinicity'] * 86400)
Fdiv_transient_high_neg_first_df['ratio'] = Fdiv_transient_high_neg_first_df['Fdiv_phi_transient'] / (baroc_neg_first_df['baroclinicity'] * 86400)
Fdiv_transient_high_pos_last_df['ratio'] = Fdiv_transient_high_pos_last_df['Fdiv_phi_transient'] / (baroc_pos_last_df['baroclinicity'] * 86400)
Fdiv_transient_high_neg_last_df['ratio'] = Fdiv_transient_high_neg_last_df['Fdiv_phi_transient'] / (baroc_neg_last_df['baroclinicity'] * 86400)

Fdiv_transient_lower_pos_first_df['ratio'] = Fdiv_transient_lower_pos_first_df['Fdiv_phi_transient'] / (baroc_pos_first_df['baroclinicity'] * 86400)
Fdiv_transient_lower_neg_first_df['ratio'] = Fdiv_transient_lower_neg_first_df['Fdiv_phi_transient'] / (baroc_neg_first_df['baroclinicity'] * 86400)
Fdiv_transient_lower_pos_last_df['ratio'] = Fdiv_transient_lower_pos_last_df['Fdiv_phi_transient'] / (baroc_pos_last_df['baroclinicity'] * 86400)
Fdiv_transient_lower_neg_last_df['ratio'] = Fdiv_transient_lower_neg_last_df['Fdiv_phi_transient'] / (baroc_neg_last_df['baroclinicity'] * 86400)
#%%
fig = plt.figure(figsize=(10, 10))
gs = GridSpec(
    6, 2, figure=fig,
    height_ratios=[3, 1, 0.5, 3, 1, 0.5],
    hspace=0.08, wspace=0.35,
)
main_ax_high = [fig.add_subplot(gs[r, 0]) for r in range(0, 6, 3)]
main_ax_lower = [fig.add_subplot(gs[r, 1]) for r in range(0, 6, 3)]
bar_ax_high = [fig.add_subplot(gs[r, 0], sharex=main_ax_high[0]) for r in range(1, 6, 3)]
bar_ax_lower = [fig.add_subplot(gs[r, 1], sharex=main_ax_lower[0]) for r in range(1, 6, 3)]

_plot_quartet(
    main_ax_high[0],
    Fdiv_transient_high_pos_first_df,
    Fdiv_transient_high_neg_first_df,
    Fdiv_transient_high_pos_last_df,
    Fdiv_transient_high_neg_last_df,
    "div",
)

_plot_quartet(
    main_ax_lower[0],
    Fdiv_transient_lower_pos_first_df,
    Fdiv_transient_lower_neg_first_df,
    Fdiv_transient_lower_pos_last_df,
    Fdiv_transient_lower_neg_last_df,
    "div",
)

_plot_diff_bars(
    bar_ax_high[0],
    Fdiv_transient_high_pos_first_df,
    Fdiv_transient_high_neg_first_df,
    Fdiv_transient_high_pos_last_df,
    Fdiv_transient_high_neg_last_df,
    "div",
)

_plot_diff_bars(
    bar_ax_lower[0],
    Fdiv_transient_lower_pos_first_df,
    Fdiv_transient_lower_neg_first_df,
    Fdiv_transient_lower_pos_last_df,
    Fdiv_transient_lower_neg_last_df,
    "div",
)


_plot_quartet(
    main_ax_high[1],
    Fdiv_transient_high_pos_first_df,
    Fdiv_transient_high_neg_first_df,
    Fdiv_transient_high_pos_last_df,
    Fdiv_transient_high_neg_last_df,
    "ratio",
)
_plot_quartet(
    main_ax_lower[1],
    Fdiv_transient_lower_pos_first_df,
    Fdiv_transient_lower_neg_first_df,
    Fdiv_transient_lower_pos_last_df,
    Fdiv_transient_lower_neg_last_df,
    "ratio",
)

_plot_diff_bars(
    bar_ax_high[1],
    Fdiv_transient_high_pos_first_df,
    Fdiv_transient_high_neg_first_df,
    Fdiv_transient_high_pos_last_df,
    Fdiv_transient_high_neg_last_df,
    "ratio",
)
_plot_diff_bars(
    bar_ax_lower[1],
    Fdiv_transient_lower_pos_first_df,
    Fdiv_transient_lower_neg_first_df,
    Fdiv_transient_lower_pos_last_df,
    Fdiv_transient_lower_neg_last_df,
    "ratio",
)

main_ax_high[0].set_title("EP flux convergence (higher latitude)")
main_ax_lower[0].set_title("EP flux convergence (lower latitude)")
main_ax_high[1].set_title("Efficiency (higher latitude)")
main_ax_lower[1].set_title("Efficiency (lower latitude)")
main_ax_high[0].set_ylabel(r"$- \nabla \cdot F$ / m $s^{-1}$ day$^{-1}$")
main_ax_lower[0].set_ylabel("")
main_ax_high[1].set_ylabel("sink / source")
main_ax_lower[1].set_ylabel("")


for ax in main_ax_high + main_ax_lower:
    ax.set_xlim(-20, 20.5)
    ax.axvline(0, color="gray", linestyle="dotted", lw=1)
    sns.despine(ax=ax, bottom=True)
    ax.tick_params(bottom=False)
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), visible=False)


for i, (ax_high, ax_lower) in enumerate(zip(bar_ax_high, bar_ax_lower)):
    for ax in [ax_high, ax_lower]:
        ax.set_xlim(-20, 20.5)
        abs_max = max(abs(ax.get_ylim()[0]), abs(ax.get_ylim()[1]))
        ax.set_ylim(-abs_max, abs_max)
        if i == 0:
            ax.set_xlabel("")
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            ax.set_xlabel("Days relative to extreme onset")

# ===== Panel labels =====
panel_idx = 0
for r in range(2):
    for c in range(2):
        main_ax_high[r].text(
            -0.08, 1.02, chr(97 + panel_idx),
            transform=main_ax_high[r].transAxes,
            fontsize=14, fontweight="bold", va="bottom", ha="right",
        )
        main_ax_lower[r].text(
            -0.08, 1.02, chr(97 + panel_idx + 2),
            transform=main_ax_lower[r].transAxes,
            fontsize=14, fontweight="bold", va="bottom", ha="right",
        )
        panel_idx += 1
plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/feedback_lines_efficiency_nonano.pdf",
    dpi=300, bbox_inches="tight",
)
# %%
