import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import * as dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import advancedFormat from "dayjs/plugin/advancedFormat";

dayjs.extend(utc);
dayjs.extend(advancedFormat);

// Vuetify
import "@mdi/font/css/materialdesignicons.css"; // Ensure you are using css-loader
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import { WebSocketClient } from "@/class/WebSocketClient";

// https://github.com/vitejs/vite/discussions/3143#discussioncomment-3031909
if (import.meta.hot) {
  import.meta.hot.on(
    "vite:beforeUpdate",
    /* eslint-disable-next-line no-console */
    () => console.clear()
  );
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    // defaultTheme: "dark",
  },
});

const app = createApp(App);

app.use(vuetify);
app.use(router);

new WebSocketClient(
  new WebSocket(`ws://${import.meta.env.VITE_CENTRAL_HOST}:8765`),
  new Map(),
  app,
  true
);

app.mount("#app");
