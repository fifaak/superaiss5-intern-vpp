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
        center: [51.505, -0.09],
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
    }
  },
  watch: {
    viewMode(newMode) {
      if (newMode === "3d" && !this.cesiumViewer && typeof Cesium !== 'undefined') {
        this.initCesium();
      }
    }
  }
};
</script>