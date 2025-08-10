FROM nginx:1.29.0-alpine

COPY ./index.html /usr/share/nginx/html/index.html
COPY ./app.js /usr/share/nginx/html/app.js

CMD ["nginx", "-g", "daemon off;"]