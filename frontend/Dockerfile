FROM node:26-alpine AS base
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

FROM base AS development
COPY . .
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS builder
COPY . .
RUN ["npm", "run", "build"]

FROM nginx:alpine AS production

COPY --from=builder /app/dist /app/www
COPY nginx.conf /etc/nginx/templates/default.conf.template

ENV NGINX_ENVSUBST_TEMPLATE_DIR=/etc/nginx/templates
ENV NGINX_ENVSUBST_TEMPLATE_SUFFIX=.template
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d
ENV PORT=80