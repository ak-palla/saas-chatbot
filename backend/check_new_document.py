#!/usr/bin/env python3
"""
Check New Document Status
Check the status of the newly uploaded document
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def check_new_document():
    """Check the status of the newly uploaded document"""
    print("🔍 Checking New Document Status")
    print("=" * 35)
    
    try:
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        # The new document ID from the frontend logs
        new_doc_id = "30fcfe60-e0d8-46bb-96e4-4c7516174f63"
        target_chatbot_id = "5e69ab00-d866-46ab-b20b-fec3338a0895"
        
        print(f"🎯 Checking document: {new_doc_id}")
        print(f"🤖 Target chatbot: {target_chatbot_id}")
        
        # Check document status
        doc_result = supabase.table("documents").select("*").eq("id", new_doc_id).execute()
        
        if doc_result.data:
            doc = doc_result.data[0]
            print(f"\n📄 Document Details:")
            print(f"   Filename: {doc['filename']}")
            print(f"   Processed: {doc.get('processed', False)}")
            print(f"   File size: {doc.get('file_size', 'Unknown')} bytes")
            print(f"   Created: {doc.get('created_at', 'Unknown')}")
            
            # Check if text was extracted
            extracted_text = doc.get('extracted_text')
            if extracted_text:
                print(f"   Extracted text: {len(extracted_text)} chars")
                print(f"   Text preview: '{extracted_text[:100]}...'")
            else:
                print(f"   ❌ No extracted text found!")
                
            # Check embeddings
            embeddings_result = supabase.table("vector_embeddings").select("*").eq("document_id", new_doc_id).execute()
            embedding_count = len(embeddings_result.data) if embeddings_result.data else 0
            print(f"   Embeddings: {embedding_count}")
            
            if embedding_count == 0:
                print(f"\n❌ ISSUE FOUND: Document uploaded but not processed!")
                print(f"💡 SOLUTION: Need to process this document into embeddings")
                return False
            else:
                print(f"\n✅ Document is properly processed")
        else:
            print(f"❌ Document not found!")
            return False
            
        # Check all documents for target chatbot
        print(f"\n📊 All Documents for Chatbot {target_chatbot_id[:8]}...:")
        all_docs = supabase.table("documents").select("*").eq("chatbot_id", target_chatbot_id).execute()
        
        total_embeddings = 0
        if all_docs.data:
            print(f"   Found {len(all_docs.data)} documents:")
            for doc in all_docs.data:
                embeddings_result = supabase.table("vector_embeddings").select("*").eq("document_id", doc['id']).execute()
                doc_embeddings = len(embeddings_result.data) if embeddings_result.data else 0
                total_embeddings += doc_embeddings
                
                status = "✅ Processed" if doc.get('processed') else "⏳ Processing"
                print(f"     📄 {doc['filename']} - {status} ({doc_embeddings} embeddings)")
        
        print(f"\n📈 Summary:")
        print(f"   Total documents: {len(all_docs.data) if all_docs.data else 0}")
        print(f"   Total embeddings: {total_embeddings}")
        print(f"   RAG ready: {'✅ Yes' if total_embeddings > 0 else '❌ No'}")
        
        return total_embeddings > 0
        
    except Exception as e:
        print(f"❌ Check failed: {e}")
        import traceback
        print(f"📝 Error details: {traceback.format_exc()}")
        return False

async def main():
    success = await check_new_document()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Check interrupted")
        sys.exit(1)