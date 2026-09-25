from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from livekit.agents import function_tool

from Friday_file_opner import Play_file
from Friday_get_whether import get_weather
from Friday_google_search import get_current_datetime, google_search
from Friday_window_CTRL import close_app, folder_file, open_app
from keyboard_mouse_CTRL import (
    control_volume_tool,
    mouse_click_tool,
    move_cursor_tool,
    press_hotkey_tool,
    press_key_tool,
    scroll_cursor_tool,
    swipe_gesture_tool,
    type_text_tool,
)

load_dotenv()

REACT_PROMPT = PromptTemplate.from_template(
    """You are Friday, a desktop AI assistant.

Use the available tools when required. Do not invent tool results.
Be concise and practical.

Tools:
{tools}

Question: {input}
Thought: {agent_scratchpad}"""
)

TOOLS = [
    google_search,
    get_current_datetime,
    get_weather,
    open_app,
    close_app,
    folder_file,
    Play_file,
    move_cursor_tool,
    mouse_click_tool,
    scroll_cursor_tool,
    type_text_tool,
    press_key_tool,
    press_hotkey_tool,
    control_volume_tool,
    swipe_gesture_tool,
]


@function_tool(
    name="thinking_capability",
    description=(
        "Use this tool for tasks requiring reasoning or actions such as "
        "search, weather, desktop apps, files, keyboard, mouse, or volume."
    ),
)
async def thinking_capability(query: str) -> str:
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            temperature=0,
        )

        agent = create_react_agent(
            llm=model,
            tools=TOOLS,
            prompt=REACT_PROMPT,
        )

        executor = AgentExecutor(
            agent=agent,
            tools=TOOLS,
            verbose=False,
            max_iterations=8,
            handle_parsing_errors=True,
        )

        result = await executor.ainvoke({"input": query})
        return str(result.get("output", result))

    except Exception as exc:
        return f"Reasoning tool failed: {exc}"
