from enum import Enum, unique

from pinax.eventlog.models import log as event_log


class InvalidLogParams(Exception):
    def __init__(self, event, args):
        self.event = event
        self.args = args

    def __str__(self):
        return "Invalid arguments passed to log() for event: {}. Required: {}, got: {}".format(self.event,
                                                                                               self.event.log_keys,
                                                                                               self.args)


@unique
class Event(Enum):
    """
    The ordering of the numbers here is not important, their uniqueness will be ensured by the enum.
    Group the values as desired (maybe by function, or alphabetically
    """
    # Format of entries is (id, list_of_event_logging_data)
    PLACE_MARKET_ORDER = (0, ['order'])
    CANCEL_MARKET_ORDER = (1, [])
    ARCHIVE_GOAL_REQUESTED = (2, [])
    ARCHIVE_GOAL = (3, [])
    REACTIVATE_GOAL = (4, [])

    def __init__(self, value, log_keys):
        if 'reason' in log_keys:
            raise ValueError("'reason' is a reserved event logging key. "
                             "Maybe you should use the 'reason' argument to the 'Event.log' method instead?")
        self.log_keys = log_keys

    def log(self, reason, *args, user=None, obj=None):
        """
        Log the event to the event log
        :param reason: The reason this event occurred. The cause of the event.
        :param args:
            The arguments appropriate for the particular event. All are required and positional.
            repr() will be called on each argument before logging.
        :param user: The user performing the event
        :param obj: The object the event concerns
        :return:
        """
        if len(args) != len(self.log_keys):
            raise InvalidLogParams(self, args)
        log_data = dict(zip(self.log_keys, map(repr, args)))
        log_data['reason'] = reason
        event_log(user, self.name, log_data, obj=obj)
