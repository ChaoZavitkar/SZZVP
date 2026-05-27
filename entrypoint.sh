#!/bin/bash
set -e

echo "🚀 NerdMatch Flask Entrypoint"
echo "=============================="

# Check if INIT_DB is set
if [ "$INIT_DB" = "true" ]; then
    echo "📊 Initializing database with test data..."

    # Wait for Neo4j
    echo "⏳ Waiting for Neo4j to be ready..."
    for i in {1..60}; do
        if timeout 2 python -c "from models.database import get_db; get_db()" 2>/dev/null; then
            echo "✅ Neo4j is ready!"
            break
        fi
        echo "  Attempt $i/60..."
        sleep 2
    done

    # Run initialization
    echo "Running profile initialization..."
    python create_test_profiles.py
    echo "✅ Database initialization complete!"
fi

echo ""
echo "🌐 Starting Flask application..."
python app.py
