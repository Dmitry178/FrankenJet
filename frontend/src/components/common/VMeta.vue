<template>
  <head>
    <title>{{ title }}</title>
    <meta name="description" :content="description">
    <meta name="keywords" :content="keywords">
  </head>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  description?: string;
  keywords?: string;
}>();
</script>
