FROM node:alpine

WORKDIR /app
COPY public/ ./public
COPY src/ ./src
COPY package.json ./

RUN npm install

CMD ["npm", "start"]

# docker image build -t server-hub-image:latest .
# docker run -it -p 8000:3000 --name server-hub-container server-hub-image:latest