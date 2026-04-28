FROM node:20-alpine
WORKDIR /app
COPY site/package*.json ./
RUN npm install --production
COPY site/ .
ENV PORT=80
EXPOSE 80
CMD ["sh", "-c", "npm start || node src/index.js || node index.js || node server.js"]
