#!/bin/bash

echo "🚀 Initializing NerdMatch database with test data..."
echo "======================================================"

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready on bolt://neo4j:7687..."
for i in {1..60}; do
  if timeout 1 bash -c "cat < /dev/null > /dev/tcp/neo4j/7687" 2>/dev/null; then
    echo "✅ Neo4j is reachable!"
    break
  fi
  printf "."
  sleep 1
done

echo ""
echo "📊 Running database initialization..."

# Run the initialization
cd /app
python create_test_profiles.py

echo ""
echo "✅ Database initialization complete!"
echo "======================================================"
echo "Ready to start Flask application..."
