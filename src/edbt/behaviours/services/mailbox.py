import time

from .service import Service


# XXX: I'm not convinced that it wouldn't be better to handle all mail
# from a single coroutine to avoid the additional overhead; potential
# optimization for later
class CheckMailbox(Service):
    async def _run(self):
        """Read from the BT mailbox until empty or a valid message is found"""
        while self._tree.mailbox_size() > 0:
            timeout, msg = self._tree.read_message()
            now = time.time_ns()
            if timeout > now and msg.condition():
                self._tree.update_blackboard(*msg.request)
                return
