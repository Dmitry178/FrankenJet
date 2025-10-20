import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth.js';

const getWsProtocol = () => window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE_URL = `${getWsProtocol()}//${window.location.host}`;
// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const useWebSocketStore = defineStore('websocket', () => {
  const ws = ref(null);
  const isConnected = ref(false);

  const getWebSocketUrl = (jti) => {
    // return API_BASE_URL.replace(/^http/, 'ws') + `/ws/${jti}`;
    return `${WS_BASE_URL}/ws/${jti}`;
  };

  const connect = async () => {
    const authStore = useAuthStore();

    if (!authStore.jti) {
      console.error('No jti available');
      return;
    }

    const wsUrl = getWebSocketUrl(authStore.jti);
    ws.value = new WebSocket(wsUrl);

    ws.value.onopen = () => {
      isConnected.value = true;
      console.log('WebSocket connected');
    };

    ws.value.onmessage = (event) => {
      console.log('Message received:', event.data);
      // обработка сообщений
    };

    ws.value.onclose = () => {
      isConnected.value = false;
      console.log('WebSocket disconnected');
    };

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const disconnect = () => {
    if (ws.value) {
      ws.value.close();
      ws.value = null;
      isConnected.value = false;
    }
  };

  const send = (message) => {
    if (ws.value && isConnected.value) {
      ws.value.send(message);
    } else {
      console.warn('WebSocket not connected');
    }
  };

  return {
    ws,
    isConnected,
    connect,
    disconnect,
    send
  };
});
