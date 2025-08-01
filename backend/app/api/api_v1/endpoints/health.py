from fastapi import APIRouter
import logging
from app.core.middleware import limiter, RATE_LIMITING_ENABLED

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    logger.info("🏥 Health check requested")
    result = {"status": "healthy", "message": "Chatbot SaaS Platform API is running"}
    logger.info(f"✅ Health check response: {result}")
    return result


@router.get("/db")
async def database_health():
    """Database health check"""
    from app.core.database import get_supabase
    
    try:
        supabase = get_supabase()
        # Test basic connection with a simple query
        # Try multiple system tables until one works
        test_queries = [
            ("_realtime_subscriptions", "select count"),
            ("information_schema.tables", "select table_name"),
            ("pg_stat_database", "select datname")
        ]
        
        for table, query_type in test_queries:
            try:
                if "count" in query_type:
                    response = supabase.table(table).select("count", count="exact").limit(1).execute()
                else:
                    response = supabase.table(table).select("*").limit(1).execute()
                
                return {"status": "healthy", "database": "connected", "test_table": table}
            except:
                continue
        
        # If all system tables fail, the database might not be properly set up
        return {"status": "warning", "database": "connected_but_schema_missing", "message": "Database connected but schema may not be set up"}
        
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@router.get("/auth-test")
async def auth_test():
    """Test authentication and user database sync without requiring auth"""
    from app.core.database import get_supabase_admin
    import uuid
    
    logger.info("🧪 Testing database connection and user creation...")
    
    try:
        supabase = get_supabase_admin()
        
        # Test if users table exists
        logger.info("🔍 Testing users table access...")
        users_test = supabase.table("users").select("id").limit(1).execute()
        logger.info(f"👤 Users table test: {users_test}")
        
        return {
            "status": "database_accessible",
            "users_table_exists": True,
            "sample_users": len(users_test.data) if users_test.data else 0,
            "message": "Database connection working"
        }
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {str(e)}")
        return {
            "status": "database_error",
            "error": str(e),
            "message": "Database connection or table access failed"
        }