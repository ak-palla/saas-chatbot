# Phase 1 Testing Guide

## Overview
This directory contains comprehensive test files to validate your Phase 1 implementation of the Chatbot SaaS platform.

**📁 All test files are now organized in the `tests/` directory.**

## Test Files

### 1. `tests/quick_test.py` - Basic Validation
- Tests server connectivity
- Validates core endpoints
- Checks authentication protection
- **Run time**: ~5 seconds

### 2. `tests/test_phase1.py` - Comprehensive Testing
- Full end-to-end testing
- Creates test user and data
- Tests all CRUD operations
- Validates authentication flow
- Cleans up test data
- **Run time**: ~30 seconds

### 3. `tests/test_diagnostics.py` - Diagnostic Tool
- Identifies common issues
- Provides troubleshooting guidance
- **Run time**: ~3 seconds

### 4. `run_tests.bat` - Test Runner (Windows)
- Runs both quick and comprehensive tests
- Easy to use batch file

## Prerequisites

1. **Server Running**: Make sure your FastAPI server is running:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Install Requests**: The tests use the `requests` library:
   ```bash
   pip install requests
   ```

3. **Database Setup**: For full testing, your Supabase database should be configured with the schema from `database.sql`

## Running Tests

### Method 1: Use the Batch File (Windows)
```cmd
run_tests.bat
```

### Method 2: Manual Execution
```bash
# Diagnostic tool (run first to identify issues)
python tests/test_diagnostics.py

# Quick test (basic validation)
python tests/quick_test.py

# Comprehensive test (full functionality)
python tests/test_phase1.py
```

## Test Coverage

### ✅ What Gets Tested

#### API Endpoints
- `GET /` - Root endpoint
- `GET /api/v1/health/` - Health check
- `GET /api/v1/health/db` - Database health
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Current user info
- `GET /api/v1/chatbots/` - List chatbots
- `POST /api/v1/chatbots/` - Create chatbot
- `GET /api/v1/chatbots/{id}` - Get specific chatbot
- `PUT /api/v1/chatbots/{id}` - Update chatbot
- `DELETE /api/v1/chatbots/{id}` - Delete chatbot
- `POST /api/v1/conversations/` - Create conversation
- `GET /api/v1/conversations/chatbot/{id}` - Get conversations
- `DELETE /api/v1/conversations/{id}` - Delete conversation

#### Functionality
- User registration and authentication
- JWT token generation and validation
- CRUD operations for chatbots
- CRUD operations for conversations
- Database connectivity
- Authentication protection
- Error handling
- Data cleanup

### ⚠️ What's NOT Tested (Phase 2+)
- Chat completion endpoints
- Document upload and processing
- Vector embeddings
- RAG functionality
- Voice processing (STT/TTS)
- Payment processing
- Rate limiting (when Redis is unavailable)

## Expected Results

### Quick Test
```
🧪 Quick Phase 1 Test
==============================
✅ Root endpoint: Chatbot SaaS Platform API
✅ Health check: healthy
✅ Database health: healthy
✅ API documentation accessible
✅ Authentication protection working

🎯 Quick test completed!
```

### Comprehensive Test (Sample)
```
🧪 Starting Phase 1 Comprehensive Tests
==================================================
--- Server Connection ---
✅ Server is running and accessible

--- User Registration ---  
✅ User registered successfully: test_123@example.com

--- Create Chatbot ---
✅ Chatbot created: Test Chatbot (ID: abc-123)

🏁 Phase 1 Test Results:
✅ Passed: 13
❌ Failed: 0
📊 Total: 13
🎉 All tests passed! Phase 1 implementation is working correctly.
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Make sure the FastAPI server is running
   - Check that it's running on `http://localhost:8000`

2. **Database Health Fails**
   - Verify Supabase credentials in `.env`
   - Check that Supabase project is active
   - Ensure database schema is created

3. **Authentication Errors**
   - Verify JWT secret key is set
   - Check Supabase auth configuration

4. **Import Errors**
   - Install missing dependencies: `pip install requests`
   - Ensure virtual environment is activated

### Getting Help

If tests fail:
1. Check the detailed error messages
2. Verify your `.env` configuration
3. Confirm database schema is properly set up
4. Check server logs for detailed errors

## Next Steps

Once all Phase 1 tests pass:
1. Move on to Phase 2 implementation (Text Chatbot Service)
2. Add chat completion endpoints
3. Implement document processing and RAG functionality

## Test Data

The comprehensive test creates:
- A test user with random email
- A test chatbot
- A test conversation

All test data is automatically cleaned up after testing.