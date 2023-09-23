from node:18-alpine

COPY . .

RUN npm install
RUN npm install react-scripts -g

EXPOSE 3000

CMD ["npm", "run", "start"]
