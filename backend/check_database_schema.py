#!/usr/bin/env python3
"""
Database Schema Verification Script
Checks if the database schema matches the RAG system expectations
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def check_database_schema():
    """Check database schema for RAG components"""
    print("🗄️ Database Schema Verification")
    print("=" * 40)
    
    try:
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        print("\n1. 📋 Checking Documents Table...")
        
        # Check documents table structure
        try:
            # Try to get table info by selecting with expected columns
            documents_query = supabase.table("documents").select("id,filename,chatbot_id,user_id,file_type,file_size,processed,created_at,extracted_text").limit(1)
            result = documents_query.execute()
            
            print("  ✅ Documents table exists with all expected columns:")
            print("    - id, filename, chatbot_id, user_id")
            print("    - file_type, file_size, processed")
            print("    - created_at, extracted_text")
            
        except Exception as e:
            print(f"  ⚠️ Documents table issue: {e}")
            
            # Try without extracted_text column
            try:
                basic_query = supabase.table("documents").select("id,filename,chatbot_id,user_id,file_type,file_size,processed,created_at").limit(1)
                basic_result = basic_query.execute()
                print("  ✅ Documents table exists with basic columns")
                print("  ❌ Missing 'extracted_text' column - this will trigger immediate processing")
                
                print("\n  💡 To add extracted_text column, run:")
                print("     ALTER TABLE documents ADD COLUMN extracted_text TEXT;")
                
            except Exception as e2:
                print(f"  ❌ Documents table not accessible: {e2}")
                return False
        
        print("\n2. 🔢 Checking Vector Embeddings Table...")
        
        # Check vector_embeddings table
        try:
            vector_query = supabase.table("vector_embeddings").select("id,document_id,chunk_index,text_content,embedding,metadata,created_at").limit(1)
            vector_result = vector_query.execute()
            
            print("  ✅ Vector embeddings table exists with expected columns:")
            print("    - id, document_id, chunk_index")
            print("    - text_content, embedding, metadata")
            print("    - created_at")
            
            # Check if there are any existing embeddings
            count_query = supabase.table("vector_embeddings").select("id", count="exact").execute()
            embedding_count = count_query.count
            print(f"  📊 Current embeddings count: {embedding_count}")
            
            if embedding_count > 0:
                # Check embedding dimensions
                sample_query = supabase.table("vector_embeddings").select("embedding").limit(1).execute()
                if sample_query.data and sample_query.data[0].get('embedding'):
                    sample_embedding = sample_query.data[0]['embedding']
                    dimension = len(sample_embedding)
                    print(f"  📏 Sample embedding dimension: {dimension}")
                    
                    if dimension == 384:
                        print("  ✅ Embedding dimension matches expected (384)")
                    else:
                        print(f"  ⚠️ Embedding dimension mismatch: found {dimension}, expected 384")
            
        except Exception as e:
            print(f"  ❌ Vector embeddings table issue: {e}")
            print("  💡 You may need to run the vector setup SQL scripts")
            return False
        
        print("\n3. 🤖 Checking Chatbots Table...")
        
        # Check chatbots table (needed for RAG context filtering)
        try:
            chatbots_query = supabase.table("chatbots").select("id,user_id,name,system_prompt").limit(1).execute()
            print("  ✅ Chatbots table accessible")
            
            # Count chatbots
            count_query = supabase.table("chatbots").select("id", count="exact").execute()
            chatbot_count = count_query.count
            print(f"  📊 Current chatbots count: {chatbot_count}")
            
        except Exception as e:
            print(f"  ❌ Chatbots table issue: {e}")
            return False
        
        print("\n4. 🔗 Checking Foreign Key Relationships...")
        
        # Check if vector_embeddings properly references documents
        try:
            join_query = supabase.table("vector_embeddings") \
                .select("vector_embeddings.id, documents.filename") \
                .join("documents", "vector_embeddings.document_id", "documents.id") \
                .limit(1).execute()
            
            print("  ✅ Foreign key relationship working (vector_embeddings -> documents)")
            
        except Exception as e:
            print(f"  ⚠️ Foreign key relationship issue: {e}")
        
        print("\n5. 📊 Checking Vector Functions...")
        
        # Check if the match_documents function exists
        try:
            # Try to call the function with dummy data (this will fail but tell us if function exists)
            dummy_embedding = [0.0] * 384
            func_result = supabase.rpc("match_documents", {
                "query_embedding": dummy_embedding,
                "chatbot_id": "dummy-id",
                "match_threshold": 0.5,
                "match_count": 1
            }).execute()
            
            print("  ✅ match_documents function exists and callable")
            
        except Exception as e:
            error_msg = str(e).lower()
            if "function match_documents" in error_msg and "does not exist" in error_msg:
                print("  ❌ match_documents function does not exist")
                print("  💡 Run the vector setup SQL script to create the function")
            elif "invalid input syntax" in error_msg or "dummy-id" in error_msg:
                print("  ✅ match_documents function exists (expected error with dummy data)")
            else:
                print(f"  ⚠️ match_documents function issue: {e}")
        
        print("\n6. 🎯 RAG System Readiness Check...")
        
        # Overall readiness assessment
        print("  Checking overall system readiness...")
        
        ready = True
        issues = []
        
        # Check if we have documents with extracted text
        try:
            docs_with_text = supabase.table("documents").select("id").not_.is_("extracted_text", "null").limit(1).execute()
            if not docs_with_text.data:
                issues.append("No documents with extracted text found")
        except:
            issues.append("Cannot check for extracted text (column may not exist)")
        
        # Check if we have embeddings
        embeddings_count = supabase.table("vector_embeddings").select("id", count="exact").execute().count
        if embeddings_count == 0:
            issues.append("No vector embeddings found")
        
        # Check if we have active chatbots
        chatbots_count = supabase.table("chatbots").select("id", count="exact").execute().count
        if chatbots_count == 0:
            issues.append("No chatbots found")
        
        if issues:
            print("  ⚠️ RAG System Issues Found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("  ✅ RAG system appears ready")
        
        return True
        
    except Exception as e:
        print(f"❌ Database schema check failed: {e}")
        return False

async def suggest_fixes():
    """Suggest fixes for common issues"""
    print("\n" + "=" * 40)
    print("💡 COMMON FIXES")
    print("=" * 40)
    
    print("\n1. If 'extracted_text' column is missing:")
    print("   ALTER TABLE documents ADD COLUMN extracted_text TEXT;")
    
    print("\n2. If vector_embeddings table is missing:")
    print("   Run: backend/scripts/database/vector_setup.sql")
    
    print("\n3. If match_documents function is missing:")
    print("   Run: backend/scripts/database/database_update.sql")
    
    print("\n4. If embeddings are missing:")
    print("   - Upload documents through the API")
    print("   - Or run the RAG test script to create test embeddings")
    
    print("\n5. If vector dimensions don't match:")
    print("   - Check embedding_service.py model configuration")
    print("   - Ensure all schema files use VECTOR(384)")
    
    print("\n6. For immediate testing:")
    print("   python test_rag_pipeline.py")

async def main():
    """Main function"""
    success = await check_database_schema()
    await suggest_fixes()
    
    if success:
        print("\n✅ Database schema check completed")
    else:
        print("\n❌ Database schema has issues that need fixing")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Schema check interrupted by user")
    except Exception as e:
        print(f"\n💥 Schema check crashed: {e}")