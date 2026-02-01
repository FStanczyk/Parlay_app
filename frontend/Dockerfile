FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Railway automatically makes REACT_APP_* env vars available during build
# But we need to ensure they're available - Railway should inject them automatically
# Debug: Check what env vars are available
RUN printenv | grep REACT_APP || echo "No REACT_APP vars found"

# Build the app (environment variables are embedded at build time)
# Railway should automatically pass REACT_APP_API_URL to the build process
RUN npm run build

# Install serve to run the app
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the app
CMD ["serve", "-s", "build", "-l", "3000"]
