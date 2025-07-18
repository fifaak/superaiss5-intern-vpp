<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>VPP Forecast</h3>
      </div>
      <div class="sidebar-content">
        <ControlPanel @predicted="stations = $event" />
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="content-section">
        <Map :stations="stations"/>
      </div>
      <div class="content-section chart-section" v-if="stations.length">
        <Visualizer :stations="stations" />
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
    };
  },
};
</script>

<style>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.sidebar {
  width: 400px;
  height: 100%;
  background: white;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.content-section {
  padding: 1rem;
}

.chart-section {
  border-top: 1px solid #eee;
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
  }
}
</style>