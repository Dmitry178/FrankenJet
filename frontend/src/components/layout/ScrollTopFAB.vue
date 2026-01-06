<template>
  <v-btn
    v-show="showScrollTop"
    fab
    icon
    color="secondary"
    class="scroll-top-btn"
    :class="{ 'final-fab-position': isFinalPosition }"
    @click="scrollToTop"
    fixed
    bottom
    right
  >
    <v-icon>mdi-arrow-up</v-icon>
  </v-btn>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  name: 'ScrollTopFAB',
  props: {
    isFinalPosition: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const showScrollTop = ref(false);
    const scrollTimer = ref(null);

    const scrollToTop = () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    };

    const handleScroll = () => {
      showScrollTop.value = window.scrollY > 300;

      if (scrollTimer.value) {
        clearTimeout(scrollTimer.value);
      }

      if (window.scrollY > 300) {
        showScrollTop.value = true;
      }
    };

    onMounted(() => {
      window.addEventListener('scroll', handleScroll);
    });

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll);
    });

    return {
      showScrollTop,
      scrollToTop,
    };
  },
};
</script>

<style scoped>
.scroll-top-btn {
  z-index: 9998;
}

.scroll-top-btn:not(.final-fab-position) {
  bottom: 90px !important;
  right: 20px !important;
  position: fixed !important;
}

.scroll-top-btn.final-fab-position {
  bottom: 30px !important;
  right: 20px !important;
  position: fixed !important;
}
</style>
