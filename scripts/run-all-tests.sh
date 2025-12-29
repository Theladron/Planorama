#!/bin/bash
# Script to run both backend and frontend tests

BACKEND_EXIT_CODE=0
FRONTEND_EXIT_CODE=0

echo "=========================================="
echo "Running Backend Tests (pytest)"
echo "=========================================="
cd /app
pytest -v || BACKEND_EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Running Frontend Tests (Vitest)"
echo "=========================================="
cd /app/frontend/react
npm test -- --coverage || FRONTEND_EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
if [ $BACKEND_EXIT_CODE -eq 0 ] && [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    [ $BACKEND_EXIT_CODE -ne 0 ] && echo "  - Backend tests failed (exit code: $BACKEND_EXIT_CODE)"
    [ $FRONTEND_EXIT_CODE -ne 0 ] && echo "  - Frontend tests failed (exit code: $FRONTEND_EXIT_CODE)"
    exit 1
fi

