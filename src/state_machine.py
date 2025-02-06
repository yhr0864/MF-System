import time
import logging
from typing import List, Optional

from transitions import Machine

from hardware import Hardware


class StateMachine:
    def __init__(
        self,
        states: List[str],
        transitions: List[dict],
        name: str,
        num_bottles: int,
        test_mode: bool = False,
        initial: str = "initialize",
        ignore_invalid_triggers: bool = True,
        auto_transitions: bool = False,
    ):
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial=initial,
            name=name,
            ignore_invalid_triggers=ignore_invalid_triggers,
            auto_transitions=auto_transitions,
        )

        self.hardware: Optional[Hardware] = None if test_mode else Hardware()
        self.feedback = None

        self.num_bottles = num_bottles
        self.current_num_bottles = num_bottles
        self.running = True  # To control `auto_run` execution

    @property
    def is_bottle_on_tray(self) -> bool:
        return self.current_num_bottles > 0

    def initialize(self):
        if self.hardware:
            self.hardware.initialize()
        self.trigger("initialize_finished")

    def auto_run(self):
        while self.running:
            action = getattr(self, self.state, lambda: None)
            action()
            time.sleep(1)

    def stop(self):
        """Gracefully stop the auto-run loop."""
        self.running = False
