<template>
  <div class="control-panel">
    <form @submit.prevent="submitForecast">
      <div class="actions mb-3">
        <button type="button" class="btn btn-primary" @click="addStation">
          <i class="bi bi-plus-lg"></i> Add Station
        </button>
        <button type="button" class="btn btn-secondary" @click="fillSample">
          <i class="bi bi-file-text"></i> Sample Data
        </button>
      </div>

      <!-- Add datetime input before stations list -->
      <div class="mb-3">
        <label class="form-label">
          <i class="bi bi-calendar"></i> Start Date/Time
        </label>
        <input
          type="datetime-local"
          class="form-control"
          v-model="startDateTime"
          required
        />
      </div>

      <div class="stations-list">
        <div
          v-for="(st, idx) in stations"
          :key="idx"
          class="station-card mb-3 p-3 border rounded"
        >
          <div class="station-header">
            <h6>Station {{ idx + 1 }}</h6>
            <button
              v-if="stations.length > 1"
              type="button"
              class="btn btn-sm btn-outline-danger"
              @click="stations.splice(idx, 1)"
            >
              <i class="bi bi-trash"></i>
            </button>
          </div>
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Name</label>
              <input v-model="st.name" type="text" class="form-control" required />
            </div>
            <div class="col-md-3">
              <label class="form-label">Latitude</label>
              <input
                v-model.number="st.lat"
                type="number"
                step="any"
                class="form-control"
                required
              />
            </div>
            <div class="col-md-3">
              <label class="form-label">Longitude</label>
              <input
                v-model.number="st.lon"
                type="number"
                step="any"
                class="form-control"
                required
              />
            </div>
            <div class="col-md-12">
              <label class="form-label">
                Values (every 15 min)&nbsp;
                <small class="text-muted"
                  >(comma-sep, e.g. 0.1,0.2,0.3…)</small
                >
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
        </div>
      </div>

      <div class="submit-section">
        <button class="btn btn-primary w-100" type="submit" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-play-fill"></i>
          {{ loading ? 'Running...' : 'Run Forecast' }}
        </button>
      </div>
    </form>

    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>

    <div v-if="result" class="result-section mt-3">
      <h6>Predictions:</h6>
      <div class="result-box">
        <pre>{{ result }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ControlPanel",
  data() {
    return {
      startDateTime: new Date().toISOString().slice(0, 16), // Format: YYYY-MM-DDThh:mm
      // list of { name, lat, lon, values: "comma,sep,here" }
      stations: [
        { name: "", lat: null, lon: null, values: "" }
      ],
      result: null,
      loading: false,
      error: null
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
      this.loading = true;
      this.error = null;
      try {
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
          startDateTime: this.startDateTime // Add startDateTime to payload
        };

        const res = await fetch("http://127.0.0.1:8000/forecast", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });

        const json = await res.json();
        this.result = json;

        if (json.stations) {
          this.$emit("predicted", {
            stations: json.stations,
            startDateTime: this.startDateTime
          });
        }
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.control-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.stations-list {
  overflow-y: auto;
  flex: 1;
  margin: 0 -1.5rem;
  padding: 0 1.5rem;
}

.station-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.2s ease;
}

.station-card:hover {
  transform: translateY(-2px);
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.actions {
  display: flex;
  gap: 8px;
}

.submit-section {
  position: sticky;
  bottom: 0;
  padding: 1rem 0;
  background: white;
  border-top: 1px solid #eee;
  margin: 0 -1.5rem;
  padding: 1rem 1.5rem;
}

.result-box {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 1rem;
  font-size: 0.9em;
  max-height: 200px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .stations-list {
    margin: 0 -1rem;
    padding: 0 1rem;
  }
  
  .submit-section {
    margin: 0 -1rem;
    padding: 1rem;
  }
}
</style>