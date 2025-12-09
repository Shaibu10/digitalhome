#!/bin/bash
# Render build script - runs after dependencies are installed

echo "=========================================="
echo "Running build phase tasks..."
echo "=========================================="

# Initialize database
echo "Initializing database..."
python init_db.py

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed!"
    exit 1
fi

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
