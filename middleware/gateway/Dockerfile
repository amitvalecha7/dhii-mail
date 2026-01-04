FROM nginxinc/nginx-unprivileged:alpine

COPY nginx.conf /etc/nginx/nginx.conf

# Create a simple index.html for the root
USER root
RUN echo "<h1>Dhii Mail API Gateway</h1>" > /usr/share/nginx/html/index.html
USER nginx
