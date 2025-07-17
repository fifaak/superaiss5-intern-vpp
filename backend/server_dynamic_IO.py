import torch
from model import InferenceModel
from flask import Flask, request, jsonify
from flask_cors import CORS

# built-in defaults
_DEFAULT_LOCATIONS = {
    "Data_สถานีชาร์จ":     (13.73624, 100.52995),
    "Data_อาคารจามจุรี4":   (13.73260, 100.53177),
    "Data_อาคารจามจุรี 9": (13.73380, 100.53045),
    "Data_อาคารจุลจักรพงษ์": (13.73684, 100.52852),
    "Data_อาคารบรมราชกุมารี": (13.73800, 100.52905),
    "Data_อาคารวิทยนิเวศน์":  (13.73723, 100.53015),
}

app = Flask(__name__)
CORS(app)

inf = InferenceModel("astgcnv2_5epoch.onnx", device="cpu")

@app.route("/forecast", methods=["POST"])
def forecast():
    try:
        data = request.get_json()

        # 1) figure out station list & locations
        stations_in = data.get("stations")
        if stations_in:
            station_names = [s["name"] for s in stations_in]
            locations     = {s["name"]:(s["lat"], s["lon"]) for s in stations_in}
        else:
            station_names = list(_DEFAULT_LOCATIONS.keys())
            locations     = _DEFAULT_LOCATIONS

        num_nodes = len(station_names)

        # 2) build & validate X
        X_input = torch.tensor(data["X"]).float()
        # must be 4-D: [batch, N, 1, T]
        if X_input.ndim != 4 or X_input.shape[1] != num_nodes:
            raise ValueError(
              f"Input X must have shape [B, {num_nodes}, 1, T], "
              f"but got {list(X_input.shape)}."
            )

        # 3) get or build edge_index
        if inf.need_edge:
            if "edge_index" in data:
                edge_index = torch.tensor(data["edge_index"]).long()
            else:
                # fully-connected directed: i→j for all i≠j
                idx_i, idx_j = [], []
                for i in range(num_nodes):
                    for j in range(num_nodes):
                        if i != j:
                            idx_i.append(i); idx_j.append(j)
                edge_index = torch.tensor([idx_i, idx_j], dtype=torch.long)
            preds = inf.forecast(X_input, edge_index)
        else:
            preds = inf.forecast(X_input)

        # 4) format and return
        preds_np = preds.squeeze(0).numpy()  # [N, T]
        out = []
        for i, name in enumerate(station_names):
            lat, lon = locations[name]
            out.append({
                "name":   name,
                "lat":    lat,
                "lon":    lon,
                "values": preds_np[i].tolist()
            })

        return jsonify({"stations": out})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)