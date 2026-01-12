<template>
  <v-breadcrumbs :items="items">
    <template v-slot:item="{ item }">
      <v-breadcrumbs-item :href="item.href" :disabled="item.disabled">
        {{ item.title }}
      </v-breadcrumbs-item>
    </template>
  </v-breadcrumbs>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ title: string; href: string; disabled?: boolean }>;
}>();
</script>
