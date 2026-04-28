FROM node:20-alpine
WORKDIR /app
COPY package*.json yarn.lock* ./
RUN npm install --production || yarn install --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
