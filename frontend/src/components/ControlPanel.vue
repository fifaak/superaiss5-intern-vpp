<template>
  <div>
    <form @submit.prevent="submitForecast">
      <div class="mb-3">
        <label for="inputX" class="form-label">X Input (JSON)</label>
        <textarea class="form-control" id="inputX" v-model="xInput" rows="6" required></textarea>
      </div>

      <div class="mb-3" v-if="needEdgeIndex">
        <label for="edgeIndex" class="form-label">Edge Index (JSON)</label>
        <textarea class="form-control" id="edgeIndex" v-model="edgeIndex" rows="3"></textarea>
      </div>

      <div class="form-check mb-3">
        <input class="form-check-input" type="checkbox" id="toggleEdgeIndex" v-model="needEdgeIndex">
        <label class="form-check-label" for="toggleEdgeIndex">
          Requires Edge Index
        </label>
      </div>

      <div class="d-flex gap-2">
        <button class="btn btn-secondary" type="button" @click="pasteSampleData">
          Paste Sample Data
        </button>
        <button class="btn btn-primary" type="submit">
          Submit
        </button>
      </div>
    </form>

    <div v-if="result" class="mt-4">
      <h5>Predictions:</h5>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ControlPanel',
  data() {
    return {
      xInput: '',
      edgeIndex: '',
      needEdgeIndex: true,
      result: null,
    };
  },
  methods: {
    async submitForecast() {
      try {
        const body = {
          X: JSON.parse(this.xInput),
        };
        if (this.needEdgeIndex) {
          body.edge_index = JSON.parse(this.edgeIndex);
        }

        const res = await fetch('http://localhost:8000/forecast', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        const json = await res.json();
        this.result = JSON.stringify(json, null, 2);
      } catch (err) {
        this.result = `Error: ${err.message}`;
      }
    },
    pasteSampleData() {
      const seqLen = 96;
      this.xInput = JSON.stringify(
        [
          [
            [Array(seqLen).fill(0.1)],
            [Array(seqLen).fill(0.2)],
            [Array(seqLen).fill(0.3)],
            [Array(seqLen).fill(0.4)],
            [Array(seqLen).fill(0.5)],
            [Array(seqLen).fill(0.6)]
          ]
        ],
        null,
        2
      );

      this.edgeIndex = JSON.stringify(
        [
          [0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4],
          [1, 2, 3, 4, 5, 0, 2, 3, 4, 0, 1, 3, 0, 1, 0]
        ],
        null,
        2
      );
    },
  },
};
</script>