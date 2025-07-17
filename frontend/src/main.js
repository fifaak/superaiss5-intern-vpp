import { createApp } from 'vue'
import App from './App.vue'
import 'bootstrap/dist/css/bootstrap.min.css'  // ✅ Import Bootstrap CSS
import 'bootstrap'                              // ✅ Import Bootstrap JS

createApp(App).mount('#app')