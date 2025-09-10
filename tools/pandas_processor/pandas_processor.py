import pandas as pd
import sys
import os
import psutil
from datetime import datetime

class SimpleTimer:
    def __init__(self):
        self.start()

    def start(self):
        self.start_time = datetime.now()

    def stop(self) -> int:
        self.stop_time = datetime.now()
        return (self.stop_time - self.start_time).total_seconds() * 1000 


def get_memory_mb(process: psutil.Process) -> None:
    memory_bytes = process.memory_info().rss
    return memory_bytes / (1024 * 1024)


def process(raw_data_file: str, processed_data_file: str):
    process = psutil.Process(os.getpid())
    timer = SimpleTimer()    

    print("Starting memory:", get_memory_mb(process), "MBs.")
    
    timer.start()
    rawdf = pd.read_csv(raw_data_file)
    print("Took", timer.stop(), "ms to load", os.path.basename(raw_data_file), "memory:", get_memory_mb(process), "MBs.")
    print(rawdf.head())

    timer.start()
    processeddf = pd.read_csv(processed_data_file)
    print("Took", timer.stop(), "ms to load", os.path.basename(processed_data_file), "memory:", get_memory_mb(process), "MBs.")
    print(rawdf.head())
    
    # Step 1
    timer.start()
    dfA = rawdf[rawdf["ActionType"] == "FirstEntry"][["ParentName", "ExpectedChildrenCount"]]
    dfB = processeddf.groupby("ParentName").size().reset_index(name="ChildrenFoundCount")
    result = pd.merge(dfA, dfB, on="ParentName", how="inner")
    print(result.head())
    print("Took", timer.stop(), "ms to select FirstEntry and group by processed rows on ParentName.", os.path.basename(processed_data_file), "memory:", get_memory_mb(process), "MBs.")

    # Step 2
    timer.start()
    only_children = rawdf[rawdf["ActionType"] == "Child"]
    merged = pd.merge(only_children, processeddf, on=["ParentName", "ChildName"], how="left", suffixes=("_r", "_p"))
    result = merged[merged["ChildName"].isna()]
    print(result.head())
    print("Took", timer.stop(), "ms find children that don't exist in processed-df.", os.path.basename(processed_data_file), "memory:", get_memory_mb(process), "MBs.")


def help():
    print("Reads the raw data and processed data csv files. Checks if the number of processed children per parent matches the expected children count and prints the children which were not processed.")
    print("Usage:")
    print("  pandas_processor <rawdata.csv> <processed_data.csv>")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        help()
        return 1

    raw_data_file = argv[1]
    if not os.path.exists(raw_data_file):
        print("Could not find file", raw_data_file)
        return 1

    processed_data_file = argv[2]
    if not os.path.exists(processed_data_file):
        print("Could not find file", raw_data_file)
        return 1

    timer = SimpleTimer()
    process(raw_data_file, processed_data_file)
    input("Total time: {0} ms. Press enter to exit.".format(timer.stop()))

sys.exit(main(sys.argv))