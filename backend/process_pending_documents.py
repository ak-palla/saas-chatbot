#!/usr/bin/env python3
"""
Process Pending Documents
Find and process documents that have extracted text but no embeddings
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def process_pending_documents():
    """Process documents that have text but no embeddings"""
    print("🔧 Processing Pending Documents")
    print("=" * 35)
    
    try:
        from app.core.database import get_supabase
        from app.services.document_service import document_service
        from app.services.embedding_service import embedding_service
        
        supabase = get_supabase()
        
        # Find documents with extracted text but processed=False
        print("🔍 Finding unprocessed documents...")
        docs_result = supabase.table("documents").select("*").eq("processed", False).execute()
        
        if not docs_result.data:
            print("✅ No pending documents found")
            return True
            
        print(f"📋 Found {len(docs_result.data)} unprocessed documents")
        
        for doc in docs_result.data:
            doc_id = doc['id']
            filename = doc['filename']
            chatbot_id = doc['chatbot_id']
            extracted_text = doc.get('extracted_text')
            
            print(f"\n📄 Processing: {filename}")
            print(f"   Document ID: {doc_id[:8]}...")
            print(f"   Chatbot ID: {chatbot_id[:8]}...")
            print(f"   Text length: {len(extracted_text) if extracted_text else 0} chars")
            
            if not extracted_text:
                print("   ⚠️ No extracted text found, skipping")
                continue
                
            try:
                # Step 1: Process the document content (this will chunk and create embeddings)
                print("   🔧 Processing document content...")
                await document_service._process_document_content(doc_id, extracted_text)
                
                # Check how many embeddings were created
                embeddings_result = supabase.table("vector_embeddings").select("*").eq("document_id", doc_id).execute()
                embedding_count = len(embeddings_result.data) if embeddings_result.data else 0
                
                print(f"   ✅ Created {embedding_count} embeddings")
                
                # Step 3: Mark document as processed
                print("   📝 Marking document as processed...")
                update_result = supabase.table("documents").update({
                    "processed": True
                }).eq("id", doc_id).execute()
                
                if update_result.data:
                    print("   ✅ Document marked as processed")
                else:
                    print("   ⚠️ Failed to mark document as processed")
                
            except Exception as e:
                print(f"   ❌ Failed to process document: {str(e)}")
                import traceback
                print(f"   📝 Error details: {traceback.format_exc()}")
                continue
        
        print(f"\n🎉 Document processing complete!")
        
        # Verify results for target chatbot
        target_chatbot_id = "5e69ab00-d866-46ab-b20b-fec3338a0895"
        print(f"\n🔍 Verifying results for target chatbot {target_chatbot_id[:8]}...")
        
        # Check embeddings now exist
        target_docs = supabase.table("documents").select("*").eq("chatbot_id", target_chatbot_id).execute()
        
        if target_docs.data:
            doc = target_docs.data[0]
            embeddings_result = supabase.table("vector_embeddings").select("*").eq("document_id", doc['id']).execute()
            embedding_count = len(embeddings_result.data) if embeddings_result.data else 0
            
            print(f"📊 Target chatbot now has:")
            print(f"   Documents: {len(target_docs.data)}")
            print(f"   Embeddings: {embedding_count}")
            print(f"   Document processed: {doc.get('processed', False)}")
            
            if embedding_count > 0:
                print("✅ SUCCESS: Target chatbot now has embeddings!")
                
                # Test a quick similarity search
                print("\n🧪 Testing RAG retrieval...")
                from app.services.vector_store_service import vector_store_service
                
                test_contexts, test_metadata = await vector_store_service.retrieve_relevant_context(
                    query="What is this document about?",
                    chatbot_id=target_chatbot_id,
                    max_contexts=2,
                    similarity_threshold=0.2  # Lower threshold for testing
                )
                
                if test_contexts:
                    print(f"🎯 RAG TEST SUCCESS: Retrieved {len(test_contexts)} contexts!")
                    for i, context in enumerate(test_contexts):
                        similarity = test_metadata[i].get('similarity', 'N/A') if i < len(test_metadata) else 'N/A'
                        print(f"   Context {i+1} (sim: {similarity}): '{context[:80]}...'")
                else:
                    print("⚠️ RAG test still returned no contexts")
            else:
                print("❌ No embeddings created for target chatbot")
        
        return True
        
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        import traceback
        print(f"📝 Error details: {traceback.format_exc()}")
        return False

async def main():
    success = await process_pending_documents()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted")
        sys.exit(1)