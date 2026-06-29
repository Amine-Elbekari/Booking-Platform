FROM node:22-alpine AS base

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

#  Development stage
FROM base AS development
ENV NODE_ENV=development
EXPOSE 5173
# passing --host 0.0.0.0 via the CLI ensures container accessibilit
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production Stage

FROM base AS builder
ENV NODE_ENV=production
RUN npm run build

FROM nginx:1.31-alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "deamon off;"]e