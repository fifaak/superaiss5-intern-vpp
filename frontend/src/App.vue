<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar">
      <h4 class="mb-4">Control Panel</h4>
      <ControlPanel @predicted="stations = $event" />
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <h2 class="mb-4">VPP Forecast Client</h2>
      <h4>Map</h4>
      <Map :stations="stations" />
      <h4>Graph</h4>
      <Visualizer v-if="stations.length" :stations="stations" class="mt-5" />
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

<style scoped>
.app-container {
  display: flex;
  width: 100%;
  height: 100vh; /* Make sure it covers the full viewport height */
}

.sidebar {
  width: 300px;
  padding: 20px;
  background-color: #f8f9fa;
  border-right: 1px solid #dee2e6;
  box-sizing: border-box; /* Include padding and border in the element's total width and height */
}

.main-content {
  flex: 1;
  padding: 20px;
  box-sizing: border-box; /* Include padding in the element's total width and height */
  overflow: auto; /* Enable scrolling if content overflows */
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .app-container {
    flex-direction: column; /* Stack sidebar and main content vertically */
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #dee2e6;
  }
}
</style>