# Test Suite

Comprehensive test suite for AWS Solution Architect Tool covering backend API, services, and frontend components.

## Structure

```
tests/
├── test_api.py                    # API endpoint tests (unit tests with mocks)
├── test_session_manager.py         # Session manager tests
├── test_cloudformation_parser.py   # CloudFormation parser tests
├── test_question_classifier.py    # Question classifier tests
├── test_follow_up_detector.py     # Follow-up detector tests
├── test_context_extractor.py      # Context extractor tests
├── test_quality_validator.py      # Quality validator tests
├── test_adaptive_prompt_generator.py  # Prompt generator tests
├── test_integration.py            # Integration tests (real service logic)
├── test_integration_mcp.py        # MCP integration tests (real MCP servers)
├── requirements.txt               # Test dependencies
└── pytest.ini                     # Pytest configuration

frontend/src/
├── services/
│   └── api.test.ts                # API service tests
└── components/
    ├── ChatInterface.test.tsx     # Chat interface tests
    ├── ModeSelector.test.tsx      # Mode selector tests
    └── ConversationInput.test.tsx # Input component tests
```

## Running Tests

### Backend Tests

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestRootEndpoints

# Run with verbose output
pytest -v

# Run integration tests (tests real service integration)
pytest tests/test_integration.py -v

# Run MCP integration tests (requires MCP servers running)
pytest tests/test_integration_mcp.py --test-mcp -v

# Run all tests except MCP tests
pytest -m "not mcp"
```

### Frontend Tests

```bash
cd frontend

# Install dependencies (if not already installed)
npm install

# Run tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

## Test Coverage

The test suite covers:

### Backend
- ✅ API endpoints (root, health, brainstorm, analyze, generate, follow-up)
- ✅ Session management (creation, updates, expiration, cleanup)
- ✅ CloudFormation template parsing and deployment instructions
- ✅ Question classification and intent detection
- ✅ Follow-up question detection
- ✅ Context extraction (services, topics, summaries)
- ✅ Quality validation (citations, tool usage, completeness)
- ✅ Adaptive prompt generation
- ✅ Error handling and edge cases
- ✅ **Integration tests** - Real service integration without mocking business logic
- ✅ **MCP integration tests** - Tests with real MCP servers (optional, use `--test-mcp` flag)

### Frontend
- ✅ API service methods (brainstorm, analyze, generate, follow-up)
- ✅ Chat interface component
- ✅ Mode selector component
- ✅ Conversation input component
- ✅ Error handling
- ✅ User interactions

## Test Principles

- **Minimalist**: Tests focus on essential functionality
- **Co-located**: Tests live next to the code they test
- **Fast**: Tests run quickly without external dependencies where possible
- **Isolated**: Each test is independent and can run in any order
- **Clear**: Test names describe what is being tested

## Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- Before deploying to production

## Coverage Goals

- **Backend**: 70%+ coverage on core logic
- **Frontend**: 60%+ coverage on components and services
- **Critical paths**: 90%+ coverage (API endpoints, session management)
