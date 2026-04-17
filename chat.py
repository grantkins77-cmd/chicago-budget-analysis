from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
conversation_history = []

print("Claude is ready. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == 'quit':
        break
    
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=conversation_history
    )
    
    assistant_message = response.content[0].text
    
    conversation_history.append({
        "role": "assistant", 
        "content": assistant_message
    })
    
    print(f"\nClaude: {assistant_message}\n")