.PHONY: sync
sync:
	cd frontend && npm install
	cd server && uv sync

.PHONY: serve
serve:
	cd frontend && npm run dev

.PHONY: dev
dev:
	@echo "🚀 Starting Job Application Tracker in development mode..."
	@echo "📱 Frontend: http://localhost:3000"
	@echo "🔧 Backend: http://localhost:8000"
	@echo "🗄️  Database: MongoDB (ensure it's running)"
	@echo ""
	@echo "Voice command examples:"
	@echo "- 'Add Google Software Engineer in Mountain View'"
	@echo "- 'Update status to applied for Microsoft'"
	@echo "- 'Show me all applications from last week'"
	@echo ""
	cd frontend && npm run dev

.PHONY: server
server:
	@echo "🔧 Starting backend server..."
	cd server && uv run server.py

.PHONY: frontend
frontend:
	@echo "📱 Starting frontend development server..."
	cd frontend && npm run dev

.PHONY: build
build:
	@echo "🏗️  Building frontend for production..."
	cd frontend && npm run build

.PHONY: start
start:
	@echo "🚀 Starting production server..."
	cd frontend && npm start

.PHONY: clean
clean:
	@echo "🧹 Cleaning up..."
	cd frontend && rm -rf .next node_modules
	cd server && rm -rf __pycache__ .pytest_cache

.PHONY: setup
setup:
	@echo "⚙️  Setting up Job Application Tracker..."
	@echo "📝 Creating .env file if it doesn't exist..."
	@if [ ! -f ".env" ]; then \
		echo "# OpenAI API Configuration" > .env; \
		echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env; \
		echo "" >> .env; \
		echo "# Database Configuration" >> .env; \
		echo "MONGODB_URI=mongodb://localhost:27017" >> .env; \
		echo "DATABASE_NAME=job_tracker" >> .env; \
		echo "✅ Created .env file. Please update OPENAI_API_KEY with your actual API key."; \
	else \
		echo "✅ .env file already exists."; \
	fi
	@echo "📦 Installing dependencies..."
	$(MAKE) sync
	@echo ""
	@echo "🎉 Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Update OPENAI_API_KEY in .env file"
	@echo "2. Start MongoDB (if not already running): mongod"
	@echo "3. Run the application: make dev"
	@echo "4. Open http://localhost:3000 in your browser"
	@echo ""

.PHONY: help
help:
	@echo "Job Application Tracker - Available Commands:"
	@echo ""
	@echo "  make setup     - Initial setup (creates .env, installs dependencies)"
	@echo "  make sync      - Install/update dependencies"
	@echo "  make dev       - Start both frontend and backend in development"
	@echo "  make frontend  - Start only frontend development server"
	@echo "  make server    - Start only backend server"
	@echo "  make build     - Build frontend for production"
	@echo "  make start     - Start production server"
	@echo "  make clean     - Clean up build artifacts and dependencies"
	@echo "  make help      - Show this help message"
	@echo ""
	@echo "Voice command examples:"
	@echo "- 'Add Google Software Engineer in Mountain View'"
	@echo "- 'Update status to applied for Microsoft'"
	@echo "- 'Show me all applications from last week'"

