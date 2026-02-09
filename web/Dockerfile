FROM node:20-alpine3.19
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
EXPOSE 40080
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "40080"]
