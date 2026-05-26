FROM nginx:alpine

# Copy the static file to the nginx html directory as a template
COPY index.html /etc/nginx/templates/index.html.template

# Install envsubst (it comes with nginx:alpine)
# Define the CMD to replace variables and start nginx
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/templates/index.html.template > /usr/share/nginx/html/index.html && nginx -g 'daemon off;'"]

# Expose port 80
EXPOSE 80
