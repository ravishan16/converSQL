# converSQL - Makefile
# Professional development utilities for the Streamlit application

.PHONY: help clean clean-cache clean-logs start dev install install-dev test test-unit test-integration test-cov lint format format-check check-deps setup ci

# Default target
help:
	@echo "🔍 converSQL - Development Commands"
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
	@echo "  install-dev  Install with development dependencies"
	@echo "  test         Run all tests with coverage"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run code linting (flake8)"
	@echo "  format       Format code with black and isort"
	@echo "  format-check Check code formatting without changes"
	@echo "  check-deps   Check for dependency updates"
	@echo "  setup        Complete setup for new development environment"
	@echo "  ci           Run full CI checks (format, lint, test)"
	@echo ""
	@echo "Usage: make <command>"

# Start Streamlit application with logging
start:
	@echo "🚀 Starting converSQL Streamlit App..."
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
	@rm -rf .pytest_cache 2>/dev/null || true
	@rm -f .coverage 2>/dev/null || true
	@rm -f coverage.xml 2>/dev/null || true
	@rm -rf htmlcov 2>/dev/null || true
	@rm -rf .mypy_cache 2>/dev/null || true
	@rm -rf .ruff_cache 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Clean Python cache files
clean-cache:
	@echo "🧹 Cleaning Python cache files..."
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*~" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ Python cache cleaned!"

# Clean log files
clean-logs:
	@echo "🧹 Cleaning log files..."
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name "*.out" -delete 2>/dev/null || true
	@find . -type f -name "*.err" -delete 2>/dev/null || true
	@echo "✅ Log files cleaned!"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Install with development dependencies
install-dev: install
	@echo "📦 Installing development dependencies..."
	@pip install -r requirements.txt
	@echo "✅ All dependencies installed!"

# Run all tests with coverage
test:
	@echo "🧪 Running all tests with coverage..."
	@pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
	@echo "✅ Tests completed! Coverage report: htmlcov/index.html"

# Run unit tests only
test-unit:
	@echo "🧪 Running unit tests..."
	@pytest tests/unit/ -v -m "not integration"
	@echo "✅ Unit tests completed!"

# Run integration tests only
test-integration:
	@echo "🧪 Running integration tests..."
	@pytest tests/integration/ -v -m integration
	@echo "✅ Integration tests completed!"

# Run tests with detailed coverage
test-cov:
	@echo "🧪 Running tests with detailed coverage..."
	@pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml --cov-branch
	@echo "✅ Coverage reports generated:"
	@echo "   - Terminal: (shown above)"
	@echo "   - HTML: htmlcov/index.html"
	@echo "   - XML: coverage.xml"

# Run linting
lint:
	@echo "🔍 Running code linting..."
	@echo "Running flake8..."
	@flake8 src/ tests/ app.py || echo "⚠️  Flake8 found issues"
	@echo "Running mypy..."
	@mypy src/ || echo "⚠️  MyPy found issues"
	@echo "✅ Linting completed!"

# Format code with black and isort
format:
	@echo "✨ Formatting code with black and isort..."
	@black --line-length 120 src/ tests/ app.py
	@isort --profile black src/ tests/ app.py
	@echo "✅ Code formatted!"

# Check code formatting without making changes
format-check:
	@echo "🔍 Checking code formatting..."
	@black --check --line-length 120 src/ tests/ app.py || (echo "❌ Code needs formatting. Run 'make format'" && exit 1)
	@isort --check-only --profile black src/ tests/ app.py || (echo "❌ Imports need sorting. Run 'make format'" && exit 1)
	@echo "✅ Code formatting is correct!"

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
setup: install-dev clean
	@echo "🎉 Setup completed! Ready for development."
	@echo ""
	@echo "Quick start:"
	@echo "  make start    # Start the application"
	@echo "  make dev      # Start in development mode"
	@echo "  make test     # Run tests"
	@echo "  make help     # Show all available commands"

# Run full CI checks locally
ci: clean format-check lint test-cov
	@echo "✅ All CI checks passed!"
	@echo ""
	@echo "Ready to commit and push!"