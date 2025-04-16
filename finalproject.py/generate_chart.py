# generate_chart.py

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend 

import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import Counter

def generate_chart(csv_path="sustainability_log.csv"):
    """
    Generates bar and pie charts from the sustainability log CSV.
    Outputs are saved to web_gui/static/ as .png images.

    Parameters:
    - csv_path (str): Path to the CSV log file (default is 'sustainability_log.csv')
    """

    # Check if the log file exists
    if not os.path.exists(csv_path):
        print("No log file found. Run the tool with --score to generate some data first.")
        return

    # Load CSV into a DataFrame
    df = pd.read_csv(csv_path)

    if df.empty:
        print("Log file is empty.")
        return

    # --- BAR CHART: Latest score per file ---

    # Get the most recent entry per filename (sorted by timestamp)
    latest = df.sort_values("timestamp").drop_duplicates("filename", keep="last")

    # Plot the bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(latest["filename"], latest["score"], color="#4CAF50")

    plt.xlabel("File", fontsize=12)
    plt.ylabel("Sustainability Score", fontsize=12)
    plt.title("Latest Sustainability Scores by File", fontsize=14)
    plt.ylim(0, 100)
    plt.xticks(rotation=45, ha="right")

    # Add value labels on top of each bar
    for bar, score in zip(bars, latest["score"]):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, str(score), ha='center', fontsize=10)

    plt.tight_layout()

    # Save bar chart
    bar_path = os.path.join("web_gui", "static", "sustainability_chart.png")
    plt.savefig(bar_path)
    print(f"Bar chart saved to {bar_path}")

    # --- PIE CHART: Distribution of suggestion types ---

    # Only generate if suggestion type data exists
    if "suggestion_type" in df.columns:
        all_types = df["suggestion_type"].dropna()
        type_counts = Counter(all_types)

        if type_counts:
            plt.figure(figsize=(6, 6))
            plt.pie(
                type_counts.values(),
                labels=type_counts.keys(),
                autopct='%1.1f%%',
                startangle=140
            )
            plt.title("Suggestion Types Distribution", fontsize=13)
            plt.axis('equal')  # Ensure circle shape
            plt.tight_layout()

            # Save pie chart
            pie_path = os.path.join("web_gui", "static", "suggestion_types_pie.png")
            plt.savefig(pie_path)
            print(f"Pie chart saved to {pie_path}")
        else:
            print("No suggestion types found to plot pie chart.")
    else:
        print("Pie chart skipped — no 'suggestion_type' column found.")
