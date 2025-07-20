<template>
  <div>
    <div class="btn-group mb-2">
      <button class="btn btn-primary" @click="switchTo2D">2D (Leaflet)</button>
      <button class="btn btn-secondary" @click="switchTo3D">3D (Cesium)</button>
    </div>

    <div v-show="viewMode === '2d'" id="map2d" style="height: 500px; width: 100%;"></div>
    <div v-show="viewMode === '3d'" id="map3d" style="height: 500px; width: 100%;"></div>
  </div>
</template>

<script>
export default {
  name: "LeafletCesiumMap",
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
    switchTo2D() {
      this.viewMode = "2d";
      this.$nextTick(() => {
        if (this.map) this.map.invalidateSize();
      });
    },
    switchTo3D() {
      this.viewMode = "3d";
      this.$nextTick(() => {
        if (!this.cesiumViewer && typeof Cesium !== "undefined") {
          this.initCesium();
        }
      });
    },
    initLeaflet() {
      if (typeof L === 'undefined') {
        console.error('Leaflet not loaded!');
        return;
      }

      const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors'
      });

      this.map = L.map("map2d", {
        center: [13.736717, 100.523186],
        zoom: 13,
        layers: [osm]
      });

      this.markersLayer = L.layerGroup().addTo(this.map);
      this.addLeafletMarkers();
    },
    addLeafletMarkers() {
      if (!this.map || !this.markersLayer) return;

      this.markersLayer.clearLayers();

      this.stations.forEach(station => {
        const lat = station.latitude || station.lat;
        const lon = station.longitude || station.lon;
        if (lat && lon) {
          L.marker([lat, lon])
            .addTo(this.markersLayer)
            .bindPopup(station.name);
        }
      });
    },
    async loadCesiumScript() {
      if (typeof Cesium !== "undefined") return;

      const script = document.createElement("script");
      script.src = "https://unpkg.com/cesium@1.116.0/Build/Cesium/Cesium.js";
      script.onload = () => this.initCesium();

      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/cesium@1.116.0/Build/Cesium/Widgets/widgets.css";

      document.head.appendChild(link);
      document.body.appendChild(script);
    },
    initCesium() {
      if (this.cesiumViewer || typeof Cesium === 'undefined') return;

      Cesium.Ion.defaultAccessToken = import.meta.env.VITE_CESIUM_ACCESS_TOKEN;

      this.cesiumViewer = new Cesium.Viewer("map3d", {
        timeline: false,
        animation: false,
        sceneModePicker: true,
        baseLayerPicker: true
      });

      this.addCesiumEntities();
    },
    addCesiumEntities() {
      if (!this.cesiumViewer) return;

      this.cesiumViewer.entities.removeAll();

      this.stations.forEach(station => {
        const lat = station.latitude || station.lat;
        const lon = station.longitude || station.lon;
        if (lat && lon) {
          this.cesiumViewer.entities.add({
            position: Cesium.Cartesian3.fromDegrees(lon, lat),
            billboard: {
              image: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
              width: 32,
              height: 32
            },
            label: {
              text: station.name,
              font: "14px sans-serif",
              verticalOrigin: Cesium.VerticalOrigin.BOTTOM
            }
          });
        }
      });

      this.cesiumViewer.zoomTo(this.cesiumViewer.entities);
    }
  },
  watch: {
    stations: {
      handler() {
        if (this.viewMode === "2d") {
          this.addLeafletMarkers();
        } else if (this.viewMode === "3d" && this.cesiumViewer) {
          this.addCesiumEntities();
        }
      },
      deep: true
    }
  }
};
</script>