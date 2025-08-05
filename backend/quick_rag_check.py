#!/usr/bin/env python3
"""
Quick RAG Health Check
Fast diagnostic script to identify the most common RAG issues
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def quick_check():
    """Perform a quick health check of the RAG system"""
    print("⚡ Quick RAG Health Check")
    print("=" * 30)
    
    issues_found = []
    
    # 1. Check imports
    print("\n1. 📦 Checking Critical Imports...")
    try:
        from app.core.config import settings
        from app.core.database import get_supabase
        from app.services.embedding_service import embedding_service
        print("  ✅ All critical imports successful")
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        issues_found.append("Import failure - check dependencies")
        return issues_found
    
    # 2. Check database connection
    print("\n2. 🗄️ Checking Database...")
    try:
        supabase = get_supabase()
        result = supabase.table("vector_embeddings").select("id", count="exact").execute()
        embedding_count = result.count
        print(f"  ✅ Database connected, {embedding_count} embeddings found")
        
        if embedding_count == 0:
            issues_found.append("No embeddings found - upload documents first")
            
    except Exception as e:
        print(f"  ❌ Database issue: {e}")
        issues_found.append("Database connection or schema problem")
    
    # 3. Check embedding service
    print("\n3. 🧠 Checking Embedding Service...")
    try:
        test_embedding = await embedding_service.generate_embedding("test")
        if test_embedding and len(test_embedding) > 0:
            print(f"  ✅ Embedding service working ({len(test_embedding)}D)")
            
            if len(test_embedding) != 384:
                issues_found.append(f"Embedding dimension mismatch: {len(test_embedding)} != 384")
        else:
            print("  ❌ Embedding generation failed")
            issues_found.append("Embedding service not working")
            
    except Exception as e:
        print(f"  ❌ Embedding service error: {e}")
        issues_found.append("Embedding service error - check model installation")
    
    # 4. Check for documents
    print("\n4. 📄 Checking Documents...")
    try:
        doc_result = supabase.table("documents").select("id", count="exact").execute()
        doc_count = doc_result.count
        print(f"  📊 Found {doc_count} documents")
        
        if doc_count == 0:
            issues_found.append("No documents uploaded")
        else:
            # Check if documents have been processed
            processed_result = supabase.table("documents").select("id", count="exact").eq("processed", True).execute()
            processed_count = processed_result.count
            print(f"  📊 {processed_count}/{doc_count} documents processed")
            
            if processed_count == 0:
                issues_found.append("Documents uploaded but not processed")
                
    except Exception as e:
        print(f"  ❌ Documents check failed: {e}")
        issues_found.append("Cannot check documents")
    
    # 5. Test RAG retrieval
    print("\n5. 🔍 Testing RAG Retrieval...")
    try:
        from app.services.vector_store_service import vector_store_service
        
        # Use the chatbot ID from your error log
        test_chatbot_id = "5e69ab00-d866-46ab-b20b-fec3338a0895"
        contexts, metadata = await vector_store_service.retrieve_relevant_context(
            query="test query",
            chatbot_id=test_chatbot_id,
            max_contexts=1,
            similarity_threshold=0.3
        )
        
        if contexts:
            print(f"  ✅ RAG retrieval working ({len(contexts)} contexts found)")
        else:
            print("  ⚠️ No contexts retrieved (may be normal if no matching documents)")
            
    except Exception as e:
        print(f"  ❌ RAG retrieval failed: {e}")
        issues_found.append("RAG retrieval not working")
    
    # Summary
    print("\n" + "=" * 30)
    print("📋 DIAGNOSIS SUMMARY")
    print("=" * 30)
    
    if not issues_found:
        print("🎉 No issues found! RAG system appears healthy.")
        print("\n💡 If RAG still isn't working:")
        print("   - Check that documents are uploaded for the correct chatbot")
        print("   - Verify the chatbot ID matches between frontend and backend")
        print("   - Run the full test suite: python test_rag_pipeline.py")
    else:
        print(f"⚠️ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 QUICK FIXES:")
        
        if "No embeddings found" in str(issues_found):
            print("   - Upload documents through the API")
            print("   - Check document processing logs")
        
        if "Embedding dimension mismatch" in str(issues_found):
            print("   - Run: python check_database_schema.py")
            print("   - Update database schema to match embedding dimensions")
        
        if "Embedding service" in str(issues_found):
            print("   - Install: pip install sentence-transformers")
            print("   - Run: python test_embedding_models.py")
        
        if "Database" in str(issues_found):
            print("   - Check Supabase connection settings")
            print("   - Run vector setup SQL scripts")
        
        if "Documents uploaded but not processed" in str(issues_found):
            print("   - Check if extracted_text column exists")
            print("   - Check document processing logs")
    
    return issues_found

async def main():
    """Main function"""
    try:
        issues = await quick_check()
        exit_code = 0 if not issues else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Quick check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Quick check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())