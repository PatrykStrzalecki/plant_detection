FROM nginx:1.29.0-alpine

COPY ./frontend/index.html /usr/share/nginx/html/index.html
COPY ./frontend/app.js /usr/share/nginx/html/app.js

CMD ["nginx", "-g", "daemon off;"]