import torch
import numpy as np
import random
import os
import pandas as pd

def set_seed(seed):
    """Sets the seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def get_device():
    """Returns the appropriate device (GPU or CPU) and prints it."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    if torch.cuda.is_available():
        print(f"Device name: {torch.cuda.get_device_name(0)}")
    return device

def save_results(experiment_name, results_df, log_df):
    """Saves the experiment results and logs to CSV files."""
    output_dir = f"results/{experiment_name}"
    os.makedirs(output_dir, exist_ok=True)
    results_df.to_csv(os.path.join(output_dir, f"{experiment_name}_results.csv"), index=False)
    log_df.to_csv(os.path.join(output_dir, f"{experiment_name}_log.csv"), index=False)