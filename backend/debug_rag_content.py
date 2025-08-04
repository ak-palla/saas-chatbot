#!/usr/bin/env python3
"""
Debug script to check if RAG content was extracted correctly from the PDF
"""

import sys
import os
sys.path.append('/mnt/d/chat_service/backend')

from app.core.database import get_supabase

def check_rag_content():
    print("🔍 Checking RAG Content Extraction")
    print("=" * 50)
    
    supabase = get_supabase()
    
    try:
        # Check documents table
        print("1. Checking documents table...")
        docs_response = supabase.table("documents") \
            .select("id, filename, processed, extracted_text") \
            .eq("filename", "Customer_Support_Policy_Manual.pdf") \
            .execute()
        
        if docs_response.data:
            doc = docs_response.data[0]
            print(f"   ✅ Document found: {doc['filename']}")
            print(f"   📊 Processed: {doc['processed']}")
            
            extracted_text = doc.get('extracted_text', '')
            if extracted_text:
                print(f"   📄 Text extracted: {len(extracted_text)} characters")
                print(f"   📄 Preview: {extracted_text[:200]}...")
                
                # Check if business hours info is in the text
                if 'monday' in extracted_text.lower() or 'business hours' in extracted_text.lower():
                    print("   ✅ Business hours content found in extracted text")
                else:
                    print("   ⚠️  Business hours content NOT found in extracted text")
            else:
                print("   ❌ No extracted text found")
                
        else:
            print("   ❌ Document not found")
            return
        
        # Check vector embeddings
        print("\n2. Checking vector embeddings...")
        embeddings_response = supabase.table("vector_embeddings") \
            .select("id, text_content") \
            .eq("document_id", doc['id']) \
            .execute()
        
        print(f"   📊 Total embeddings: {len(embeddings_response.data)}")
        
        # Search for business hours in embeddings
        business_hours_chunks = []
        for i, embedding in enumerate(embeddings_response.data):
            text_content = embedding.get('text_content', '').lower()
            if 'monday' in text_content or 'business hours' in text_content or 'hours' in text_content:
                business_hours_chunks.append({
                    'chunk_id': i,
                    'content': embedding.get('text_content', '')[:200] + "..."
                })
        
        if business_hours_chunks:
            print(f"   ✅ Found {len(business_hours_chunks)} chunks with business hours content:")
            for chunk in business_hours_chunks[:3]:  # Show first 3
                print(f"      Chunk {chunk['chunk_id']}: {chunk['content']}")
        else:
            print("   ⚠️  No business hours content found in embeddings")
            
        # Show sample of all embeddings
        print(f"\n3. Sample of all embeddings:")
        for i, embedding in enumerate(embeddings_response.data[:5]):
            content = embedding.get('text_content', '')
            print(f"   Chunk {i}: {content[:100]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_rag_content()