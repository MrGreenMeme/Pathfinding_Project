import pandas
import matplotlib.pyplot as plt
import os
from tkinter import filedialog

def plot_metrics_for_selected_map(df, map_file_name: str, metrics: list, metrics_description: list) -> None:
    """
    Plots metrics for the selected map and saves metric-plots as png-files.

    Args:
        df: The DataFrame containing the data to plot.
        map_file_name: The name of the map file to filter the data by.
        metrics: List of metric column names to plot.
        metrics_description: List of descriptions corresponding to the metrics for labeling the plot.
    """
    df_filtered = df[df["Map-Filename"] == map_file_name]

    if df_filtered.empty:
        print(f"No data found for the selected map: {map_file_name}")
        return

    for metric, description in zip(metrics, metrics_description):
        plt.figure(figsize=(10, 6))

        bars = plt.bar(
            x=df_filtered["Algorithm"],
            height=df_filtered[metric],
            color="seagreen"
        )

        plt.xlabel("Algorithm")
        plt.ylabel(description)
        plt.title(f"Average {metric} on {map_file_name}")

        for bar in bars:
            height = bar.get_height()
            if height % 1 != 0:
                plt.text(bar.get_x() + bar.get_width()/2, height, f"{height:.2f}", va="bottom", ha="center", fontsize=7)
            else:
                plt.text(bar.get_x() + bar.get_width()/2, height, f"{height:.0f}", va="bottom", ha="center", fontsize=7)

        plt.grid(axis='y', linestyle='--', alpha=0.7)

        if not os.path.exists(f"../plots/{map_file_name}"):
            os.makedirs(f"../plots/{map_file_name}")
        plt.savefig(f"../plots/{map_file_name}/{metric}.png")
        plt.close()


def main() -> None:
    """Main function to load result data, select a map file and to plot metrics from selected map."""

    df = pandas.read_csv("../results/results.csv", delimiter=";")

    map_file = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[("Text files", "*.txt")])

    if not map_file:
        print("No map file selected. Exiting...")
        return

    metrics = ["Path-Length", "Visited-Cubes", "Max-Queue-Size", "Runtime", "Memory-Used", "Count-Of-Memory-Allocations", "Average-Allocation-Size"]
    metrics_description = ["Path-Length", "Visited-Cubes", "Max-Queue-Size", "Runtime (seconds)", "Memory-Used (KB)", "Count-Of-Memory-Allocations", "Average-Allocation-Size (bytes)"]

    plot_metrics_for_selected_map(df, map_file.split("/")[-1] , metrics, metrics_description)

if __name__ == "__main__":
    main()
