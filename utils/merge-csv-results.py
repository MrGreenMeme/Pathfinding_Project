import pandas
import re

def extract_map_info(filename: str):
    """
    Extracts map information from the given filename.

    The function identifies map size, map number, and space number based on
    the filename pattern. For self-made maps, it returns default values.

    Args:
        filename: The name of the file to extract information from.

    Returns:
        tuple: A tuple containing map size, map number, and space number.
    """
    pattern1 = re.compile(r'(\d+x\d+)_Map_(\d+)_Space_(\d+)\.txt') # 512x512_Map_1_Space_1.txt
    parts = filename.split("_")
    map_size = parts[0]
    if pattern1.match(filename):
        map_number = int(parts[2])
        space_number = int(parts[4].replace(".txt", ""))
        return map_size, map_number, space_number

    return map_size, 0, 0 # self-made maps 512x512_yyyy_mm_dd_hh_mm_ss.txt

def main() -> None:
    """Main function to load, clean, filter, and combine metrics from CSV files."""

    df = pandas.read_csv("../results/Stats.csv", sep=";")
    df_memory = pandas.read_csv("../results/Memory-Consumption.csv", sep=";")

    average_metrics = None
    average_memory_metrics = None

    if not df.empty:
        # clean data
        df_cleaned = df.dropna(subset=["Map-Filename"])
        filtered_df = df_cleaned[(df_cleaned["Map-Filename"].str.strip() != "not found")]

        #temp columns for filtering
        filtered_df[["Map-Size", "Map-Number", "Space-Number"]] = filtered_df["Map-Filename"].apply(
            lambda x: pandas.Series(extract_map_info(x))
        )

        # columns for mean
        numeric_columns = ["Path-Length", "Visited-Cubes", "Max-Queue-Size", "Runtime", "Found-Goal"]
        average_metrics = filtered_df.groupby(["Algorithm", "Map-Filename", "Map-Size", "Map-Number", "Space-Number"])[numeric_columns].mean().reset_index()
        average_metrics = average_metrics.sort_values(by=["Algorithm", "Map-Size", "Map-Number", "Space-Number"])

        # drop temp columns
        average_metrics = average_metrics.drop(columns=["Map-Size", "Map-Number", "Space-Number"])

        average_metrics.to_csv("../results/average-stats.csv", index=False, sep=";")

    if not df_memory.empty:
        # clean data
        df_memory_cleaned = df_memory.dropna(subset=["Map-Filename"])
        filtered_memory_df = df_memory_cleaned[(df_memory_cleaned["Map-Filename"].str.strip() != "not found")]

        average_memory_metrics = filtered_memory_df.groupby(["Algorithm", "Map-Filename"]).mean().reset_index()
        average_memory_metrics.to_csv("../results/average-memory-consumption.csv", index=False, sep=";")

    # combines average_stats with memory_stats
    if average_metrics is not None and average_memory_metrics is not None:
        combined_metrics = pandas.merge(average_metrics, average_memory_metrics, on=["Algorithm", "Map-Filename"])
        combined_metrics.to_csv("../results/results.csv", index=False, sep=";")
    else:
        print(f"Stats empty: {average_metrics is None} \nMemory-Stats empty: {average_memory_metrics is None}.\n-> Skip merge.")

if __name__ == "__main__":
    main()