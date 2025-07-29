from fastapi import APIRouter
from app.core.middleware import limiter, RATE_LIMITING_ENABLED

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Chatbot SaaS Platform API is running"}


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