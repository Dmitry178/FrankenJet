import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useChatStore = defineStore('chat', () => {
  const chatId = ref(null);

  const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  const initializeChatId = () => {
    if (!chatId.value) {
      const storedChatId = localStorage.getItem('chat_id');
      if (storedChatId) {
        chatId.value = storedChatId;
      } else {
        chatId.value = generateUUID();
        localStorage.setItem('chat_id', chatId.value);
      }
    }
    return chatId.value;
  };

  const resetChatId = () => {
    chatId.value = null;
    localStorage.removeItem('chat_id');
  };

  const processText = (text) => {
    if (typeof text !== 'string') {
      return text;
    }
    const telegramLinkRegex = /\[([^\[\]]+)\]\(\s*(https?:\/\/[^\s)]+)\s*\)/g;
    return text.replace(telegramLinkRegex, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  };

  return {
    chatId,
    initializeChatId,
    resetChatId,
    processText,
  };
});
