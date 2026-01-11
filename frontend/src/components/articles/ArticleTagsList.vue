<template>
  <div v-if="tags && tags.length > 0" class="mt-4">
    <h4 class="text-h6 mb-2">Теги</h4>
    <div class="tag-chips-wrapper">
      <v-chip
        v-for="tag in tags"
        :key="tag"
        class="mr-2 mb-2 tag-chip"
        size="small"
        variant="outlined"
        @click="$emit('tag-click', tag)"
      >
        {{ tag }}
      </v-chip>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ArticleTagsList',
  props: {
    tags: Array,
  },
  emits: ['tag-click'],
};
</script>

<style scoped>
.tag-chips-wrapper {

}
.tag-chip {
  cursor: pointer;
}
</style>
