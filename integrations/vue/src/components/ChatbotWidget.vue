<template>
  <div 
    ref="widgetContainer"
    :class="[
      'chatbot-widget-container',
      `chatbot-theme-${config.theme}`,
      `chatbot-position-${config.position}`,
      { 'chatbot-loading': isLoading, 'chatbot-error': error }
    ]"
    :style="containerStyle"
  >
    <!-- Loading State -->
    <div v-if="isLoading" class="chatbot-loading-overlay">
      <div class="chatbot-spinner"></div>
      <span class="chatbot-loading-text">{{ loadingText }}</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="chatbot-error-overlay">
      <div class="chatbot-error-icon">⚠️</div>
      <span class="chatbot-error-text">{{ error }}</span>
      <button @click="retry" class="chatbot-retry-button">
        {{ retryText }}
      </button>
    </div>

    <!-- Widget Content -->
    <div v-else class="chatbot-widget-content">
      <slot :chatbot="chatbotInstance" :state="state">
        <!-- Default widget will be rendered here by the script -->
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  ref, 
  computed, 
  onMounted, 
  onUnmounted, 
  watch, 
  inject,
  nextTick
} from 'vue';
import type { ChatbotConfig, ChatbotEvents } from '../index';
import { useChatbot } from '../composables/useChatbot';

// Props
interface Props extends ChatbotConfig, ChatbotEvents {
  loadingText?: string;
  retryText?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  baseUrl: 'https://api.yourchatbot.com',
  theme: 'light',
  position: 'bottom-right',
  primaryColor: '#3b82f6',
  secondaryColor: '#1f2937',
  borderRadius: 12,
  autoOpen: false,
  autoOpenDelay: 3000,
  showAvatar: true,
  enableSound: true,
  enableTypingIndicator: true,
  enableFileUpload: false,
  enableVoice: false,
  maxWidth: 400,
  maxHeight: 600,
  mobileFullScreen: true,
  zIndex: 999999,
  loadingText: 'Loading chatbot...',
  retryText: 'Retry',
  disabled: false,
});

// Emits
const emit = defineEmits<{
  open: [];
  close: [];
  message: [message: string];
  error: [error: Error];
  ready: [];
}>();

// Global config injection
const globalConfig = inject<ChatbotConfig>('chatbot-global-config', {});

// Merge configurations
const config = computed<ChatbotConfig>(() => ({
  ...globalConfig,
  ...props,
}));

// Refs
const widgetContainer = ref<HTMLElement>();
const chatbotInstance = ref<any>(null);

// Use chatbot composable
const {
  state,
  isLoading,
  error,
  loadScript,
  initializeWidget,
  destroyWidget,
} = useChatbot(config.value);

// Computed styles
const containerStyle = computed(() => ({
  '--chatbot-primary-color': config.value.primaryColor,
  '--chatbot-secondary-color': config.value.secondaryColor,
  '--chatbot-border-radius': `${config.value.borderRadius}px`,
  '--chatbot-max-width': `${config.value.maxWidth}px`,
  '--chatbot-max-height': `${config.value.maxHeight}px`,
  '--chatbot-z-index': config.value.zIndex,
  ...(config.value.customCss && { '--chatbot-custom-css': config.value.customCss }),
}));

// Methods
const retry = async () => {
  if (props.disabled) return;
  
  try {
    await initializeWidget(widgetContainer.value!);
  } catch (err) {
    console.error('Failed to retry chatbot initialization:', err);
  }
};

const openChatbot = () => {
  if (chatbotInstance.value) {
    chatbotInstance.value.open();
  }
};

const closeChatbot = () => {
  if (chatbotInstance.value) {
    chatbotInstance.value.close();
  }
};

const sendMessage = (message: string) => {
  if (chatbotInstance.value) {
    chatbotInstance.value.sendMessage(message);
  }
};

// Lifecycle
onMounted(async () => {
  if (props.disabled || !config.value.chatbotId) return;

  try {
    await loadScript();
    await nextTick();
    
    if (widgetContainer.value) {
      const instance = await initializeWidget(widgetContainer.value, {
        onOpen: () => {
          emit('open');
          props.onOpen?.();
        },
        onClose: () => {
          emit('close');
          props.onClose?.();
        },
        onMessage: (message: string) => {
          emit('message', message);
          props.onMessage?.(message);
        },
        onError: (err: Error) => {
          emit('error', err);
          props.onError?.(err);
        },
      });
      
      chatbotInstance.value = instance;
      emit('ready');
    }
  } catch (err) {
    console.error('Failed to initialize chatbot:', err);
  }
});

onUnmounted(() => {
  destroyWidget();
});

// Watch for config changes
watch(
  () => config.value,
  async (newConfig, oldConfig) => {
    if (props.disabled) return;
    
    // Reinitialize if critical config changed
    const criticalProps = ['chatbotId', 'baseUrl'];
    const shouldReinitialize = criticalProps.some(
      prop => newConfig[prop as keyof ChatbotConfig] !== oldConfig[prop as keyof ChatbotConfig]
    );
    
    if (shouldReinitialize && widgetContainer.value) {
      destroyWidget();
      await nextTick();
      await retry();
    } else if (chatbotInstance.value) {
      // Update non-critical config
      chatbotInstance.value.updateConfig?.(newConfig);
    }
  },
  { deep: true }
);

// Expose methods to parent
defineExpose({
  open: openChatbot,
  close: closeChatbot,
  sendMessage,
  retry,
  instance: chatbotInstance,
  state,
});
</script>

<style scoped>
.chatbot-widget-container {
  position: relative;
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.chatbot-loading-overlay,
.chatbot-error-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  min-height: 200px;
}

.chatbot-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--chatbot-primary-color, #3b82f6);
  border-top: 3px solid transparent;
  border-radius: 50%;
  animation: chatbot-spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes chatbot-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.chatbot-loading-text,
.chatbot-error-text {
  color: var(--chatbot-secondary-color, #1f2937);
  font-size: 14px;
  margin-bottom: 1rem;
}

.chatbot-error-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.chatbot-retry-button {
  background: var(--chatbot-primary-color, #3b82f6);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--chatbot-border-radius, 12px);
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.2s;
}

.chatbot-retry-button:hover {
  opacity: 0.9;
}

.chatbot-retry-button:active {
  transform: translateY(1px);
}

/* Theme variations */
.chatbot-theme-dark {
  --chatbot-secondary-color: #f3f4f6;
}

.chatbot-theme-dark .chatbot-loading-text,
.chatbot-theme-dark .chatbot-error-text {
  color: var(--chatbot-secondary-color);
}

/* Position classes for absolute positioning */
.chatbot-position-bottom-right {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: var(--chatbot-z-index, 999999);
}

.chatbot-position-bottom-left {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: var(--chatbot-z-index, 999999);
}

.chatbot-position-top-right {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: var(--chatbot-z-index, 999999);
}

.chatbot-position-top-left {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: var(--chatbot-z-index, 999999);
}

/* Responsive design */
@media (max-width: 768px) {
  .chatbot-widget-container {
    max-width: var(--chatbot-max-width, 400px);
    max-height: var(--chatbot-max-height, 600px);
  }
}

/* Custom CSS injection */
.chatbot-widget-container[style*="--chatbot-custom-css"] {
  /* Custom CSS will be applied via the style attribute */
}
</style>
