# Stage 1: Build
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Use a custom nginx config if needed, or stick to default for port 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
