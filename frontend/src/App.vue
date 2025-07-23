<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <img src="/thaivppplatform_logo.png" alt="Thai VPP Platform Logo" class="logo" />
      </div>
      <div class="sidebar-content">
        <ControlPanel @predicted="handlePredicted" @preview="handlePreview" />
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <Transition name="fade" mode="out-in">
        <div v-if="stations.length" class="content-wrapper">
          <div class="content-section chart-section">
            <Visualizer 
              :key="'visualizer-' + stations.length"
              :stations="stations" 
              :actual-data="actualData"
              :is-chula-sample="isChulaSample"
              :start-date-time="startDateTime"
            />
          </div>
          <div class="content-section">
            <Map :stations="stations"/>
          </div>
        </div>
        <div v-else class="content-section empty-state">
          <div class="text-center p-4">
            <i class="bi bi-bar-chart-line fs-1 mb-3 d-block text-muted"></i>
            <h5>No Data Available</h5>
            <p class="text-muted">Add stations or load sample data to begin</p>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script>
import ControlPanel from './components/ControlPanel.vue';
import Visualizer from './components/Visualizer.vue';
import Map from './components/Map.vue';
export default {
  components: {
    ControlPanel,
    Visualizer,
    Map,
  },
  data() {
    return {
      stations: [],
      actualData: [],
      startDateTime: null,
      isChulaSample: false
    };
  },
  methods: {
    handlePredicted({ stations: forecastStations, startDateTime, isChulaSample, actualData }) {
      // Store actual data if it's Chula sample
      if (isChulaSample && actualData) {
        this.isChulaSample = true;
        this.actualData = actualData.map(data => ({
          ...data,
          // Add difference calculation between forecast and actual
          values: data.values.map((val, i) => ({
            actual: val,
            forecast: forecastStations[i].values[i],
            difference: val - forecastStations[i].values[i]
          }))
        }));
      } else {
        this.isChulaSample = false;
        this.actualData = [];
      }

      // merge forecast values onto current preview data
      this.stations = this.stations.map((previewStation, idx) => ({
        ...previewStation,
        values: previewStation.values.concat(forecastStations[idx].values)
      }));
      this.startDateTime = startDateTime;
    },
    handlePreview({ stations, startDateTime }) {
      this.stations = stations;
      this.actualData = [];
      this.startDateTime = startDateTime;
      this.isChulaSample = false;
    }
  }
};
</script>

<style>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f8f9fa;
}

.sidebar {
  width: 400px;
  height: 100%;
  background: white;
  box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transition: transform 0.3s ease;
}

.sidebar-header {
  padding: 1.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 1rem;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.content-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 1.5rem;
}

.chart-section {
  min-height: 450px;
  margin-bottom: 1rem;
  flex: 1;
  position: relative;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.icon {
  margin-right: 0.5rem;
  vertical-align: middle;
}

.logo {
  width: 200px;
  height: auto;
  margin-bottom: 1rem;
  display: block;
}

@media (max-width: 1024px) {
  .sidebar {
    width: 350px;
  }
}

@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
    max-height: 50vh;
  }

  .main-content {
    height: 50vh;
    padding: 0.5rem;
  }

  .content-section {
    padding: 1rem;
  }
}
</style>