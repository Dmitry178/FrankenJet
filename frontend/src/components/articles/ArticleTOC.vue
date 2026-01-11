<template>
  <div v-if="items.length > 0" class="toc-wrapper">
    <v-card class="toc-card" elevation="0">
      <v-card-title>Содержание</v-card-title>
      <v-card-text>
        <ul class="toc-list">
          <li
            v-for="item in items"
            :key="item.id"
            :class="{ 'active': activeId === item.id }"
          >
            <a href="#" @click.prevent="$emit('item-click', item.id)">
              {{ item.text }}
            </a>
          </li>
        </ul>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'ArticleTableOfContents',
  props: {
    items: Array,
    activeId: String,
  },
  emits: ['item-click'],
};
</script>

<style scoped>
.toc-wrapper {
  position: sticky;
  top: 64px; /* высота тулбара */
  height: calc(100vh - 64px);
  width: 300px;
  overflow-y: auto;
  padding: 0;
}

.toc-card {
  padding: 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-list li {
  cursor: pointer;
  font-size: 0.9rem;
}

.toc-list li:hover {
  text-decoration: underline;
}

.toc-list li.active a {
  font-weight: bold;
}

.toc-list a {
  text-decoration: none;
  color: inherit;
  display: block;
  padding: 4px 0;
}

@media (max-width: 768px) {
  .toc-wrapper {
    display: none !important;
  }
}
</style>
