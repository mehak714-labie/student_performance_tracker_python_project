# ============================================================
#  charts.py  —  All chart functions using Matplotlib
# ============================================================
# Each function takes data and returns a Matplotlib Figure.
# That Figure gets embedded into the Tkinter window.

import matplotlib
matplotlib.use("TkAgg")          # use Tkinter-compatible backend
import matplotlib.pyplot as plt
import numpy as np
import database as db

# --- Color scheme (dark theme) ---
BG     = "#1e1e2e"   # background
FG     = "#cdd6f4"   # text color
GRID   = "#313244"   # grid lines
COLORS = ["#89b4fa", "#a6e3a1", "#f9e2af", "#f38ba8", "#cba6f7"]


def _apply_dark_style(fig, ax):
    """Apply dark background to any chart (called by every function)"""
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.yaxis.grid(True, color=GRID, linestyle="--", linewidth=0.5)
    ax.set_axisbelow(True)


# ── CHART 1: Bar chart — subject marks per exam ──────────────

def bar_chart(marks_by_exam, student_name):
    """Show marks for each subject, grouped by exam"""
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.subplots_adjust(bottom=0.2)

    exams    = [e for e in db.EXAMS if e in marks_by_exam]
    x        = np.arange(len(db.SUBJECTS))
    bar_width = 0.25

    for i, exam in enumerate(exams):
        # Get score for each subject (default 0 if missing)
        scores = [marks_by_exam[exam].get(s, 0) for s in db.SUBJECTS]
        bars   = ax.bar(x + i * bar_width, scores, bar_width,
                        label=exam, color=COLORS[i], alpha=0.9)
        # Show the number on top of each bar
        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1,
                    str(int(score)),
                    ha="center", fontsize=8, color=FG)

    # Use short subject names on X axis
    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(db.SUBJECTS, rotation=15, ha="right", fontsize=9)
    ax.set_ylim(0, 115)
    ax.set_ylabel("Marks")
    ax.set_title(f"Subject Marks — {student_name}")
    ax.legend(facecolor=BG, edgecolor=GRID, labelcolor=FG)
    _apply_dark_style(fig, ax)
    return fig


# ── CHART 2: Line chart — performance trend ──────────────────

def line_chart(trend, student_name):
    """Show how average score changed across exams"""
    fig, ax = plt.subplots(figsize=(7, 4))

    exams  = [item[0] for item in trend]
    scores = [item[1] for item in trend]

    ax.plot(exams, scores, color=COLORS[0], linewidth=2.5,
            marker="o", markersize=10, markerfacecolor=COLORS[2])
    ax.fill_between(exams, scores, alpha=0.15, color=COLORS[0])

    # Label each point
    for exam, score in zip(exams, scores):
        ax.text(exam, score + 2, f"{score}", ha="center",
                fontsize=11, fontweight="bold", color=FG)

    # Draw pass line at 50
    ax.axhline(50, color=COLORS[3], linewidth=1.2,
               linestyle="--", alpha=0.7, label="Pass mark (50)")
    ax.set_ylim(0, 110)
    ax.set_ylabel("Average Score")
    ax.set_title(f"Performance Trend — {student_name}")
    ax.legend(facecolor=BG, edgecolor=GRID, labelcolor=FG)
    _apply_dark_style(fig, ax)
    return fig


# ── CHART 3: Pie chart — pass vs fail ────────────────────────

def pie_chart(passed, failed):
    """Show class pass/fail split as a pie chart"""
    fig, ax = plt.subplots(figsize=(5, 4))

    if passed + failed == 0:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                color=FG, transform=ax.transAxes, fontsize=13)
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        return fig

    ax.pie(
        [passed, failed],
        labels=[f"Pass ({passed})", f"Fail ({failed})"],
        colors=[COLORS[1], COLORS[3]],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": BG, "linewidth": 2},
        textprops={"color": FG, "fontsize": 11}
    )
    ax.set_title("Class Pass / Fail", color=FG)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    return fig


# ── CHART 4: Radar chart — subject strengths ─────────────────

def radar_chart(subject_avgs, class_avgs, student_name):
    """Spider/radar chart showing strong and weak subjects"""
    subjects = db.SUBJECTS
    N        = len(subjects)

    # Angles: evenly space N points around a circle
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]   # close the shape by repeating first point

    student_scores = [subject_avgs.get(s, 0) for s in subjects] + [subject_avgs.get(subjects[0], 0)]
    class_scores   = [class_avgs.get(s, 0)   for s in subjects] + [class_avgs.get(subjects[0], 0)]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # Plot student line
    ax.plot(angles, student_scores, color=COLORS[0], linewidth=2)
    ax.fill(angles, student_scores, color=COLORS[0], alpha=0.25, label=student_name)

    # Plot class average line
    ax.plot(angles, class_scores, color=COLORS[2], linewidth=1.5, linestyle="--")
    ax.fill(angles, class_scores, color=COLORS[2], alpha=0.1, label="Class Avg")

    ax.set_thetagrids(np.degrees(angles[:-1]), subjects, color=FG, fontsize=9)
    ax.set_ylim(0, 100)
    ax.tick_params(colors=FG)
    ax.yaxis.grid(True, color=GRID, linestyle="--")
    ax.xaxis.grid(True, color=GRID)
    ax.set_title(f"Subject Strengths — {student_name}", color=FG, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1),
              facecolor=BG, edgecolor=GRID, labelcolor=FG, fontsize=9)
    return fig
