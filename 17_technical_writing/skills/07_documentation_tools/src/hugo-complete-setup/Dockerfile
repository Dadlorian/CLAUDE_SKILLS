FROM klakegg/hugo:latest as builder

WORKDIR /src

# Copy site content
COPY . .

# Build the site
RUN hugo --minify --destination=/target

# Use nginx for serving
FROM nginx:1.25-alpine

# Copy built site
COPY --from=builder /target /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
