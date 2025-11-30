import { defineStore } from 'pinia';
import { ref } from 'vue';

const getWsProtocol = () => window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE_URL = `${getWsProtocol()}//${window.location.host}`;

export const useWebSocketStore = defineStore('websocket', () => {
  const ws = ref(null);
  const isConnected = ref(false);
  let currentChatId = ref(null); // добавим локальное хранилище chatId в store

  const connect = (chatId) => {
    // если уже есть подключение, отключаем старое соединение
    if (ws.value) {
      disconnect(currentChatId.value); // передача старого chatId
    }

    const wsUrl = `${WS_BASE_URL}/ws/${chatId}`;
    ws.value = new WebSocket(wsUrl);
    currentChatId.value = chatId;

    ws.value.onopen = () => {
      isConnected.value = true;
    };

    ws.value.onmessage = (event) => {
      window.dispatchEvent(new CustomEvent('websocket_message', { detail: event }));
    };

    ws.value.onclose = (event) => {
      // проверка, закрылось ли соединение по нашей просьбе (code 1000) или из-за ошибки/сервера
      if (event.code !== 1000) {
        // console.log('WebSocket disconnected unexpectedly:', event.reason);
        reconnect(currentChatId.value);
      } else {
        // console.log('WebSocket closed normally for chat_id:', currentChatId.value);
      }
      isConnected.value = false;
      ws.value = null;
      currentChatId.value = null; // сброс chatId при закрытии
    };

    ws.value.onerror = (error) => {
      // console.error('WebSocket error:', error);
    };
  };

  const disconnect = (chatId) => {
    // проверяем, что мы отключаемся от правильного chatId
    if (ws.value && currentChatId.value === chatId) {
      ws.value.close(1000, "Client disconnected");
    }
  };

  const send = (message) => {
    if (ws.value && isConnected.value) {
      ws.value.send(message);
    } else {
      console.warn('WebSocket not connected');
    }
  };

  // метод для переподключения
  const reconnect = (chatId) => {
    setTimeout(() => connect(chatId), 1000);
  };

  return {
    ws,
    isConnected,
    connect,
    disconnect,
    send
  };
});
