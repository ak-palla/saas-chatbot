# Database Setup Guide

## Why Set Up the Full Schema Now?

Setting up the complete database schema prevents issues that could compound later. Even though Phase 1 only uses basic tables, having the full schema ensures:

- ✅ No migration issues when moving to Phase 2
- ✅ Proper foreign key relationships established
- ✅ Vector extension properly configured for embeddings
- ✅ All indexes created for optimal performance
- ✅ Triggers and functions ready for advanced features

## Step-by-Step Setup

### Step 1: Access Supabase Dashboard

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project
3. Navigate to **SQL Editor** in the left sidebar

### Step 2: Execute the Database Schema

1. **Copy the entire content** from `setup_database.sql`
2. **Paste it** into the SQL Editor
3. **Click "Run"** to execute the script

**OR**

Use the original `database.sql` file if you prefer the simpler version.

### Step 3: Verify Schema Creation

Run the database schema verification tool **from the backend directory**:

```bash
# Make sure you're in the backend directory
cd D:\chat_service\backend

# Activate virtual environment
venv\Scripts\activate

# Run schema verification
python tests/test_database_schema.py

# Or use the batch file (Windows)
check_database.bat
```

### Step 4: Expected Output

You should see:
```
🔍 Starting Database Schema Verification
============================================================
✅ Passed: 5
❌ Failed: 0
📊 Total: 5
🎉 Database schema is properly set up!
```

## What Gets Created

### Tables
- **users** - User accounts and authentication
- **chatbots** - Chatbot configurations
- **conversations** - Chat history and sessions
- **documents** - Uploaded files (Phase 2)
- **vector_embeddings** - Text embeddings for RAG (Phase 2)
- **usage_records** - Usage tracking and billing

### Extensions
- **uuid-ossp** - UUID generation
- **vector** - Vector similarity search (for Phase 2)

### Indexes
- Email lookup index
- User-chatbot relationships
- Vector similarity search
- Usage tracking queries

### Functions & Triggers
- Automatic timestamp updates
- UUID generation
- Vector operations (Phase 2 ready)

## Verification Commands

### Manual Verification
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check extensions
SELECT extname FROM pg_extension;

-- Test basic operations
SELECT COUNT(*) FROM users;
```

### Automated Verification
```bash
# Run the complete verification
python tests/test_database_schema.py

# Or run all tests including schema verification
python run_tests.py
```

## Common Issues & Solutions

### Issue 1: Vector Extension Not Available
**Error:** `extension "vector" is not available`
**Solution:** Vector extension is only available in newer Supabase projects. If not available:
- Phase 1 will work fine without it
- Phase 2 will need vector extension for embeddings
- Consider upgrading your Supabase project

### Issue 2: Permission Errors
**Error:** `permission denied to create extension`
**Solution:** 
- Use the Supabase SQL Editor (has admin permissions)
- Don't run schema commands from application code

### Issue 3: Tables Already Exist
**Error:** `relation "users" already exists`
**Solution:**
- The `setup_database.sql` includes `DROP TABLE IF EXISTS` commands
- It will recreate tables cleanly
- **Warning:** This will delete existing data

### Issue 4: Foreign Key Violations
**Error:** `violates foreign key constraint`
**Solution:**
- Tables are created in the correct order
- Foreign keys are properly defined
- Use the provided schema files

## After Setup

Once the database schema is set up:

1. **Run the verification tool:**
   ```bash
   python tests/test_database_schema.py
   ```

2. **Run all tests:**
   ```bash
   python run_tests.py
   ```

3. **Check that Phase 1 tests pass:**
   - All 13 endpoints should work
   - Database health should show "healthy"
   - No more schema warnings

## Phase 2 Benefits

With the full schema in place, Phase 2 development will be smooth:
- Vector embeddings table ready
- Document storage configured
- Usage tracking operational
- No migration scripts needed

## Rollback (If Needed)

If you need to start fresh:

```sql
-- Drop all tables (in correct order)
DROP TABLE IF EXISTS usage_records CASCADE;
DROP TABLE IF EXISTS vector_embeddings CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS chatbots CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```

Then re-run the setup script.

## Next Steps

After successful database setup:
1. ✅ All Phase 1 functionality will work perfectly
2. ✅ Database health checks will pass
3. ✅ Ready for Phase 2 development
4. ✅ No more compound error issues

The investment in proper database setup now saves significant time and prevents issues later!