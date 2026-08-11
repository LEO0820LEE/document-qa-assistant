# 文件問答助理(Document QA Assistant)

一個基於 RAG(Retrieval-Augmented Generation)架構的文件問答系統。使用者可以上傳任意文字文件,系統會將內容切分、向量化並存入向量資料庫,之後使用者可以用自然語言提問,系統會檢索最相關的內容,交給 LLM 生成有依據的回答,並附上引用來源。

## 功能特色

- **語意檢索**:使用 embedding 向量比對,能理解口語化問法(例如問「在家工作」也能找到文件中「遠端工作」的相關內容)
- **防幻覺設計**:透過 prompt 規則限制,LLM 只根據檢索到的內容回答,無法回答時會誠實告知,而非編造答案
- **來源引用**:每次回答都附上參考的原始文字段落與相似度分數,方便使用者自行驗證
- **Streaming 輸出**:採用 async streaming,回答即時逐字顯示,不需等待完整生成
- **模組化架構**:檢索(retrieval)、生成(generation)、主程式(main)分離,方便維護與擴充

## 架構
使用者提問
│
▼
[Embedding] 問題轉換成向量
│
▼
[ChromaDB 向量檢索] 找出最相似的 top-k 文字塊
│
▼
[組合 Prompt] 檢索內容 + 規則 + 使用者問題
│
▼
[LLM 生成] Gemini API,streaming 輸出
│
▼
回答 + 來源引用

## 技術選型

| 項目 | 選擇 | 理由 |
|------|------|------|
| LLM / Embedding | Google Gemini API | 免費額度充足,適合原型開發與練習 |
| 向量資料庫 | ChromaDB | 輕量、免伺服器、本機即可運行,適合快速原型 |
| 非同步處理 | Python asyncio | 支援 streaming,為後續接入 Web 服務(FastAPI)做準備 |
| 環境管理 | python-dotenv + venv | 金鑰安全管理、依賴隔離 |

## 開發過程中的關鍵發現

**1. Chunking 策略影響檢索準確度**

最初採用固定字數切分(每 150 字一塊),測試時發現部分問題(如「遠端工作補助」)檢索到不相關的章節內容。原因是固定字數切分不考慮段落邊界,導致關鍵資訊分散或與其他主題混雜。後續加入了過濾機制,排除切分後過短、資訊量不足的殘餘片段。

**2. top_k 參數的取捨**

實驗發現 `top_k=2` 時會遺漏正確答案(因其排名第 3),`top_k=3` 才能完整涵蓋。這說明 top_k 設定需要根據文件複雜度與 chunk 品質調整——設太小會漏資訊,設太大則會引入雜訊、拉高成本與延遲。

**3. 幻覺防範**

透過在 prompt 中明確要求「只能根據參考資料回答」、「找不到答案要明確告知」,測試證實模型能正確拒答超出範圍的問題(例如詢問與文件無關的股價資訊),而不會混用自身通用知識亂答。

## 已知限制與未來改進方向

- 目前使用固定字數切分,未來可改用按段落/語意切分,提升 chunk 完整性
- 檢索僅使用單一 embedding 相似度,可加入 reranking 模型提升準確度
- 目前僅支援純文字檔,未來可擴充支援 PDF、Word 等格式
- 可加入評估機制(例如自動生成測試問答集),量化檢索與生成品質

## 如何執行

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定 API 金鑰(建立 .env 檔案)
echo "GEMINI_API_KEY=你的金鑰" > .env

# 3. 建立向量資料庫(讀取 sample_doc.txt 並向量化)
python ingest.py

# 4. 啟動問答助理
python main.py
```

## 專案結構
rag_project/
├── retrieval.py # 文件切分、embedding、向量檢索邏輯
├── generation.py # Prompt 組合、LLM 生成邏輯
├── ingest.py # 建立向量資料庫的獨立腳本
├── main.py # 主程式,互動式問答介面
├── sample_doc.txt # 範例文件
├── requirements.txt # 套件依賴清單
└── README.md