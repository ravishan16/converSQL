# NLP to SQL - Makefile
# Professional development utilities for the Streamlit application

.PHONY: help clean clean-cache clean-logs start dev install test lint format check-deps

# Default target
help:
	@echo "🔍 NLP to SQL - Development Commands"
	@echo "=================================="
	@echo ""
	@echo "📱 Application Commands:"
	@echo "  start        Start Streamlit app on port 8501 with logs"
	@echo "  dev          Start in development mode with auto-reload"
	@echo ""
	@echo "🧹 Cleanup Commands:"
	@echo "  clean        Clean all cache files and temporary data"
	@echo "  clean-cache  Remove Python cache files (__pycache__, .pyc)"
	@echo "  clean-logs   Remove log files"
	@echo ""
	@echo "🛠️  Development Commands:"
	@echo "  install      Install dependencies from requirements.txt"
	@echo "  test         Run tests (if available)"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with black"
	@echo "  check-deps   Check for dependency updates"
	@echo ""
	@echo "Usage: make <command>"

# Start Streamlit application with logging
start:
	@echo "🚀 Starting NLP to SQL Streamlit App..."
	@echo "📍 URL: http://localhost:8501"
	@echo "📝 Logs will be displayed below..."
	@echo "=================================="
	streamlit run app.py --server.port 8501 --logger.level debug

# Development mode with auto-reload
dev:
	@echo "🛠️  Starting in Development Mode..."
	@echo "📍 URL: http://localhost:8501"
	@echo "🔄 Auto-reload enabled"
	@echo "=================================="
	streamlit run app.py --server.port 8501 --logger.level debug --server.runOnSave true

# Clean all cache and temporary files
clean: clean-cache clean-logs
	@echo "🧹 Cleaning all temporary files..."
	@find . -type f -name "*.tmp" -delete 2>/dev/null || true
	@find . -type f -name "*.temp" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Clean Python cache files
clean-cache:
	@echo "🧹 Cleaning Python cache files..."
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ Python cache cleaned!"

# Clean log files
clean-logs:
	@echo "🧹 Cleaning log files..."
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name "*.out" -delete 2>/dev/null || true
	@echo "✅ Log files cleaned!"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Run tests (if test files exist)
test:
	@echo "🧪 Running tests..."
	@if [ -d "tests" ] || ls test_*.py 1> /dev/null 2>&1; then \
		python -m pytest -v; \
	else \
		echo "⚠️  No tests found. Create test files to enable testing."; \
	fi

# Run linting
lint:
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 app.py --max-line-length=88 --ignore=E203,W503; \
	else \
		echo "⚠️  flake8 not installed. Run: pip install flake8"; \
	fi

# Format code
format:
	@echo "✨ Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black app.py --line-length=88; \
	else \
		echo "⚠️  black not installed. Run: pip install black"; \
	fi

# Check for dependency updates
check-deps:
	@echo "🔍 Checking for dependency updates..."
	@if command -v pip-check >/dev/null 2>&1; then \
		pip-check; \
	else \
		echo "⚠️  pip-check not installed. Run: pip install pip-check"; \
		echo "📋 Current installed packages:"; \
		pip list --outdated; \
	fi

# Quick setup for new development environment
setup: install clean
	@echo "🎉 Setup completed! Ready for development."
	@echo ""
	@echo "Quick start:"
	@echo "  make start    # Start the application"
	@echo "  make dev      # Start in development mode"
	@echo "  make help     # Show all available commands"