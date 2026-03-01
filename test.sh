#!/bin/bash
# Test runner for PixelFort

set -e

echo "🧪 Running PixelFort Test Suite"
echo "================================"
echo ""

# Run tests in Docker container
docker-compose exec -T api pytest tests/ \
    -v \
    --tb=short \
    --color=yes \
    --cov=api \
    --cov-report=term-missing

echo ""
echo "================================"
echo "✅ Tests complete!"