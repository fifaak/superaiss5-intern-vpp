<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3><i class="bi bi-bar-chart-line-fill icon"></i> VPP Forecast</h3>
      </div>
      <div class="sidebar-content">
        <ControlPanel @predicted="handlePredicted" @preview="handlePreview" />
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="content-section">
        <Map :stations="stations"/>
      </div>
      <div class="content-section chart-section" v-if="stations.length">
        <Visualizer 
          :stations="stations" 
          :start-date-time="startDateTime"
        />
      </div>
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
      startDateTime: null
    };
  },
  methods: {
    handlePredicted({ stations: forecastStations, startDateTime }) {
      // merge forecast values onto current preview data
      this.stations = this.stations.map((previewStation, idx) => ({
        ...previewStation,
        values: previewStation.values.concat(forecastStations[idx].values)
      }));
      this.startDateTime = startDateTime;
    },
    handlePreview({ stations, startDateTime }) {
      this.stations = stations;
      this.startDateTime = startDateTime;
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
  gap: 1rem;
}

.content-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 1.5rem;
}

.chart-section {
  min-height: 400px;
}

.icon {
  margin-right: 0.5rem;
  vertical-align: middle;
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