from logging import Logger


def handle_connect_account(ack, logger: Logger):
    """Handle the Connect button click on App Home.

    The Connect button is a URL button that opens the OAuth page in the
    browser, so we only need to acknowledge the action.
    """
    ack()
