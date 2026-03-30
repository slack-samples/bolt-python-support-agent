from logging import Logger

from slack_bolt import Ack, BoltContext
from slack_sdk import WebClient

from agent import DEFAULT_MODEL, CaseyDeps, casey_agent
from conversation import conversation_store
from listeners.views.feedback_block import create_feedback_block


def handle_issue_submission(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    logger: Logger,
):
    """Handle modal submission: open DM, post issue, and run Casey agent."""
    ack()

    try:
        team_id = context.team_id
        user_id = context.user_id
        values = body["view"]["state"]["values"]
        category = values["category_block"]["category_select"]["selected_option"][
            "value"
        ]
        description = values["description_block"]["description_input"]["value"]

        # Open a DM with the user
        dm = client.conversations_open(users=[user_id])
        channel_id = dm["channel"]["id"]

        # Post the initial message with category and description
        user_message = f"*Category:* {category}\n*Description:* {description}"
        initial = client.chat_postMessage(
            channel=channel_id,
            text=user_message,
        )
        thread_ts = initial["ts"]

        # Set assistant thread status with loading messages
        client.assistant_threads_setStatus(
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
        client.reactions_add(
            channel=channel_id,
            timestamp=thread_ts,
            name="eyes",
        )

        # Run the agent
        deps = CaseyDeps(
            client=client,
            user_id=user_id,
            channel_id=channel_id,
            thread_ts=thread_ts,
        )
        result = casey_agent.run_sync(user_message, model=DEFAULT_MODEL, deps=deps)

        # Stream the response in thread with feedback buttons
        streamer = client.chat_stream(
            channel=channel_id,
            recipient_team_id=team_id,
            recipient_user_id=user_id,
            thread_ts=thread_ts,
        )
        streamer.append(markdown_text=result.output)
        feedback_blocks = create_feedback_block()
        streamer.stop(blocks=feedback_blocks)

        # Store conversation history
        conversation_store.set_history(channel_id, thread_ts, result.all_messages())

    except Exception as e:
        logger.exception(f"Failed to handle issue submission: {e}")
