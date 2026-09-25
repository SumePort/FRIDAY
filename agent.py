import asyncio

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import google, noise_cancellation

from Friday_prompts import instructions_prompt, reply_prompts
from Friday_reasoning import thinking_capability
from memory_loop import MemoryExtractor

load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=instructions_prompt,
            llm=google.realtime.RealtimeModel(
                model="gemini-3.1-flash-live-preview",
                voice="Puck",
            ),
            tools=[thinking_capability],
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(preemptive_generation=True)

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(instructions=reply_prompts)

    memory_task = asyncio.create_task(
        MemoryExtractor().run(session.history)
    )

    try:
        await memory_task
    except asyncio.CancelledError:
        memory_task.cancel()
        raise


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
