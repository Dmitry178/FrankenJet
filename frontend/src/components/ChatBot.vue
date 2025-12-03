<template>
  <v-card
    v-if="isOpen"
    class="chat-bot-card"
    :class="{ 'chat-bot-card--mobile': $vuetify.display.smAndDown }"
    elevation="10"
    rounded="lg"
    width="370"
    style="position: fixed; bottom: 20px; right: 20px; z-index: 9998; max-height: 60vh; overflow-y: auto;"
  >
    <!-- Заголовок -->
    <v-card-title class="d-flex align-center pa-3">
      <v-icon size="large" color="primary" class="mr-2">mdi-airplane</v-icon>
      <span class="font-weight-bold">Авиабот</span>
      <v-spacer></v-spacer>
      <v-btn icon size="small" @click="toggleChat">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>

    <v-divider></v-divider>

    <!-- Область переписки -->
    <v-card-text class="pa-3 d-flex flex-column" style="flex: 1 1 auto; min-height: 0;">
      <div
        ref="chatMessagesContainer"
        class="chat-messages-inner"
        :class="mobile ? 'chat-messages-mobile' : 'chat-messages-desktop'"
        style="overflow-y: auto;"
      >
        <div v-for="(msg, index) in messages" :key="index" class="mb-2">
          <div
            v-if="msg.sender === 'bot'"
            class="d-flex align-start mb-1"
          >
            <v-avatar size="32" color="primary" class="mr-2">
              <RobotIcon size="18" color="white" />
            </v-avatar>
            <div
              class="bg-secondary text-white rounded-lg d-inline-block"
              style="
                border-radius: 1px 16px 16px 16px !important;
                white-space: normal;
                max-width: 80%;
                overflow: hidden;
                word-break: break-word;
                padding: 8px 12px;
                line-height: 1.5;
                font-size: 0.875rem;
              "
            >
              {{ msg.text }}
            </div>
          </div>
          <div
            v-else
            class="d-flex align-start mb-1"
          >
            <v-spacer></v-spacer>
            <div
              class="bg-secondary text-white rounded-lg d-inline-block"
              style="
                border-radius: 16px 1px 16px 16px !important;
                white-space: normal;
                max-width: 80%;
                overflow: hidden;
                word-break: break-word;
                padding: 8px 12px;
                line-height: 1.5;
                font-size: 0.875rem;
              "
            >
              {{ msg.text }}
            </div>
            <v-avatar size="32" color="primary" class="ml-2">
              <v-icon size="18" color="white">mdi-account</v-icon>
            </v-avatar>
          </div>
        </div>
      </div>
    </v-card-text>

    <v-divider></v-divider>

    <!-- Поле ввода -->
    <v-card-text class="pa-3 pt-2">
      <v-textarea
        ref="chatInputRef"
        v-model="userInput"
        placeholder="Написать сообщение..."
        variant="outlined"
        density="compact"
        hide-details
        @keydown.enter.prevent="sendMessage"
        append-inner-icon="mdi-send"
        :maxlength="200"
        rows="2"
        no-resize
        autocomplete="off"
        class="chat-input-area"
        :disabled="isInputDisabled"
        @click:append-inner="sendMessage"
      ></v-textarea>
      <div class="text-caption text-right mt-0">
        {{ userInput.length }} / 200
      </div>
    </v-card-text>
  </v-card>

  <!-- Кнопка вызова чат-бота -->
  <v-btn
    v-if="!isOpen"
    fab
    icon
    color="secondary"
    class="chat-bot-fab"
    @click="toggleChat"
    fixed
    bottom
    right
    style="z-index: 9999; bottom: 85px !important; right: 23px !important;"
  >
    <RobotIcon size="26" />
  </v-btn>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { useChatStore } from '@/stores/chat';
import { useWebSocketStore } from '@/stores/websocket';
import { useDisplay } from 'vuetify';
import axios from 'axios';
import RobotIcon from '@/components/RobotIcon.vue';

const isOpen = ref(false);
const userInput = ref('');
const messages = ref([]);
const isInputDisabled = ref(false);
const chatMessagesContainer = ref(null);
const chatInputRef = ref(null);

const chatStore = useChatStore();
const wsStore = useWebSocketStore();
const { mobile } = useDisplay();
const currentChatId = computed(() => chatStore.chatId);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    const id = chatStore.initializeChatId();
    wsStore.connect(id);
    nextTick(() => scrollToBottom());
  } else {
    wsStore.disconnect(currentChatId.value);
  }
};

const welcomeMessage = () => {
  messages.value = [{
    sender: 'bot',
    text: 'Привет! Я - Авиабот, я могу отвечать по вопросам авиации'
  }];
};

const loadChatHistory = async (chatId) => {
  try {
    const response = await axios.get(`/chat/history/${chatId}`);
    if (response.data.status === 'ok') {
      messages.value = [];

      if (response.data.data && response.data.data.length > 0) {
        response.data.data.forEach(item => {
          // сообщение пользователя
          messages.value.push({
            sender: 'user',
            text: item.message
          });

          // ответ бота
          messages.value.push({
            sender: 'bot',
            text: item.answer
          });
        });
      } else {
        welcomeMessage();
      }

      await nextTick(() => scrollToBottom());
    } else {
      console.error('Ошибка при получении истории чата:', response.data);
      welcomeMessage();
    }
  } catch (error) {
    console.error('Ошибка при загрузке истории чата:', error);
    welcomeMessage();
  }
};

const sendMessage = () => {
  if (!userInput.value.trim() || isInputDisabled.value) return;

  if (!wsStore.isConnected) {
    messages.value.push({
      sender: 'bot',
      text: 'Сервис временно недоступен ⚠️'
    });
    scrollToBottom();
    return;
  }

  // добавление сообщения пользователя
  messages.value.push({
    sender: 'user',
    text: userInput.value.trim()
  });

  // подготовка и отправка сообщения
  const messageData = {
    type: 'message',
    message: userInput.value.trim()
  };
  wsStore.send(JSON.stringify(messageData));
  isInputDisabled.value = true;

  userInput.value = '';
  scrollToBottom();
};

const handleWebSocketMessage = (event) => {
  try {
    const data = JSON.parse(event.detail.data);

    if (data.type === 'answer') {
      messages.value.push({
        sender: 'bot',
        text: data.text
      });

      isInputDisabled.value = false;
      scrollToBottom();

      nextTick(() => {
        if (chatInputRef.value) {
          chatInputRef.value.focus();
        }
      });
    } else if (data.type === 'system') {
      console.log('System message:', data.message);
    }
  } catch (e) {
    console.error('Error parsing WebSocket message:', e);
    messages.value.push({
      sender: 'bot',
      text: `Ошибка: ${event.detail.data}`
    });
    isInputDisabled.value = false;
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesContainer.value) {
      chatMessagesContainer.value.scrollTop = chatMessagesContainer.value.scrollHeight;
    }
  });
};

onMounted(() => {
  window.addEventListener('websocket_message', handleWebSocketMessage);
  loadChatHistory(chatStore.initializeChatId());
});

onUnmounted(() => {
  window.removeEventListener('websocket_message', handleWebSocketMessage);
});
</script>

<style scoped>
.chat-bot-card {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.chat-bot-card--mobile {
  width: 100vw !important;
  height: 100vh !important;
  right: 0 !important;
  left: 0 !important;
  bottom: 0 !important;
  top: 0 !important;
  max-height: none !important;
  position: fixed !important;
  z-index: 9998 !important;
  border-radius: 0 !important;
}

.chat-bot-fab {
  position: fixed !important;
  bottom: 85px !important;
  right: 23px !important;
  z-index: 9999;
}

.chat-messages-inner {
  height: 100%;
  overflow-y: auto;
}

.chat-messages-desktop {
  height: 350px !important;
}

.chat-messages-mobile {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-input-area {
  & ::v-deep(.v-field__input) {
    -webkit-box-shadow: none !important;
    box-shadow: none !important;
  }
}
</style>
