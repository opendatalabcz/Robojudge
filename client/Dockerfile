from node:18-alpine

COPY package*.json ./

RUN npm install
RUN npm install react-scripts -g

COPY . .

EXPOSE 3000

CMD ["npm", "run", "start"]
