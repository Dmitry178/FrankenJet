<template>
  <div class="rag-tab">
    <div class="text-center py-8">
      <v-icon size="96" color="primary" class="mb-4">mdi-database-search</v-icon>
      <h3 class="text-h5 mb-2">Настройки RAG</h3>
      <p class="text-body-1 text-medium-emphasis mb-4">
        Раздел в разработке
      </p>
      <p class="text-caption text-disabled mb-6">
        Здесь будут настройки для Retrieval-Augmented Generation:<br>
        индексация документов, настройки поиска, источники данных и т.д.
      </p>

      <v-divider class="my-6"></v-divider>

      <div class="features-list">
        <v-row>
          <v-col cols="12" md="4">
            <v-card variant="outlined" height="100%">
              <v-card-text class="text-center">
                <v-icon size="48" color="primary" class="mb-2 mt-6">mdi-file-document-multiple</v-icon>
                <div class="text-subtitle-2 mb-1">Управление документами</div>
                <div class="text-caption text-disabled">
                  Загрузка и индексация документов
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card variant="outlined" height="100%">
              <v-card-text class="text-center">
                <v-icon size="48" color="primary" class="mb-2 mt-6">mdi-magnify</v-icon>
                <div class="text-subtitle-2 mb-1">Настройки поиска</div>
                <div class="text-caption text-disabled">
                  Параметры семантического поиска
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card variant="outlined" height="100%">
              <v-card-text class="text-center">
                <v-icon size="48" color="primary" class="mb-2 mt-6">mdi-cog</v-icon>
                <div class="text-subtitle-2 mb-1">Конфигурация RAG</div>
                <div class="text-caption text-disabled">
                  Настройки релевантности и выборки
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

</script>

<style scoped>
.rag-tab {
  max-width: 900px;
  margin: 0 auto;
}

.features-list {
  max-width: 800px;
  margin: 0 auto;
}
</style>
