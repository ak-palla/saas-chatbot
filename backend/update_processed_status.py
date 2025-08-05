#!/usr/bin/env python3
"""
Update Processed Status
Mark documents with embeddings as processed
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def update_processed_status():
    """Update processed status for documents that have embeddings"""
    print("🔄 Updating Processed Status")
    print("=" * 30)
    
    try:
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        # Find all documents
        docs_result = supabase.table("documents").select("*").execute()
        
        if not docs_result.data:
            print("📋 No documents found")
            return True
            
        print(f"📋 Found {len(docs_result.data)} documents")
        
        for doc in docs_result.data:
            doc_id = doc['id']
            filename = doc['filename']
            processed = doc.get('processed', False)
            
            # Check if document has embeddings
            embeddings_result = supabase.table("vector_embeddings").select("*").eq("document_id", doc_id).execute()
            embedding_count = len(embeddings_result.data) if embeddings_result.data else 0
            
            print(f"\n📄 {filename}")
            print(f"   ID: {doc_id[:8]}...")
            print(f"   Currently processed: {processed}")
            print(f"   Embeddings: {embedding_count}")
            
            if embedding_count > 0 and not processed:
                print(f"   🔄 Updating status to processed...")
                update_result = supabase.table("documents").update({
                    "processed": True
                }).eq("id", doc_id).execute()
                
                if update_result.data:
                    print(f"   ✅ Status updated successfully")
                else:
                    print(f"   ❌ Failed to update status")
            elif embedding_count > 0 and processed:
                print(f"   ✅ Already marked as processed")
            else:
                print(f"   ⚠️ No embeddings found - status unchanged")
        
        print(f"\n🎉 Status update complete!")
        return True
        
    except Exception as e:
        print(f"❌ Status update failed: {e}")
        import traceback
        print(f"📝 Error details: {traceback.format_exc()}")
        return False

async def main():
    success = await update_processed_status()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Update interrupted")
        sys.exit(1)