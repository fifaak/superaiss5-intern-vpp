<template>
  <div class="visualizer">
    <canvas ref="chartEl"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import annotationPlugin from 'chartjs-plugin-annotation'

Chart.register(...registerables, annotationPlugin)

export default {
  name: 'Visualizer',
  props: {
    stations: {
      type: Array,
      required: true
    },
    actualData: {
      type: Array,
      default: () => []
    },
    isChulaSample: {
      type: Boolean,
      default: false
    },
    startDateTime: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const chartEl = ref(null)
    let chartInstance = null
    // store preview data length (first emission) to delineate current vs forecasted
    const previewLength = ref(0)

    const buildChart = (stationsData) => {
      const ctx = chartEl.value.getContext('2d')

      // if there's already a chart, destroy it before re-drawing
      if (chartInstance) {
        chartInstance.destroy()
      }

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

      const labels = generateTimeLabels()
      // Map each station into datasets
      let datasets = [];
      
      stationsData.forEach((st, idx) => {
        // Add forecast data
        datasets.push({
          label: `${st.name} (Forecast)`,
          data: st.values,
          fill: false,
          borderColor: `hsl(${idx * 60}, 70%, 50%)`,
          tension: 0.4
        });

        // If we have actual data for Chula sample, add it and the difference
        if (props.isChulaSample && props.actualData[idx]) {
          const actualData = props.actualData[idx];
          
          // Add actual data
          datasets.push({
            label: `${st.name} (Actual)`,
            data: actualData.values.map(v => v.actual),
            fill: false,
            borderColor: `hsl(${idx * 60}, 70%, 70%)`,
            borderDash: [5, 5],
            tension: 0.4
          });

          // Add difference data
          datasets.push({
            label: `${st.name} (Difference)`,
            data: actualData.values.map(v => v.difference),
            fill: false,
            borderColor: `hsl(${idx * 60}, 70%, 30%)`,
            borderWidth: 1,
            pointStyle: 'cross',
            tension: 0
          });
        }
      });

      // Prepare annotation ranges only if forecasted data exists
      let annotations = {}
      if (previewLength.value && labels.length > previewLength.value) {
        annotations.currentData = {
          type: 'box',
          xMin: labels[0],
          xMax: labels[previewLength.value - 1],
          backgroundColor: 'rgba(0, 255, 0, 0.1)',
          borderWidth: 0
        }
        annotations.forecastData = {
          type: 'box',
          xMin: labels[previewLength.value],
          xMax: labels[labels.length - 1],
          backgroundColor: 'rgba(255, 0, 0, 0.1)',
          borderWidth: 0
        }
      }

      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
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
            },
            annotation: {
              annotations
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
      // initial draw and set previewLength if not set
      if (props.stations?.[0]?.values.length) {
        previewLength.value = props.stations[0].values.length
      }
      buildChart(props.stations)
    })

    // Update chart whenever stations prop changes.
    watch(
      () => props.stations,
      (newStations) => {
        if (newStations && newStations.length) {
          // Set previewLength only once (if forecast data appended, length increases)
          if (previewLength.value === 0) {
            previewLength.value = newStations[0].values.length
          } else if (newStations[0].values.length < previewLength.value) {
            // if preview data is updated
            previewLength.value = newStations[0].values.length
          }
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