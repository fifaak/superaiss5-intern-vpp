<!-- Access token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2NGNmODc0My03ODI2LTRkNGYtYWU5My0zYWM5MTU1OGE4NjgiLCJpZCI6MzIyNzEyLCJpYXQiOjE3NTI4MzE4ODd9.1oKKgaweBEEAU1pI-c_edzK7od6aBtD-0WEQsItJkl0 -->
<template>
  <div class="map-container">
    <div class="map-controls">
      <button class="map-btn" :class="{ active: viewMode === '2d' }" @click="viewMode = '2d'">
        <i class="bi bi-map"></i> 2D
      </button>
      <button class="map-btn" :class="{ active: viewMode === '3d' }" @click="viewMode = '3d'">
        <i class="bi bi-globe"></i> 3D
      </button>
    </div>

    <div v-show="viewMode === '2d'" id="map2d" class="map-view"></div>
    <div v-show="viewMode === '3d'" id="map3d" class="map-view"></div>
  </div>
</template>

<style scoped>
.map-container {
  position: relative;
  height: 100%;
  min-height: 500px;
  background: #f8f9fa;
}

.map-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  padding: 5px;
}

.map-btn {
  background: white;
  border: none;
  padding: 8px 16px;
  margin: 0 2px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.map-btn:hover {
  background: #f0f0f0;
}

.map-btn.active {
  background: #e0e0e0;
  font-weight: bold;
}

.map-view {
  height: 100%;
  width: 100%;
}
</style>

<script>
export default {
  name: "LeafletMap",
  props: {
    stations: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      map: null,
      markersLayer: null,
      viewMode: "2d",
      cesiumViewer: null
    };
  },
  mounted() {
    this.initLeaflet();
    this.loadCesiumScript().then(() => {
      console.log("CesiumJS loaded.");
    });
  },
  methods: {
    // Add this helper method to normalize station coordinates
    getNormalizedCoords(station) {
      return {
        lat: station.latitude || station.lat,
        lon: station.longitude || station.lon,
        name: station.name
      };
    },

    calculateCenter() {
      if (!this.stations || this.stations.length === 0) return [13.736717, 100.523186];
      
      const coordinates = this.stations.map(this.getNormalizedCoords);
      const lats = coordinates.map(c => c.lat);
      const lons = coordinates.map(c => c.lon);
      
      const centerLat = lats.reduce((a, b) => a + b, 0) / lats.length;
      const centerLon = lons.reduce((a, b) => a + b, 0) / lons.length;
      
      return [centerLat, centerLon];
    },

    calculateBounds() {
      if (!this.stations || this.stations.length === 0) return null;
      
      const coordinates = this.stations.map(this.getNormalizedCoords);
      const lats = coordinates.map(c => c.lat);
      const lons = coordinates.map(c => c.lon);
      
      const minLat = Math.min(...lats);
      const maxLat = Math.max(...lats);
      const minLon = Math.min(...lons);
      const maxLon = Math.max(...lons);
      
      return [[minLat, minLon], [maxLat, maxLon]];
    },

    updateMapView() {
      if (!this.map) return;
      
      const bounds = this.calculateBounds();
      if (bounds) {
        this.map.fitBounds(bounds, {
          padding: [50, 50],
          maxZoom: 16
        });
      } else {
        const center = this.calculateCenter();
        this.map.setView(center, 13);
      }
    },

    initLeaflet() {
      if (typeof L === 'undefined') {
        console.error('Leaflet not loaded!');
        return;
      }

      const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors'
      });

      const topo = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenTopoMap contributors'
      });

      const carto = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; CartoDB'
      });

      this.map = L.map("map2d", {
        center: this.calculateCenter(),
        zoom: 13,
        layers: [osm]
      });

      const baseLayers = {
        "OpenStreetMap": osm,
        "TopoMap": topo,
        "Carto Light": carto
      };

      L.control.layers(baseLayers).addTo(this.map);

      this.markersLayer = L.layerGroup().addTo(this.map);
      this.stations.forEach(station => {
        L.marker([station.latitude, station.longitude])
          .addTo(this.markersLayer)
          .bindPopup(station.name);
      });
    },

    updateMarkers() {
      if (!this.map || !this.markersLayer) return;
      
      this.markersLayer.clearLayers();
      
      this.stations.forEach(station => {
        const coords = this.getNormalizedCoords(station);
        if (coords.lat && coords.lon) {
          L.marker([coords.lat, coords.lon])
            .addTo(this.markersLayer)
            .bindPopup(coords.name);
        }
      });

      this.updateMapView();
    },

    async loadCesiumScript() {
      if (typeof Cesium !== "undefined") return;

      const script = document.createElement("script");
      script.src = "https://unpkg.com/cesium@1.116.0/Build/Cesium/Cesium.js";
      script.onload = () => {
        this.$nextTick(() => {
          this.initCesium();
        });
      };

      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/cesium@1.116.0/Build/Cesium/Widgets/widgets.css";

      document.head.appendChild(link);
      document.body.appendChild(script);
    },

    initCesium() {
      if (this.cesiumViewer || typeof Cesium === 'undefined') return;

      // ✅ Apply your token before using any Cesium APIs
      Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI2NGNmODc0My03ODI2LTRkNGYtYWU5My0zYWM5MTU1OGE4NjgiLCJpZCI6MzIyNzEyLCJpYXQiOjE3NTI4MzE4ODd9.1oKKgaweBEEAU1pI-c_edzK7od6aBtD-0WEQsItJkl0";

      this.cesiumViewer = new Cesium.Viewer("map3d", {
        timeline: false,
        animation: false,
        sceneModePicker: true,
        baseLayerPicker: true
      });

      this.stations.forEach(station => {
        this.cesiumViewer.entities.add({
          position: Cesium.Cartesian3.fromDegrees(station.longitude, station.latitude),
          point: {
            pixelSize: 10,
            color: Cesium.Color.BLUE
          },
          label: {
            text: station.name,
            font: "14px sans-serif",
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM
          }
        });
      });

      this.cesiumViewer.zoomTo(this.cesiumViewer.entities);
    },

    updateCesiumView() {
      if (!this.cesiumViewer || this.stations.length === 0) return;

      try {
        // Clear existing entities
        this.cesiumViewer.entities.removeAll();

        // Add station markers
        this.stations.forEach(station => {
          const coords = this.getNormalizedCoords(station);
          if (coords.lat && coords.lon) {
            this.cesiumViewer.entities.add({
              position: Cesium.Cartesian3.fromDegrees(coords.lon, coords.lat),
              point: {
                pixelSize: 10,
                color: Cesium.Color.BLUE
              },
              label: {
                text: coords.name,
                font: "14px sans-serif",
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM
              }
            });
          }
        });

        // Zoom to entities
        if (this.cesiumViewer.entities.values.length > 0) {
          this.cesiumViewer.zoomTo(this.cesiumViewer.entities);
        }
      } catch (error) {
        console.error('Error updating Cesium view:', error);
      }
    }
  },
  watch: {
    stations: {
      handler(newStations) {
        if (!newStations || newStations.length === 0) return;
        
        if (this.viewMode === '2d') {
          this.updateMarkers();
        } else if (this.cesiumViewer) {
          this.updateCesiumView();
        }
      },
      deep: true
    },
    viewMode(newMode) {
      if (newMode === "3d" && !this.cesiumViewer && typeof Cesium !== 'undefined') {
        this.initCesium();
      }
    }
  }
};
</script>