import tkinter as tk
from tkinter import ttk
import os
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- CSV Path ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_PATH = os.path.join(BASE_DIR, "saves", "stats.csv")

# --- Aincrad Theme Colors ---
COLOR_BG = "#0f0f19"
COLOR_PANEL = "#1a1a2e"
COLOR_ACCENT = "#b43232"
COLOR_GOLD = "#ffe066"
COLOR_WHITE = "#f0f0f0"
COLOR_SUBTEXT = "#aaaaaa"
COLOR_CRIT = "#ff8c00"
COLOR_NORMAL = "#e05050"
COLOR_KILL = "#50c878"
COLOR_PURCHASE = "#7eb8f7"
COLOR_SKILL = "#c87eff"
COLOR_PLAYTIME = "#7ef7d4"


# ===========================================================================
# DATA LOADING
# ===========================================================================

def load_data():
    """Reads the CSV using Pandas and maps session IDs to readable names."""
    if not os.path.exists(STATS_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(STATS_PATH)

        # Convert long session hashes into readable "Session 1, Session 2..."
        if not df.empty and "session_id" in df.columns:
            unique_sessions = df["session_id"].dropna().unique()
            ordered_labels = [f"Session {i + 1}" for i in range(len(unique_sessions))]
            session_map = dict(zip(unique_sessions, ordered_labels))

            df["session_name"] = df["session_id"].map(session_map)
            # Make it categorical to ensure proper sorting in charts
            df["session_name"] = pd.Categorical(
                df["session_name"], categories=ordered_labels, ordered=True
            )

        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


# ===========================================================================
# STATISTICAL CALCULATIONS
# ===========================================================================

def compute_stats(series: pd.Series) -> dict:
    """Mean, Median, Std, Min, Max on a Pandas Series."""
    if series is None or series.empty:
        return {"mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "count": 0}

    series = pd.to_numeric(series, errors='coerce').dropna()
    return {
        "mean": round(series.mean(), 2),
        "median": round(series.median(), 2),
        "std": round(series.std(), 2) if len(series) > 1 else 0,
        "min": series.min(),
        "max": series.max(),
        "count": len(series),
    }


# ===========================================================================
# MATPLOTLIB CHARTS
# ===========================================================================

def apply_theme(ax):
    """Applies the dark Aincrad theme to a Matplotlib Axes."""
    ax.set_facecolor(COLOR_PANEL)
    ax.tick_params(colors=COLOR_SUBTEXT, labelsize=8)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color(COLOR_SUBTEXT)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)


def draw_bar_chart(parent, series, title: str, bar_color: str, y_label=""):
    """Draws a bar chart embedded in Tkinter."""
    fig = Figure(figsize=(5.6, 2.2), dpi=100)
    fig.patch.set_facecolor(COLOR_PANEL)
    ax = fig.add_subplot(111)
    apply_theme(ax)

    if series is None or series.empty:
        ax.text(0.5, 0.5, "No Data", color=COLOR_SUBTEXT, ha='center', va='center')
        ax.axis('off')
    else:
        # Avoid truncating if the label is nicely formatted like "Session X"
        labels = [str(x) if str(x).startswith("Session") else (str(x)[:8] + "…" if len(str(x)) > 8 else str(x)) for x in
                  series.index]
        bars = ax.bar(labels, series.values, color=bar_color)
        ax.bar_label(bars, color=COLOR_WHITE, fontsize=8, padding=2)
        ax.set_ylabel(y_label, color=COLOR_SUBTEXT, fontsize=8)

    ax.set_title(title, color=COLOR_WHITE, fontsize=10, fontweight="bold")
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(padx=10, pady=4)


def draw_line_chart(parent, series, title: str, line_color: str):
    """Draws a line chart embedded in Tkinter."""
    fig = Figure(figsize=(5.6, 2.2), dpi=100)
    fig.patch.set_facecolor(COLOR_PANEL)
    ax = fig.add_subplot(111)
    apply_theme(ax)

    if series is None or len(series) < 2:
        ax.text(0.5, 0.5, "Not enough data (min 2 points)", color=COLOR_SUBTEXT, ha='center', va='center')
        ax.axis('off')
    else:
        ax.plot(range(len(series)), series.values, color=line_color, linewidth=2)

    ax.set_title(title, color=COLOR_WHITE, fontsize=10, fontweight="bold")
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(padx=10, pady=4)


def draw_pie_chart(parent, series, title: str):
    """Draws a pie chart embedded in Tkinter."""
    fig = Figure(figsize=(5.6, 2.6), dpi=100)
    fig.patch.set_facecolor(COLOR_PANEL)
    ax = fig.add_subplot(111)
    ax.set_facecolor(COLOR_PANEL)

    if series is None or series.empty or series.sum() == 0:
        ax.text(0.5, 0.5, "No Data", color=COLOR_SUBTEXT, ha='center', va='center')
        ax.axis('off')
    else:
        colors = ["#b43232", "#ffe066", "#50c878", "#7eb8f7", "#c87eff", "#7ef7d4", "#ff8c00", "#e05050"]
        wedges, texts, autotexts = ax.pie(
            series.values, labels=series.index, autopct='%1.1f%%',
            colors=colors, textprops={'color': COLOR_WHITE, 'fontsize': 8}
        )
        for autotext in autotexts:
            autotext.set_weight("bold")

    ax.set_title(title, color=COLOR_WHITE, fontsize=10, fontweight="bold")
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(padx=10, pady=8)


# ===========================================================================
# STATS WIDGETS
# ===========================================================================

def make_stat_row(parent, label, value, color=COLOR_GOLD):
    f = tk.Frame(parent, bg=COLOR_PANEL)
    f.pack(fill="x", pady=1)
    tk.Label(f, text=label, bg=COLOR_PANEL, fg=COLOR_SUBTEXT,
             font=("Verdana", 10), width=18, anchor="w").pack(side="left")
    tk.Label(f, text=str(value), bg=COLOR_PANEL, fg=color,
             font=("Verdana", 10, "bold")).pack(side="left")


def make_stats_panel(parent, title, stats: dict, color=COLOR_GOLD):
    frame = tk.LabelFrame(
        parent, text=title, bg=COLOR_PANEL,
        fg=COLOR_WHITE, font=("Verdana", 10, "bold"),
        bd=1, relief="flat", padx=8, pady=6
    )
    frame.pack(fill="x", padx=10, pady=4)
    make_stat_row(frame, "Count", stats["count"], color)
    make_stat_row(frame, "Mean", stats["mean"], color)
    make_stat_row(frame, "Median", stats["median"], color)
    make_stat_row(frame, "Std", stats["std"], color)
    make_stat_row(frame, "Min", stats["min"], color)
    make_stat_row(frame, "Max", stats["max"], color)


# ===========================================================================
# TABS
# ===========================================================================

def build_damage_tab(nb, df):
    tab = tk.Frame(nb, bg=COLOR_BG)
    nb.add(tab, text="  Damage  ")

    df_dmg = df[df["event_type"] == "damage"] if not df.empty else pd.DataFrame()

    all_dmg = pd.to_numeric(df_dmg["value"], errors='coerce') if not df_dmg.empty else pd.Series()
    norm_dmg = pd.to_numeric(df_dmg[df_dmg["metadata"] == "normal"]["value"],
                             errors='coerce') if not df_dmg.empty else pd.Series()
    crit_dmg = pd.to_numeric(df_dmg[df_dmg["metadata"] == "crit"]["value"],
                             errors='coerce') if not df_dmg.empty else pd.Series()

    top = tk.Frame(tab, bg=COLOR_BG)
    top.pack(fill="x")

    make_stats_panel(top, "All Damage", compute_stats(all_dmg), COLOR_GOLD)
    make_stats_panel(top, "Normal Hits", compute_stats(norm_dmg), COLOR_NORMAL)
    make_stats_panel(top, "Critical Hits", compute_stats(crit_dmg), COLOR_CRIT)

    draw_line_chart(tab, all_dmg.reset_index(drop=True), "Damage per Click (chronological)", COLOR_CRIT)


def build_kills_tab(nb, df):
    tab = tk.Frame(nb, bg=COLOR_BG)
    nb.add(tab, text="  Kills  ")

    df_kills = df[df["event_type"] == "kill"] if not df.empty else pd.DataFrame()

    if not df_kills.empty:
        by_monster = df_kills["metadata"].value_counts()
        by_floor = df_kills["floor_id"].apply(lambda x: f"Floor {x}").value_counts()
        kills_vals = pd.to_numeric(df_kills["value"], errors='coerce')
    else:
        by_monster = pd.Series()
        by_floor = pd.Series()
        kills_vals = pd.Series()

    make_stats_panel(tab, "Monster Kills", compute_stats(kills_vals), COLOR_KILL)
    draw_bar_chart(tab, by_monster, "Kills by Monster", COLOR_KILL, y_label="Kills")
    draw_bar_chart(tab, by_floor, "Kills by Floor", COLOR_KILL, y_label="Kills")


def build_purchases_tab(nb, df):
    tab = tk.Frame(nb, bg=COLOR_BG)
    nb.add(tab, text="  Gold Spent  ")

    df_purch = df[df["event_type"] == "purchase"].copy() if not df.empty else pd.DataFrame()

    if not df_purch.empty:
        df_purch["value"] = pd.to_numeric(df_purch["value"], errors='coerce')
        # Use 'session_name' instead of hashing strings
        by_session = df_purch.groupby("session_name", observed=True)["value"].sum()
        values = df_purch["value"].reset_index(drop=True)
    else:
        by_session = pd.Series()
        values = pd.Series()

    make_stats_panel(tab, "Gold Spent per Purchase", compute_stats(values), COLOR_PURCHASE)
    draw_bar_chart(tab, by_session, "Total Gold Spent by Session", COLOR_PURCHASE, y_label="Gold")
    draw_line_chart(tab, values, "Gold Spent per Purchase (chronological)", COLOR_PURCHASE)


def build_skills_tab(nb, df):
    tab = tk.Frame(nb, bg=COLOR_BG)
    nb.add(tab, text="  Skills  ")

    df_skills = df[df["event_type"] == "skill"] if not df.empty else pd.DataFrame()

    if not df_skills.empty:
        by_skill = df_skills["metadata"].value_counts()
        skills_vals = pd.to_numeric(df_skills["value"], errors='coerce')
    else:
        by_skill = pd.Series()
        skills_vals = pd.Series()

    make_stats_panel(tab, "Skill Activations", compute_stats(skills_vals), COLOR_SKILL)

    if not by_skill.empty:
        draw_pie_chart(tab, by_skill, "Skill Usage Distribution")
    else:
        tk.Label(tab, text="No skills used yet", bg=COLOR_BG, fg=COLOR_SUBTEXT, font=("Verdana", 12)).pack(pady=40)


def build_playtime_tab(nb, df):
    tab = tk.Frame(nb, bg=COLOR_BG)
    nb.add(tab, text="  Playtime  ")

    df_time = df[df["event_type"] == "playtime"] if not df.empty else pd.DataFrame()

    num_rows = len(df_time)
    total_sec = num_rows * 10
    total_min = total_sec // 60
    total_s_rem = total_sec % 60

    if not df_time.empty:
        # Use 'session_name' instead of hashing strings
        by_session = df_time.groupby("session_name", observed=True).size() * 10
    else:
        by_session = pd.Series()

    f = tk.Frame(tab, bg=COLOR_PANEL)
    f.pack(fill="x", padx=10, pady=8)
    tk.Label(f, text="Total Playtime Recorded", bg=COLOR_PANEL, fg=COLOR_SUBTEXT, font=("Verdana", 11)).pack()
    tk.Label(f, text=f"{total_min}m {total_s_rem}s", bg=COLOR_PANEL, fg=COLOR_PLAYTIME,
             font=("Verdana", 22, "bold")).pack()
    tk.Label(f, text=f"({num_rows} intervals of 10s  |  {len(by_session)} sessions)", bg=COLOR_PANEL, fg=COLOR_SUBTEXT,
             font=("Verdana", 9)).pack()

    draw_bar_chart(tab, by_session, "Playtime by Session (seconds)", COLOR_PLAYTIME, y_label="Seconds")


# ===========================================================================
# MAIN WINDOW
# ===========================================================================

def main():
    df = load_data()

    root = tk.Tk()
    root.title("AINCRAD SIMULATOR — Stats Analyzer")
    root.configure(bg=COLOR_BG)
    root.resizable(False, False)

    header = tk.Frame(root, bg=COLOR_ACCENT, pady=6)
    header.pack(fill="x")
    tk.Label(header, text="⚔  AINCRAD SIMULATOR  —  Data Analysis",
             bg=COLOR_ACCENT, fg=COLOR_WHITE,
             font=("Verdana", 14, "bold")).pack()

    if df.empty:
        tk.Label(root,
                 text=f"File not found or empty:\n{STATS_PATH}\n\nRun the game first.",
                 bg=COLOR_BG, fg=COLOR_SUBTEXT,
                 font=("Verdana", 12), pady=40).pack()
        root.mainloop()
        return

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=COLOR_PANEL, foreground=COLOR_WHITE,
                    padding=[10, 4], font=("Verdana", 10))
    style.map("TNotebook.Tab",
              background=[("selected", COLOR_ACCENT)],
              foreground=[("selected", COLOR_WHITE)])

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True, padx=10, pady=10)

    build_damage_tab(nb, df)
    build_kills_tab(nb, df)
    build_purchases_tab(nb, df)
    build_skills_tab(nb, df)
    build_playtime_tab(nb, df)

    root.mainloop()


if __name__ == "__main__":
    main()