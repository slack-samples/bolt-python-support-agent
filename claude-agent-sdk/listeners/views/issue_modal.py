from logging import Logger

from slack_bolt import Ack
from slack_bolt.agent.async_agent import AsyncBoltAgent
from slack_bolt.context.async_context import AsyncBoltContext
from slack_sdk.web.async_client import AsyncWebClient

from agent import run_casey_agent
from conversation import session_store
from listeners.views.feedback_block import create_feedback_block


async def handle_issue_submission(
    ack: Ack,
    agent: AsyncBoltAgent,
    body: dict,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    logger: Logger,
):
    """Handle modal submission: open DM, post issue, and run Casey agent."""
    await ack()

    try:
        team_id = context.team_id
        user_id = context.user_id
        values = body["view"]["state"]["values"]
        category = values["category_block"]["category_select"]["selected_option"][
            "value"
        ]
        description = values["description_block"]["description_input"]["value"]

        # Open a DM with the user
        dm = await client.conversations_open(users=[user_id])
        channel_id = dm["channel"]["id"]

        # Post the initial message with category and description
        user_message = f"*Category:* {category}\n*Description:* {description}"
        initial = await client.chat_postMessage(
            channel=channel_id,
            text=user_message,
        )
        thread_ts = initial["ts"]

        # Set assistant thread status with loading messages
        await client.assistant_threads_setStatus(
            channel_id=channel_id,
            thread_ts=thread_ts,
            status="Thinking...",
            loading_messages=[
                "Teaching the hamsters to type faster…",
                "Untangling the internet cables…",
                "Consulting the office goldfish…",
                "Polishing up the response just for you…",
                "Convincing the AI to stop overthinking…",
            ],
        )

        # Add eyes reaction
        await client.reactions_add(
            channel=channel_id,
            timestamp=thread_ts,
            name="eyes",
        )

        # Run the agent
        response_text, new_session_id = await run_casey_agent(user_message)

        # Stream the response in thread with feedback buttons
        streamer = await agent.chat_stream(
            channel=channel_id,
            recipient_team_id=team_id,
            recipient_user_id=user_id,
            thread_ts=thread_ts,
        )
        await streamer.append(markdown_text=response_text)
        feedback_blocks = create_feedback_block()
        await streamer.stop(blocks=feedback_blocks)

        # Store session ID for future context
        if new_session_id:
            session_store.set_session(channel_id, thread_ts, new_session_id)

    except Exception as e:
        logger.exception(f"Failed to handle issue submission: {e}")
