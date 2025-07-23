<template>
  <div class="control-panel">
    <form @submit.prevent="submitForecast">
      <div class="actions mb-4">
        <button 
          type="button" 
          class="btn btn-primary action-btn" 
          @click="addStation"
          title="Add a new station to the forecast">
          <i class="bi bi-plus-lg"></i> Add Station
        </button>
        <button 
          type="button" 
          class="btn btn-secondary action-btn" 
          @click="fillSample"
          title="Fill with sample station data">
          <i class="bi bi-file-text"></i> Sample Data
        </button>
        <button 
          type="button" 
          class="btn btn-info action-btn" 
          @click="fillChulaData"
          title="Load real data from Chulalongkorn University">
          <i class="bi bi-database"></i> Chula's Real Data
        </button>
      </div>

      <!-- Data range slider for Chula's data -->
      <div v-if="showChulaSlider" class="slider-container mb-4">
        <label class="form-label d-flex align-items-center">
          <i class="bi bi-sliders me-2"></i> Data Range
          <span class="badge bg-primary ms-2">96 points per station</span>
        </label>
        <div class="slider-wrapper">
          <input
            type="range"
            class="form-range custom-range"
            min="0"
            :max="maxChulaSliderValue"
            v-model="chulaDataIndex"
            @input="updateChulaData"
          />
          <div class="time-range-display">
            <i class="bi bi-clock me-1"></i>
            {{ formatSliderDateTime(chulaDataIndex) }}
          </div>
        </div>
      </div>

      <!-- Add datetime input before stations list -->
      <div class="datetime-section mb-4">
        <label class="form-label d-flex align-items-center">
          <i class="bi bi-calendar me-2"></i> Start Date/Time
          <i class="bi bi-info-circle ms-2" title="Select the starting date and time for the forecast"></i>
        </label>
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-clock"></i>
          </span>
          <input
            type="datetime-local"
            class="form-control"
            v-model="startDateTime"
            required
            :class="{ 'is-invalid': !startDateTime }"
          />
        </div>
      </div>

      <h5 class="section-title mb-3">
        <i class="bi bi-geo-alt me-2"></i>
        Stations
        <span class="badge bg-secondary ms-2">{{ stations.length }}</span>
      </h5>
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
        <button 
          class="btn btn-primary w-100 submit-btn" 
          type="submit" 
          :disabled="loading"
          :class="{ 'btn-loading': loading }">
          <div class="d-flex align-items-center justify-content-center">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-play-fill me-2"></i>
            {{ loading ? 'Running Forecast...' : 'Run Forecast' }}
          </div>
        </button>
      </div>
    </form>

    <transition name="fade">
      <div v-if="error" class="alert alert-danger mt-3 d-flex align-items-center">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        {{ error }}
      </div>
    </transition>

    <transition name="fade">
      <div v-if="result" class="result-section mt-4">
        <h6 class="d-flex align-items-center mb-3">
          <i class="bi bi-graph-up me-2"></i>
          Predictions
          <span class="badge bg-success ms-2">Ready</span>
        </h6>
        <div class="result-box">
          <pre>{{ result }}</pre>
        </div>
      </div>
    </transition>
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
      error: null,
      showChulaSlider: false,
      chulaDataIndex: 0,
      chulaData: null,
      maxChulaSliderValue: 0
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
    async fillChulaData() {
      try {
        const response = await fetch('/test_data_chula.csv');
        const csvText = await response.text();
        
        // Parse CSV
        const rows = csvText.trim().split('\n').slice(1); // Skip header
        const stations = {};
        
        rows.forEach(row => {
          const [station, datetime, value] = row.split(',');
          if (!stations[station]) {
            stations[station] = {
              dates: [],
              values: []
            };
          }
          stations[station].dates.push(datetime);
          stations[station].values.push(parseFloat(value));
        });

        this.chulaData = stations;
        this.maxChulaSliderValue = Math.max(...Object.values(stations).map(s => s.values.length - 96));
        this.chulaDataIndex = 0;
        this.showChulaSlider = true;
        this.$nextTick(() => {
          this.updateChulaData();
        });
      } catch (error) {
        this.error = "Error loading Chula's data: " + error.message;
      }
    },

    formatSliderDateTime(index) {
      if (!this.chulaData) return '';
      const firstStation = Object.values(this.chulaData)[0];
      const startDate = firstStation.dates[index];
      const endDate = firstStation.dates[index + 95];
      return `${startDate} to ${endDate}`;
    },

    updateChulaData() {
      const stationCoordinates = {
        'Data_สถานีชาร์จ': { lat: 13.73624, lon: 100.52995 },
        'Data_อาคารจามจุรี4': { lat: 13.73260, lon: 100.53177 },
        'Data_อาคารจามจุรี 9': { lat: 13.73380, lon: 100.53045 },
        'Data_อาคารจุลจักรพงษ์': { lat: 13.73684, lon: 100.52852 },
        'Data_อาคารบรมราชกุมารี': { lat: 13.73800, lon: 100.52905 },
        'Data_อาคารวิทยนิเวศน์': { lat: 13.73723, lon: 100.53015 }
      };

      const index = parseInt(this.chulaDataIndex);
      
      this.stations = Object.entries(this.chulaData).map(([name, data]) => ({
        name,
        lat: stationCoordinates[name]?.lat || null,
        lon: stationCoordinates[name]?.lon || null,
        values: data.values.slice(index, index + 96).join(',')
      }));

      // Update start datetime
      if (this.chulaData && Object.keys(this.chulaData).length > 0) {
        const firstStation = Object.values(this.chulaData)[0];
        this.startDateTime = firstStation.dates[index].slice(0, 16); // Format: YYYY-MM-DDThh:mm
      }
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

        const res = await fetch(" http://192.168.1.38:8000/forecast", {
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
    emitPreview() {
      const parsed = this.stations.map(st => {
        const arr = st.values
          .split(',')
          .map(v => parseFloat(v.trim()))
          .filter(v => !Number.isNaN(v));
        return { ...st, values: arr };
      });
      this.$emit('preview', { stations: parsed, startDateTime: this.startDateTime });
    }
  },
  watch: {
    stations: {
      handler() { this.emitPreview(); },
      deep: true
    },
    startDateTime(newVal) { this.emitPreview(); }
  }
};
</script>

<style scoped>
.control-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
}

.stations-list {
  overflow-y: auto;
  flex: 1;
  margin: 0 -1.5rem;
  padding: 0 1.5rem;
}

.station-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.station-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

.station-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  transition: all 0.2s ease;
  border-radius: 8px;
  padding: 0.5rem 1rem;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.submit-section {
  position: sticky;
  bottom: 0;
  background: linear-gradient(to bottom, transparent, #f8f9fa 20%);
  margin: 0 -1.5rem;
  padding: 1.5rem;
}

.submit-btn {
  border-radius: 8px;
  padding: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-loading {
  background-color: #0056b3;
}

.result-box {
  background: white;
  border-radius: 8px;
  padding: 1.2rem;
  font-size: 0.9em;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}

.section-title {
  color: #495057;
  font-weight: 500;
}

.slider-container {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.slider-wrapper {
  position: relative;
  padding: 0.5rem 0;
}

.custom-range {
  height: 6px;
}

.time-range-display {
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.9em;
  text-align: center;
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .control-panel {
    padding: 1rem;
    border-radius: 0;
  }

  .stations-list {
    margin: 0 -1rem;
    padding: 0 1rem;
  }
  
  .submit-section {
    margin: 0 -1rem;
    padding: 1rem;
  }

  .action-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9em;
  }
}
</style>