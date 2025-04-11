import type { App } from "vue";

class WebSocketClient {
  ws: WebSocket;
  stateUpdateMap: Map<string, Function>;

  constructor(
    ws: WebSocket,
    stateUpdateMap: Map<string, Function>,
    app: App<any>,
    shouldRetry: boolean
  ) {
    this.ws = ws;
    this.stateUpdateMap = stateUpdateMap;
    const thiz = this;

    this.ws.onerror = (e) => {
      console.error(e);
    };

    this.ws.onopen = (event) => {
      console.log(event);
    };

    this.ws.onclose = (event) => {
      console.log(event);
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("Ws message", message);
      const func = thiz.stateUpdateMap.get(message.message_type);
      func ? func(message.payload) : null;
    };
    app.config.globalProperties.ws = this.ws;
    app.config.globalProperties.stateUpdateMap = stateUpdateMap;
  }
}

export { WebSocketClient };
