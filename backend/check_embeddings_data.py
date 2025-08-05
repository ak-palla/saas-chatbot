#!/usr/bin/env python3
"""
Check Embeddings Data
Inspect what embeddings exist in the database for debugging
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def check_embeddings_data():
    """Check what embeddings and documents exist in the database"""
    print("🔍 Checking Embeddings Data")
    print("=" * 30)
    
    try:
        from app.core.database import get_supabase
        supabase = get_supabase()
        
        # Your chatbot ID from the error log
        target_chatbot_id = "5e69ab00-d866-46ab-b20b-fec3338a0895"
        
        print(f"🎯 Target chatbot ID: {target_chatbot_id}")
        
        # 1. Check all documents
        print(f"\n1. 📄 All Documents:")
        docs_result = supabase.table("documents").select("id,filename,chatbot_id,processed,created_at").execute()
        
        if docs_result.data:
            print(f"   Found {len(docs_result.data)} total documents:")
            for doc in docs_result.data:
                status = "✅ Processed" if doc.get('processed') else "⏳ Not processed"
                is_target = "🎯" if doc.get('chatbot_id') == target_chatbot_id else "  "
                print(f"   {is_target} {doc['filename']} ({doc['chatbot_id'][:8]}...) - {status}")
        else:
            print("   ❌ No documents found")
            return
        
        # 2. Check documents for target chatbot
        print(f"\n2. 📋 Documents for target chatbot:")
        target_docs = supabase.table("documents").select("*").eq("chatbot_id", target_chatbot_id).execute()
        
        if target_docs.data:
            print(f"   Found {len(target_docs.data)} documents:")
            for doc in target_docs.data:
                print(f"   📄 {doc['filename']} (ID: {doc['id'][:8]}...)")
                print(f"      Processed: {doc.get('processed', False)}")
                print(f"      File type: {doc.get('file_type', 'Unknown')}")
                print(f"      Created: {doc.get('created_at', 'Unknown')}")
                
                # Check if it has extracted text
                if 'extracted_text' in doc:
                    extracted_text = doc.get('extracted_text')
                    if extracted_text:
                        text_length = len(extracted_text)
                        print(f"      Extracted text: {text_length} chars - '{extracted_text[:100]}...'")
                    else:
                        print(f"      Extracted text: None")
                else:
                    print(f"      Extracted text: Column not present")
                print()
        else:
            print("   ❌ No documents found for target chatbot")
            print("   💡 This explains why no contexts are retrieved!")
            return
        
        # 3. Check all embeddings
        print(f"3. 🧠 All Vector Embeddings:")
        embeddings_result = supabase.table("vector_embeddings").select("id,document_id,text_content,created_at").execute()
        
        if embeddings_result.data:
            print(f"   Found {len(embeddings_result.data)} total embeddings:")
            
            # Group by document
            doc_embeddings = {}
            for emb in embeddings_result.data:
                doc_id = emb['document_id']
                if doc_id not in doc_embeddings:
                    doc_embeddings[doc_id] = []
                doc_embeddings[doc_id].append(emb)
            
            for doc_id, embeddings in doc_embeddings.items():
                # Find document info
                doc_info = next((d for d in docs_result.data if d['id'] == doc_id), None)
                if doc_info:
                    chatbot_id = doc_info['chatbot_id']
                    filename = doc_info['filename']
                    is_target = "🎯" if chatbot_id == target_chatbot_id else "  "
                    print(f"   {is_target} {filename} ({chatbot_id[:8]}...): {len(embeddings)} embeddings")
                    
                    if is_target == "🎯":
                        # Show sample embeddings for target chatbot
                        for i, emb in enumerate(embeddings[:3]):  # Show first 3
                            text_preview = emb['text_content'][:60] if emb['text_content'] else 'No content'
                            print(f"      Embedding {i+1}: '{text_preview}...'")
                        if len(embeddings) > 3:
                            print(f"      ... and {len(embeddings) - 3} more embeddings")
                else:
                    print(f"   ❓ Unknown document {doc_id[:8]}...: {len(embeddings)} embeddings")
        else:
            print("   ❌ No embeddings found")
            print("   💡 This explains why no contexts are retrieved!")
        
        # 4. Check embeddings specifically for target chatbot
        print(f"\n4. 🎯 Embeddings for target chatbot:")
        target_embeddings_query = """
        SELECT ve.*, d.filename, d.chatbot_id 
        FROM vector_embeddings ve
        JOIN documents d ON ve.document_id = d.id
        WHERE d.chatbot_id = %s
        """
        
        # Since we can't run raw SQL easily, let's check through documents
        target_embedding_count = 0
        if target_docs.data:
            for doc in target_docs.data:
                doc_embeddings_result = supabase.table("vector_embeddings").select("*").eq("document_id", doc['id']).execute()
                doc_embedding_count = len(doc_embeddings_result.data) if doc_embeddings_result.data else 0
                target_embedding_count += doc_embedding_count
                
                print(f"   📄 {doc['filename']}: {doc_embedding_count} embeddings")
                
                if doc_embeddings_result.data:
                    # Show a sample
                    sample = doc_embeddings_result.data[0]
                    text_preview = sample['text_content'][:80] if sample['text_content'] else 'No content'
                    print(f"      Sample: '{text_preview}...'")
        
        print(f"\n📊 Summary for chatbot {target_chatbot_id[:8]}...:")
        print(f"   Documents: {len(target_docs.data) if target_docs.data else 0}")
        print(f"   Embeddings: {target_embedding_count}")
        
        if target_embedding_count == 0:
            print(f"\n❌ ROOT CAUSE: No embeddings exist for this chatbot!")
            print(f"💡 SOLUTIONS:")
            print(f"   1. Upload documents through the API")
            print(f"   2. Check if documents are being processed")
            print(f"   3. Check document processing logs")
            print(f"   4. Verify the chatbot ID is correct")
        else:
            print(f"\n✅ Embeddings exist, but query isn't matching")
            print(f"💡 SOLUTIONS:")
            print(f"   1. Lower the similarity threshold (currently 0.3)")
            print(f"   2. Try different queries")
            print(f"   3. Check embedding model consistency")
        
        # 5. Test similarity search with very low threshold
        if target_embedding_count > 0:
            print(f"\n5. 🧪 Testing with very low similarity threshold...")
            try:
                from app.services.vector_store_service import vector_store_service
                
                low_threshold_contexts, low_threshold_metadata = await vector_store_service.retrieve_relevant_context(
                    query="What is this about?",
                    chatbot_id=target_chatbot_id,
                    max_contexts=5,
                    similarity_threshold=0.1  # Very low threshold
                )
                
                if low_threshold_contexts:
                    print(f"   ✅ Found {len(low_threshold_contexts)} contexts with low threshold!")
                    for i, context in enumerate(low_threshold_contexts):
                        similarity = low_threshold_metadata[i].get('similarity', 'N/A') if i < len(low_threshold_metadata) else 'N/A'
                        print(f"      Context {i+1} (sim: {similarity}): '{context[:60]}...'")
                else:
                    print(f"   ❌ Still no contexts found even with very low threshold")
                    
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        import traceback
        print(f"📝 Error details: {traceback.format_exc()}")
        return False

async def main():
    success = await check_embeddings_data()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Check interrupted")
        sys.exit(1)