import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns



def load_csvs(file_names: list) -> pd.DataFrame:
    combined_df = pd.DataFrame()




    return combined_df

# Main execution
if __name__ == "__main__":
    print("Analyzing FaaS")

    faas_result_file_locs = ["./cleaned-results-aws/Lambda-Results.csv", "./cleaned-results-azure/Azure-Functions-Results.csv"]
    iaas_result_file_locs = ["./cleaned-results-aws/EC2-Results.csv", "./cleaned-results-azure/Azure-VM-Results.csv"]
    print("Loading of faas")

    print("Finished Analyzing FaaS")


