<template>
  <v-dialog v-model="model" max-width="900">
    <v-card>
      <v-img
        :src="src"
        :alt="alt"
        max-height="80vh"
        contain
      />
      <v-card-text v-if="captionTitle || captionDescription" class="pt-2 pb-0">
        <div class="modal-image-caption">
          <h4 v-if="captionTitle" class="text-h6 font-weight-medium mb-1">
            {{ captionTitle }}
          </h4>
          <p v-if="captionDescription" class="text-body-2 text--secondary mb-0">
            {{ captionDescription }}
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="closeModal" icon>
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
const model = defineModel();

defineProps({
  src: String,
  alt: String,
  captionTitle: String,
  captionDescription: String,
});

const closeModal = () => {
  model.value = false;
};
</script>

<style scoped>
.modal-image-caption {
  text-align: center;
  padding: 0.5rem 0 0 0;
}

.modal-image-caption h4 {
  margin: 0;
}

.modal-image-caption p {
  margin: 0;
  opacity: 0.8;
}
</style>
