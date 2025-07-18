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
    },
    startDateTime: {
      type: String,
      default: null
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

      // Generate time labels with date and time
      const generateTimeLabels = () => {
        const labels = []
        const start = props.startDateTime ? new Date(props.startDateTime) : new Date()

        for (let i = 0; i < stationsData[0]?.values.length; i++) {
          const time = new Date(start.getTime() + i * 15 * 60000) // Changed from 30 to 15 minutes
          labels.push(
            time.toLocaleString('th-TH', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })
          )
        }
        return labels
      }

      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: generateTimeLabels(),
          datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          },
          plugins: {
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `${context.dataset.label}: ${context.parsed.y} kW`
                }
              }
            },
            legend: {
              position: 'top',
              align: 'start',
              labels: {
                boxWidth: 15,
                usePointStyle: true
              }
            },
            title: {
              display: true,
              text: '📈 Station Predictions Over Time', // updated title with icon
              padding: {
                top: 10,
                bottom: 20
              }
            }
          },
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: 'Date/Time'
              },
              grid: {
                display: true,
                color: '#f0f0f0'
              },
              ticks: {
                maxRotation: 45,
                minRotation: 45
              }
            },
            y: {
              display: true,
              title: {
                display: true,
                text: 'Power (kW)'
              },
              grid: {
                color: '#f0f0f0'
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
  height: 100%;
  min-height: 400px;
}

canvas {
  width: 100% !important;
  height: 100% !important;
}

@media (max-width: 768px) {
  .visualizer {
    min-height: 300px;
  }
}
</style>