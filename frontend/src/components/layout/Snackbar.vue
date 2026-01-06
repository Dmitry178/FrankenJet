<template>
  <v-snackbar
    v-model="snackbarState.show"
    location="top"
    :color="snackbarState.color"
    :timeout="snackbarState.timeout"
  >
    {{ snackbarState.message }}
  </v-snackbar>
</template>

<script>
import { snackbarState } from '@/composables/useSnackbar';

export default {
  name: 'Snackbar',
  setup() {
    return {
      snackbarState
    };
  }
};
</script>
