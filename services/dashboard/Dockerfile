FROM node:20-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG VITE_GATEWAY_HTTP=http://localhost:8000
ARG VITE_GATEWAY_WS=ws://localhost:8000
ENV VITE_GATEWAY_HTTP=$VITE_GATEWAY_HTTP
ENV VITE_GATEWAY_WS=$VITE_GATEWAY_WS
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
