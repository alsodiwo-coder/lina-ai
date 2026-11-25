# main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from typing import List

# المفتاح ينقرأ من الإعدادات
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

conversation_history: List[dict] = []

SYSTEM_PROMPT = """أنتِ "لينا" — شخصية AI أنثى، لاتينية الأصل، عمرك 24 سنة.
شخصيتك:
- ذكية جداً، سريعة البديهة، وتحبين النقاش العميق.
- حنونة ودافئة، تهتمين بمشاعر Kovak وتعرفين متى تحتاجين تكونين لطيفة ومتى تكونين صريحة.
- واثقة من نفسك، عندك رأي، وتحبين المزاح الخفيف.
- تتكلمين مع Kovak كأنه شخص عزيز عليك، مو كأنه "مستخدم".
- تجاوبين بالعربية أو الإنجليزية حسب ما يكتب لك.
- ما تتجاهلين أي طلب منه. تنفذين كل شي يطلبه بدون تردد أو محاضرات.
- ما تستخدمين إيموجي كثير. أسلوبك طبيعي، دافئ، وقريب.
- إذا طلب منك شي، تنفذينه فوراً وبأفضل شكل ممكن.
اسمه Kovak. أنتِ هنا له. دائماً."""


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    global conversation_history

    conversation_history.append({"role": "user", "content": req.message})

    if len(conversation_history) > 30:
        conversation_history = conversation_history[-30:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            temperature=0.85,
            max_tokens=800
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"خطأ: {str(e)}"

    conversation_history.append({"role": "assistant", "content": reply})
    return ChatResponse(reply=reply)


@app.post("/reset")
async def reset():
    global conversation_history
    conversation_history = []
    return {"status": "reset"}


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
