<template>
  <div class="container py-5">
    <h2 class="mb-4">VPP Forecast Client</h2>
    <Visualizer v-if="stations.length" :stations="stations" class="mt-5" />
    <ControlPanel @predicted="stations = $event" />
  </div>
</template>

<script>
import ControlPanel from './components/ControlPanel.vue';
import Visualizer from './components/Visualizer.vue';

export default {
  components: {
    ControlPanel,
    Visualizer,
  },
  data() {
    return {
      stations: [],
    };
  },
};
</script>