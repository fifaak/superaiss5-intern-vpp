<template>
  <div class="container py-5">
    <h2 class="mb-4">VPP Forecast Client</h2>
    <ControlPanel />
  </div>
</template>

<script>
import ControlPanel from './components/ControlPanel.vue';

export default {
  components: {
    ControlPanel,
  },
};
</script>