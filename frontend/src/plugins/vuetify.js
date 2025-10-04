import { createVuetify } from 'vuetify'
import vuetifyConfig from '@/vuetify.config'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles';

export default createVuetify({
  ...vuetifyConfig,
  components,
  directives,
})
