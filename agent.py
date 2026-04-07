from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]

# Khởi tạo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    # xử lý lỗi context nếu có
    convert_system_message_to_human=True 
)

# Gắn tools vào llm
llm_with_tools = llm.bind_tools(tools_list)
# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    # Tự động gắn System Prompt vào đầu list nếu chưa có
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    # == LOGGING ====================
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"   [ACTION] Gọi tool: {tc['name']} ({tc['args']})")
    else:
        print(f"   [ACTION] Trả lời trực tiếp")
    # ===============================

    return {"messages": [response]}

# 5. Xây dựng Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

# LUỒNG ĐIỀU KHIỂN (EDGES)
builder.add_edge(START, "agent")
# Nếu agent quyết định gọi tool -> nhảy sang node 'tools'. Nếu không -> END
builder.add_conditional_edges("agent", tools_condition)
# Node 'tools' chạy xong sẽ trả kết quả ngược lại cho 'agent' suy nghĩ tiếp
builder.add_edge("tools", "agent")

graph = builder.compile()

# 6. Chat loop
if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' hoặc 'q' để thoát")
    print("=" * 60)

    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("TravelBuddy: Chúc bạn một ngày tốt lành!")
            break

        print("\nTravelBuddy đang suy nghĩ...")
        # Gọi luồng thực thi
        result = graph.invoke({"messages": [("human", user_input)]})
        final = result["messages"][-1]
        # Chỉ in phần nội dung văn bản, bỏ qua các metadata thừa
        if isinstance(final.content, list):
            print(f"\nTravelBuddy: {final.content[0]['text']}")
        else:
            print(f"\nTravelBuddy: {final.content}")