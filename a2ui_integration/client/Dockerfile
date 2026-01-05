FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port (Vite default is 5173, but we use 3001 in docker-compose)
EXPOSE 3001

# Start command (host 0.0.0.0 is needed for Docker networking)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]
