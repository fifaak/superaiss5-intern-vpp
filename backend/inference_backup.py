
import torch
from model import InferenceModel
# --- Example usage ---
# 2. Graph setup
locations = {
    "Data_สถานีชาร์จ": (13.73624, 100.52995),
    "Data_อาคารจามจุรี4": (13.73260, 100.53177),
    "Data_อาคารจามจุรี 9": (13.73380, 100.53045),
    "Data_อาคารจุลจักรพงษ์": (13.73684, 100.52852),
    "Data_อาคารบรมราชกุมารี": (13.73800, 100.52905),
    "Data_อาคารวิทยนิเวศน์": (13.73723, 100.53015),
}
station_names = list(locations.keys())
num_nodes = len(station_names)

# fully connected edges (i != j)
edge_index = torch.tensor(
    [[i, j] for i in range(num_nodes) for j in range(num_nodes) if i != j],
    dtype=torch.long,
).t().contiguous()
len_input=96
# Case 1: ONNX with two inputs
inf = InferenceModel("/kaggle/working/astgcn_v2_final.onnx", device="cpu")
X_test = torch.randn(8, num_nodes, 1, len_input)
preds = inf.forecast(X_test, edge_index)                # must pass edge_index
print(preds)