import time

from .service import Service


class CheckMailbox(Service):
    def _run(self):
        while self._tree.mailbox_size() > 0:
            timeout, msg = self._tree.read_message()
            now = time.time_ns() // 1_000_000
            if timeout > now and msg.condition():
                self._tree.update_blackboard(*msg.request)
                return  # successfully read message, sleep until next
