"""
generation.py
負責:組合prompt、呼叫LLM生成答案
"""
from google import genai

client_genai = genai.Client()


def build_prompt(question, retrieved_chunks):
    context = "\n\n".join(
        [f"[參考資料{i+1}]\n{chunk['text']}" for i, chunk in enumerate(retrieved_chunks)]
    )

    prompt = f"""你是一個文件問答助理。請根據以下參考資料回答使用者的問題。

規則:
1. 只能根據參考資料的內容回答,不要編造參考資料裡沒有的資訊
2. 如果參考資料裡找不到答案,要明確說「根據現有資料無法回答這個問題」
3. 回答要簡潔,直接針對問題回答
4. 在回答的最後,用「(參考資料X)」標註主要參考了哪份資料

參考資料:
{context}

使用者問題:{question}

請回答:"""
    return prompt


async def generate_answer_stream(question, retrieved_chunks):
    """用streaming方式生成答案,回傳一個async generator"""
    prompt = build_prompt(question, retrieved_chunks)

    response_stream = await client_genai.aio.models.generate_content_stream(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response_stream
