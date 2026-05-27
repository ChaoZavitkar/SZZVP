#!/bin/bash

echo "🚀 NerdMatch initialization script"
echo "=================================="

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
for i in {1..30}; do
  if nc -z neo4j 7687 2>/dev/null; then
    echo "✅ Neo4j is ready!"
    break
  fi
  echo "  Attempt $i/30..."
  sleep 2
done

# Check if database needs initialization
echo "📊 Checking database status..."

# Run Flask app in background
echo "🌐 Starting Flask application..."
exec python app.py
