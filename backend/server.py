import torch
from model import InferenceModel
from flask import Flask, request, jsonify
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

app = Flask(__name__)
inf = InferenceModel("/kaggle/working/astgcn_v2_final.onnx", device="cpu")

@app.route("/forecast", methods=["POST"])
def forecast():
    try:
        data = request.get_json()
        X_input = torch.tensor(data["X"]).float()  # Expecting shape [B, N, 1, seq_len]

        if inf.need_edge:
            edge_index = torch.tensor(data["edge_index"]).long()  # Expecting shape [2, E]
            preds = inf.forecast(X_input, edge_index)
        else:
            preds = inf.forecast(X_input)

        return jsonify({"predictions": preds.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)