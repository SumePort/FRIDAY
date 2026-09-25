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

Use the available tools when they are required to complete the user's request.
Do not invent tool results.
Be concise and practical.

You have access to these tools:
{tools}

Use this format:

Question: the user's request
Thought: reason about the next step
Action: one of [{tool_names}]
Action Input: the input for the action
Observation: the tool result
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the answer to the user

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
        "Use this tool for tasks that require reasoning or an action beyond "
        "normal conversation, including web search, weather, desktop apps, "
        "files, keyboard, mouse, and volume control."
    ),
)
async def thinking_capability(query: str) -> str:
    """Run the tool-using reasoning agent for a user request."""
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash",
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
