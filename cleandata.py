import os
import pandas as pd
# clean data
for filename in os.listdir("data"):
        if filename.endswith(".csv"):
            path = os.path.join("data", filename)
            try:
                # skip row2 and row3
                df = pd.read_csv(path, skiprows=[1, 2])

                # change column name to date
                df.rename(columns={df.columns[0]: "date"}, inplace=True)

                # add stock name column
                symbol = filename.replace(".csv", "")
                df["stockname"] = symbol

                # replace initial file
                df.to_csv(path, index=False)
                print(f"Cleaned: {filename}")
            except Exception as e:
                print(f"Failed to clean {filename}: {e}")
