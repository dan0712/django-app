from django.utils import six
from pinax.eventlog.models import log as event_log
from common.structures import ChoiceEnum

# using AppConfig is for Django 1.9+
# from django.apps import AppConfig
# use this instead for Django 1.7<1.9
from django.db.models.loading import get_model


class InvalidLogParams(Exception):
    def __init__(self, event, args):
        self.event = event
        self.args = args

    def __str__(self):
        return ("Invalid arguments passed to log() for event: {}. "
                "Required: {}, got: {}".format(self.event, self.event.log_keys,
                                               self.args))


class Event(ChoiceEnum):
    """
    The ordering of the numbers here is not important, their uniqueness will
     be ensured by the enum.
    Group the values as desired (maybe by function, or alphabetically
    """
    # Format: (id, list_of_event_logging_data, required object type)
    PLACE_MARKET_ORDER = (0, ['order'], 'client.ClientAccount')
    CANCEL_MARKET_ORDER = (1, [], 'client.ClientAccount')
    ARCHIVE_GOAL_REQUESTED = (2, [], 'main.Goal')
    ARCHIVE_GOAL = (3, [], 'main.Goal')
    REACTIVATE_GOAL = (4, [], 'main.Goal')
    # "Settings changes approved"
    APPROVE_SELECTED_SETTINGS = (5, [], 'main.Goal')
    # "Settings changes reverted"
    REVERT_SELECTED_SETTINGS = (6, [], 'main.Goal')
    # "Settings update '{}' requested"
    SET_SELECTED_SETTINGS = (7, ['request'], 'main.Goal')
    # "Settings change '{}' requested"
    UPDATE_SELECTED_SETTINGS = (8, ['request'], 'main.Goal')
    # "Withdrawal from goal requested"
    GOAL_WITHDRAWAL = (9, ['request'], 'main.Goal')
    # "Deposit to goal requested"
    GOAL_DEPOSIT = (10, ['request'], 'main.Goal')

    # We may never actually log the below, as we have the data stored in
    # the HistoricalBalance table.
    # It's here so we can easily process it for the account activity endpoint.
    GOAL_BALANCE_CALCULATED = (11, [], 'main.Goal')

    # Events listed in the Transaction.EXECUTION_EVENTS get a 'transaction'
    # field populated in the 'extra' field when viewing the event activity.
    GOAL_WITHDRAWAL_EXECUTED = (12, ['txid'], 'main.Goal')
    GOAL_DEPOSIT_EXECUTED = (13, ['txid'], 'main.Goal')
    GOAL_DIVIDEND_DISTRIBUTION = (14, ['txid'], 'main.Goal')
    GOAL_FEE_LEVIED = (15, ['txid', 'cause'], 'main.Goal')
    GOAL_REBALANCE_EXECUTED = (16, ['txid'], 'main.Goal')
    GOAL_TRANSFER_EXECUTED = (17, ['txid'], 'main.Goal')
    GOAL_ORDER_DISTRIBUTION = (18, ['txid'], 'main.Goal')

    def __init__(self, id, log_keys, obj_class: str):
        """
        Create an Event enumeration.
        This is overridden to have all the extra data we want.

        :param obj_class: What is the required class of the obj logged?
        """
        if 'reason' in log_keys:
            raise ValueError("'reason' is a reserved event logging key. Maybe "
                             "you should use the 'reason' argument to the "
                             "'Event.log' method instead?")
        self.log_keys = log_keys
        self._obj_class = obj_class

    @property
    def obj_class(self):
        if isinstance(self._obj_class, six.string_types):
            app_label, model_name = self._obj_class.rsplit('.', 1)
            # using AppConfig only works for Django 1.9+
            # self._obj_class = AppConfig.get_model(app_label, model_name)
            # use this instead of Django 1.7<1.9
            self._obj_class = get_model(app_label, model_name)
        return self._obj_class

    def log(self, reason, *args, user=None, obj=None, support_request_id=None):
        """
        Log the event to the event log
        :param reason: The reason this event occurred. The cause of the event.
        :param args:
            The arguments appropriate for the particular event.
            All are required and positional.
            repr() will be called on each argument before logging.
        :param user: The user performing the event
        :param obj: The object the event concerns.
                    Objects of a ClientAccount type will show up on
                        the account activity stream.
                    Objects of a Goal type will show up on the goal and
                        account activity streams.
        :param support_request_id: if this action's been performed by support
                                request
        :return: The event that was logged.
        """
        if not isinstance(obj, self.obj_class):
            raise TypeError("obj parameter: {} is not of required type: {}"
                            .format(type(obj), self.obj_class))

        if len(args) != len(self.log_keys):
            raise InvalidLogParams(self, args)

        log_data = dict(zip(self.log_keys, map(repr, args)))
        log_data['reason'] = reason
        if support_request_id:
            log_data['support_request_id'] = support_request_id
        return event_log(user, self.name, log_data, obj=obj)
