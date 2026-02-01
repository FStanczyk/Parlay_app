FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Make sure environment variables are available during build
# Railway will inject REACT_APP_* variables automatically
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Build the app (environment variables are embedded at build time)
RUN npm run build

# Install serve to run the app
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the app
CMD ["serve", "-s", "build", "-l", "3000"]
