<template>
  <div id="map" style="height: 500px; width: 100%;"></div>
</template>

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
    };
  },
  mounted() {
    if (typeof L === 'undefined') {
      console.error('Leaflet not loaded!');
      return;
    }

    // Base layers
    const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenStreetMap contributors'
    });

    const topo = L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenTopoMap contributors'
    });

    const carto = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; CartoDB'
    });

    // Create map
    this.map = L.map("map", {
      center: [51.505, -0.09],
      zoom: 13,
      layers: [osm]  // Default base layer
    });

    // Layer control UI
    const baseLayers = {
      "OpenStreetMap": osm,
      "TopoMap": topo,
      "Carto Light": carto
    };

    L.control.layers(baseLayers).addTo(this.map);

    // Marker layer group
    this.markersLayer = L.layerGroup().addTo(this.map);

    this.stations.forEach(station => {
      L.marker([station.latitude, station.longitude])
        .addTo(this.markersLayer)
        .bindPopup(station.name);
    });
  }
};
</script>