FROM node:20-alpine AS base

WORKDIR /app

# Install dependencies first to maximize layer caching.
COPY package*.json ./
RUN npm ci

FROM base AS dev

# Live-reload development server target.
COPY . .
EXPOSE 4200
CMD ["npm", "run", "start", "--", "--host", "0.0.0.0", "--port", "4200", "--poll", "1000"]

FROM base AS build

# Build optimized production assets.
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS production

# Angular builder outputs static assets to dist/<project>/browser by default.
COPY --from=build /app/dist/airpas/browser /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
