<template>
  <div class="container py-5">
    <h2 class="mb-4">VPP Forecast Client</h2>
    <h4>map</h4>
    <Map :stations="stations"/>
    <h4>Graph</h4>

    <Visualizer v-if="stations.length" :stations="stations" class="mt-5" />
    <h4>Control Panel</h4>

    <ControlPanel @predicted="stations = $event" />
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