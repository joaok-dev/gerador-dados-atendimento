class Ticket:
    def __init__(self, ticket_id, start_time, end_time, ticket_type):
        """
        Initialize a new ticket object.

        :param ticket_id: Unique identifier for the ticket
        :param start_time: The time the ticket started
        :param end_time: The time the ticket ended
        :param ticket_type: The type of the ticket (voice, chat, email)
        """
        self.ticket_id = ticket_id
        self.start_time = start_time
        self.end_time = end_time
        self.ticket_type = ticket_type

