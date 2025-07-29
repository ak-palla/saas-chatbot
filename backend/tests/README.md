# Test Directory

This directory contains the comprehensive test suite for Phase 1 backend implementation.

## Test Files

### 1. `test_phase1.py` - Main Test Suite
- **Purpose**: Complete test suite for all Phase 1 functionality
- **What it tests**: All API endpoints, authentication, database operations, configuration
- **Run with**: `python tests/test_phase1.py`

### 2. `conftest.py` - Test Configuration
- **Purpose**: Test configuration and path setup
- **What it does**: Ensures proper Python path configuration for tests

## Additional Test File

### `test_phase1_complete.py` (in backend root)
- **Purpose**: Enhanced comprehensive test suite with detailed logging
- **What it tests**: Everything in test_phase1.py plus additional diagnostics
- **Run with**: `python test_phase1_complete.py`

## Running Tests

### Quick Start
```bash
# Navigate to backend directory
cd /path/to/backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Run comprehensive test suite
python test_phase1_complete.py
```

### Alternative Test
```bash
# Run original Phase 1 tests
python tests/test_phase1.py
```

### Using Batch Files (Windows)
```cmd
# Run all tests
run_tests.bat

# Check database schema
check_database.bat
```

## Test Requirements

1. **FastAPI server must be running** on `http://localhost:8000`
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Environment variables must be set** in `.env` file:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY` 
   - `SUPABASE_SERVICE_KEY`
   - `GROQ_API_KEY`
   - `DEEPGRAM_API_KEY`
   - `JWT_SECRET_KEY`

3. **Database schema must be set up** in Supabase:
   - Run `setup_database.sql` in Supabase SQL Editor
   - Vector extension should be enabled

## Expected Results

### All Tests Passing
When everything is working correctly, you should see:
```
🎉 All tests passed! Phase 1 implementation is complete and working!
✅ Passed: 16/16
📈 Success Rate: 100.0%
```

### Test Categories Covered
1. **📋 Configuration & Environment Tests**
   - Environment variables validation
   - Database connectivity
   - Schema verification

2. **🌐 API Endpoint Tests**
   - Health check endpoint

3. **🔐 Authentication Tests**
   - User registration
   - User login
   - Authentication protection
   - Current user retrieval

4. **🤖 Chatbot Tests**
   - Create, read, update, delete chatbots
   - List user's chatbots

5. **💬 Conversation Tests**
   - Create conversations
   - List conversations
   - Send messages

6. **🧹 Cleanup Operations**
   - Automatic test data cleanup

## Common Issues

1. **Server not running**: Start with `uvicorn app.main:app --reload`
2. **Database connection failed**: Check Supabase credentials in `.env`
3. **Schema errors**: Run `setup_database.sql` in Supabase SQL Editor
4. **Import errors**: Ensure virtual environment is activated and dependencies installed
5. **Vector extension issues**: Enable vector extension in Supabase

## File Structure After Cleanup

```
tests/
├── README.md              # This file
├── __init__.py            # Package initialization
├── conftest.py            # Test configuration
└── test_phase1.py         # Main test suite

backend/
├── test_phase1_complete.py # Comprehensive test suite
├── setup_database.sql      # Database schema setup
├── database.sql           # Alternative database setup
└── run_tests.bat          # Windows batch file
```

The test directory has been cleaned up to focus on essential testing functionality while maintaining comprehensive coverage of all Phase 1 features.