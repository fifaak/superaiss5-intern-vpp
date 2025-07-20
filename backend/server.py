# server.py
from model import InferenceModel
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

# built-in defaults
_DEFAULT_LOCATIONS = {
    "Data_สถานีชาร์จ":     (13.73624, 100.52995),
    "Data_อาคารจามจุรี4":   (13.73260, 100.53177),
    "Data_อาคารจามจุรี 9": (13.73380, 100.53045),
    "Data_อาคารจุลจักรพงษ์": (13.73684, 100.52852),
    "Data_อาคารบรมราชกุมารี": (13.73800, 100.52905),
    "Data_อาคารวิทยนิเวศน์":  (13.73723, 100.53015),
}

EXPECTED_NODES = len(_DEFAULT_LOCATIONS)

app = Flask(__name__)
CORS(app)

inf = InferenceModel("astgcnv2_5epoch.onnx", device="cpu")

@app.route("/forecast", methods=["POST"])
def forecast():
    try:
        data = request.get_json()

        # determine stations & locations
        stations_in = data.get("stations")
        if stations_in:
            if len(stations_in) != EXPECTED_NODES:
                raise ValueError(
                    f"Model expects {EXPECTED_NODES} stations, "
                    f"but got {len(stations_in)}."
                )
            station_names = [s["name"] for s in stations_in]
            locations = {s["name"]: (s["lat"], s["lon"]) for s in stations_in}
        else:
            station_names = list(_DEFAULT_LOCATIONS.keys())
            locations = _DEFAULT_LOCATIONS

        # build X tensor and validate shape
        X_input = np.array(data["X"], dtype=np.float32)
        # expected shape: [1, EXPECTED_NODES, 1, T]
        if X_input.ndim != 4 or X_input.shape[1] != EXPECTED_NODES:
            raise ValueError(
                f"Input X must have shape [1, {EXPECTED_NODES}, 1, T], "
                f"but got {list(X_input.shape)}."
            )

        # build edge_index
        if inf.need_edge:
            edge_index = np.array(data["edge_index"], dtype=np.int64)
            # optional: validate edge_index dims here...
            preds = inf.forecast(X_input, edge_index)
        else:
            preds = inf.forecast(X_input)

        preds_np = preds.squeeze(0)  # [N, T]
        station_data = []
        for i, name in enumerate(station_names):
            lat, lon = locations[name]
            station_data.append({
                "name": name,
                "lat": lat,
                "lon": lon,
                "values": preds_np[i].tolist()
            })

        return jsonify({"stations": station_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)