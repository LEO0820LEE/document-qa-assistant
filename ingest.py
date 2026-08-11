"""
ingest.py
執行這支程式,把文件讀取、切分、向量化,存入資料庫
只需要在文件內容變更時執行一次
"""
from dotenv import load_dotenv
load_dotenv()

from retrieval import ingest_document

if __name__ == "__main__":
    num_chunks = ingest_document("sample_doc.txt")
    print(f"完成!已將文件切成{num_chunks}塊,並存入向量資料庫。")
    