"""
main.py
文件問答助理 - 主程式
使用方式: python main.py
"""
from dotenv import load_dotenv
load_dotenv()

import asyncio
from retrieval import search
from generation import generate_answer_stream


async def answer_question(question):
    retrieved_chunks = search(question, top_k=3)
    response_stream = await generate_answer_stream(question, retrieved_chunks)

    print("\n助理: ", end="", flush=True)
    async for chunk in response_stream:
        print(chunk.text, end="", flush=True)
    print()

    print("\n--- 本次回答參考的原始資料 ---")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"\n[參考資料{i+1}] (相似度距離: {chunk['distance']:.4f})")
        print(chunk['text'])
    print("-" * 40)


async def main():
    print("=" * 50)
    print("文件問答助理(輸入 exit 結束)")
    print("=" * 50)

    while True:
        question = input("\n你想問什麼: ")

        if question.strip().lower() == "exit":
            print("再見!")
            break
        if not question.strip():
            continue

        await answer_question(question)


if __name__ == "__main__":
    asyncio.run(main())
