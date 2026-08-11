"""
retrieval.py
負責:讀取文件、切分文字、建立/查詢向量資料庫
"""
import chromadb
from google import genai

client_genai = genai.Client()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="company_handbook")


def split_into_chunks(text, chunk_size=150, overlap=30):
    """
    把長文字切成小塊(固定字數切分法)

    已知限制:此方法不考慮段落/章節邊界,可能導致
    語意完整的段落被切斷在不同塊中,影響檢索準確度。
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # 過濾掉太短的殘餘塊(例如切到最後剩下的小段落)
        if len(chunk.strip()) > 20:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def ingest_document(filepath):
    """讀取文件、切分、embedding、存入向量資料庫"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = split_into_chunks(content, chunk_size=150, overlap=30)

    for i, chunk in enumerate(chunks):
        result = client_genai.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk
        )
        embedding_vector = result.embeddings[0].values

        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding_vector],
            documents=[chunk]
        )

    return len(chunks)


def search(query, top_k=3):
    """
    檢索最相似的文字塊

    回傳格式:list of dict,每個dict包含id、text、distance
    distance越小代表越相似
    """
    result = client_genai.models.embed_content(
        model="gemini-embedding-001",
        contents=query
    )
    query_vector = result.embeddings[0].values

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "distance": results["distances"][0][i]
        })
    return retrieved