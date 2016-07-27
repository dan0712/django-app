from django.db.models import signals
from django.test import TestCase

from main.models import User
from user.connectors import create_avatar


class BaseTest(TestCase):
    class no_signal():
        """ Temporarily disconnect a model from a signal """

        def __init__(self, signal, receiver, sender, dispatch_uid=None):
            self.signal = signal
            self.receiver = receiver
            self.sender = sender
            self.dispatch_uid = dispatch_uid

        def __enter__(self):
            self.signal.disconnect(
                receiver=self.receiver,
                sender=self.sender,
                dispatch_uid=self.dispatch_uid,
                weak=False
            )

        def __exit__(self, type, value, traceback):
            self.signal.connect(
                receiver=self.receiver,
                sender=self.sender,
                dispatch_uid=self.dispatch_uid,
                weak=False
            )


class GenerateAvatarTest(BaseTest):
    def test_user_without_avatar(self):
        with self.no_signal(signal=signals.post_save,
                            receiver=create_avatar,
                            sender=User):
            user = User.objects.create()
        self.assertFalse(user.avatar)
        create_avatar(User, user)
        self.assertTrue(user.avatar)
