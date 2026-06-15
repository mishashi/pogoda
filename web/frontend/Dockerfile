FROM node:20-alpine AS build-stage

WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Удаляем возможные конфликтующие файлы (чистая установка)
RUN npm ci || npm install

# Копируем исходники
COPY . .

# Даём права на выполнение для бинарников (особенно для vite)
RUN chmod +x node_modules/.bin/*

# Собираем проект
RUN npm run build

# Этап 2: сервер nginx для отдачи статики
FROM nginx:stable-alpine AS production-stage

# Копируем собранные файлы из предыдущего этапа
COPY --from=build-stage /app/dist /usr/share/nginx/html

# (Опционально) копируем кастомный конфиг nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
