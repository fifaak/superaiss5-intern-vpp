<template>
  <div class="visualizer">
    <canvas ref="chartEl"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'Visualizer',
  props: {
    stations: {
      type: Array,
      required: true
    }
  },
  setup(props) {
    const chartEl = ref(null)
    let chartInstance = null

    const buildChart = (stationsData) => {
      const ctx = chartEl.value.getContext('2d')

      // if there's already a chart, destroy it before re-drawing
      if (chartInstance) {
        chartInstance.destroy()
      }

      // Example: plot each station as a separate dataset
      const datasets = stationsData.map((st, idx) => ({
        label: st.name,
        data: st.values,
        fill: false,
        // Chart.js will pick default colors
      }))

      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: stationsData[0]?.values.map((_, i) => i), // 0,1,2,... as x-axis
          datasets
        },
        options: {
          responsive: true,
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          },
          plugins: {
            legend: {
              position: 'bottom'
            },
            title: {
              display: true,
              text: 'Station Predictions Over Time'
            }
          },
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: 'Timestep'
              }
            },
            y: {
              display: true,
              title: {
                display: true,
                text: 'Value'
              }
            }
          }
        }
      })
    }

    onMounted(() => {
      // initial draw
      buildChart(props.stations)
    })

    // redraw whenever stations prop changes
    watch(
      () => props.stations,
      (newStations) => {
        if (chartEl.value && newStations && newStations.length) {
          buildChart(newStations)
        }
      },
      { deep: true }
    )

    return {
      chartEl
    }
  }
}
</script>

<style scoped>
.visualizer {
  position: relative;
  width: 100%;
  height: 400px;
}
canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>