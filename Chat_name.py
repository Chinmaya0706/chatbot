from langchain_core.prompts import ChatPromptTemplate

prompt_for_chat_name = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Generate a short, concise and HIGHLY CREATIVE title (4-5 words max) for this chat conversation based on the initial exchange. Do not use quotation marks."),
        ('human', "User: {user_msg}\nAI: {ai_msg}")
    ]
)

def get_chat_name(chat_history, model, parser):
    # specific check to ensure we have enough data
    if len(chat_history) < 2:
        return "New Chat"
        
    user_msg = chat_history[0]["content"]
    ai_msg = chat_history[1]["content"]

    chain_for_name = prompt_for_chat_name | model | parser
    
    response = chain_for_name.invoke({
        "user_msg": user_msg,
        "ai_msg": ai_msg
    })
    
    return response.strip()