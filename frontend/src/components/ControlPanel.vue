<template>
  <div>
    <form @submit.prevent="submitForecast">
      <div v-for="(st, idx) in stations" :key="idx" class="station-row mb-4 p-3 border rounded">
        <h6>Station {{ idx + 1 }}</h6>
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Name</label>
            <input v-model="st.name" type="text" class="form-control" required />
          </div>
          <div class="col-md-3">
            <label class="form-label">Latitude</label>
            <input v-model.number="st.lat" type="number" step="any" class="form-control" required />
          </div>
          <div class="col-md-3">
            <label class="form-label">Longitude</label>
            <input v-model.number="st.lon" type="number" step="any" class="form-control" required />
          </div>
          <div class="col-md-12">
            <label class="form-label">
              Values (every 30 min)&nbsp;
              <small class="text-muted">(comma-sep, e.g. 0.1,0.2,0.3…)</small>
            </label>
            <textarea
              v-model="st.values"
              class="form-control"
              rows="2"
              placeholder="e.g. 0.1,0.2,0.3,… (length must match all stations)"
              required
            ></textarea>
          </div>
        </div>
        <button
          type="button"
          class="btn btn-sm btn-danger mt-2"
          @click="stations.splice(idx, 1)"
          v-if="stations.length > 1"
        >
          Remove
        </button>
      </div>

      <button type="button" class="btn btn-outline-primary mb-3" @click="addStation">
        + Add Station
      </button>

      <div class="d-flex gap-2">
        <button class="btn btn-secondary" type="button" @click="fillSample">
          Sample Data
        </button>
        <button class="btn btn-primary" type="submit">
          Submit
        </button>
      </div>
    </form>

    <div v-if="result" class="mt-4">
      <h5>Predictions:</h5>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: "ControlPanel",
  data() {
    return {
      // list of { name, lat, lon, values: "comma,sep,here" }
      stations: [
        { name: "", lat: null, lon: null, values: "" }
      ],
      result: null,
    };
  },
  methods: {
    addStation() {
      this.stations.push({ name: "", lat: null, lon: null, values: "" });
    },
fillSample() {
  const seqLen = 96;
  this.stations = [
    {
      name: "Data_สถานีชาร์จ",
      lat: 13.73624,
      lon: 100.52995,
      values: Array(seqLen).fill(0.1).join(","),
    },
    {
      name: "Data_อาคารจามจุรี4",
      lat: 13.73260,
      lon: 100.53177,
      values: Array(seqLen).fill(0.2).join(","),
    },
    {
      name: "Data_อาคารจามจุรี 9",
      lat: 13.73380,
      lon: 100.53045,
      values: Array(seqLen).fill(0.3).join(","),
    },
    {
      name: "Data_อาคารจุลจักรพงษ์",
      lat: 13.73684,
      lon: 100.52852,
      values: Array(seqLen).fill(0.4).join(","),
    },
    {
      name: "Data_อาคารบรมราชกุมารี",
      lat: 13.73800,
      lon: 100.52905,
      values: Array(seqLen).fill(0.5).join(","),
    },
    {
      name: "Data_อาคารวิทยนิเวศน์",
      lat: 13.73723,
      lon: 100.53015,
      values: Array(seqLen).fill(0.6).join(","),
    },
  ];
},
    async submitForecast() {
      try {
        // parse station values into arrays
        const parsed = this.stations.map((st) => {
          const arr = st.values
            .split(",")
            .map((v) => parseFloat(v.trim()))
            .filter((v) => !Number.isNaN(v));
          return { ...st, values: arr };
        });

        const numNodes = parsed.length;
        const seqLen = parsed[0].values.length;

        // build X: shape [1, N, 1, seqLen]
        const X = [
          parsed.map((st) => [st.values])
        ];

        // fully connected directed edges (i != j)
        const edge_index = [[], []];
        for (let i = 0; i < numNodes; i++) {
          for (let j = 0; j < numNodes; j++) {
            if (i !== j) {
              edge_index[0].push(i);
              edge_index[1].push(j);
            }
          }
        }

        const body = {
          X,
          edge_index,
          stations: parsed.map(({ name, lat, lon }) => ({ name, lat, lon })),
        };

        const res = await fetch("http://localhost:8000/forecast", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });

        const json = await res.json();
        this.result = json;

        if (json.stations) {
          this.$emit("predicted", json.stations);
        }
      } catch (err) {
        this.result = { error: err.message };
      }
    },
  },
};
</script>

<style scoped>
.station-row {
  background: #f9f9f9;
}
</style>