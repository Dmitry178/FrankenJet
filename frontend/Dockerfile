FROM node:20-alpine

WORKDIR /app

ARG API_BASE_URL
ARG S3_BASE_URL
ENV VITE_API_BASE_URL=$API_BASE_URL
ENV VITE_S3_BASE_URL=$S3_BASE_URL

COPY package*.json ./
RUN npm install
COPY ./public /app/public
COPY ./src /app/src
COPY ./vite.config.js /app/vite.config.js
COPY ./index.html /app/index.html

RUN npm run build

FROM nginx:alpine

COPY --from=0 /app/dist /usr/share/nginx/html

# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
