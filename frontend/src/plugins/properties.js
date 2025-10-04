import axios from 'axios';

const DEFAULT_IMAGE = '/aircraft.svg';

export function setupProperties(app) {
  app.config.globalProperties.$axios = axios;
  app.config.globalProperties.$defaultImage = DEFAULT_IMAGE;
}
