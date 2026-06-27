FROM node:20-alpine

WORKDIR /workspace

# Install dependencies first to optimize docker caching layers
COPY package.json /workspace/
RUN npm install

# Copy source code
COPY . /workspace/

EXPOSE 5173

# Run Vite dev server bound to all network interfaces
CMD ["npm", "run", "dev"]
