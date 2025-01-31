import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from transitions import Machine

from hardware import Hardware
from utils import states, transitions


def parallel_action_handle(*args):
    futures = []
    with ThreadPoolExecutor() as executor:
        for arg in args:
            futures.append(executor.submit(arg))

        for future in futures:
            future.result()


class StateMachine:
    def __init__(self) -> None:
        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial="initialize",
            name="Micro Fluidic System",
            ignore_invalid_triggers=True,
            auto_transitions=False,
        )

        self.hardware = Hardware()
        self.feedback = None
        # Simulate 3 bottles
        self.cnt = 3
        self.is_bottle_on_tray = True

    def initialize(self):
        # Initialize all the hardwares
        self.hardware.initialize()

        # transition
        self.trigger("initialize_finished")

    def before_cycle_stage_1(self):
        # Send command
        # self.hardware.tray_to_pump()

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_2(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_3(self):
        # Send command
        # parallel_action_handle(self.hardware.fill_bottle, self.hardware.tray_to_pump)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_4(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_5(self):
        # Send command
        # parallel_action_handle(self.hardware.fill_bottle, self.hardware.pump_to_measure)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_6(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_7(self):
        # Send command
        # parallel_action_handle(self.hardware.tray_to_pump, self.hardware.measure_UV)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_8(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_9(self):
        # Send command
        # parallel_action_handle(self.hardware.fill_bottle, self.hardware.pump_to_measure)

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_10(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()

        if self.feedback:
            self.feedback = None

            # transition
            self.trigger("command_finished")

    def before_cycle_stage_11(self):
        # Send command
        # self.hardware.tray_to_pump()

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_12(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_13(self):
        # Send command
        # parallel_action_handle(
        #     self.hardware.fill_bottle,
        #     self.hardware.pump_to_measure,
        #     self.hardware.measure_DLS,
        #     self.hardware.measure_UV,
        # )

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_14(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_15(self):
        # Send command
        # self.hardware.tray_to_pump()

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_16(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def before_cycle_stage_17(self):
        # Send command
        # parallel_action_handle(
        #     self.hardware.fill_bottle,
        #     self.hardware.measure_DLS,
        #     self.hardware.measure_UV,
        # )

        # transition
        self.trigger("command_finished")

    ############################

    def cycle_stage_1(self):
        # Send command
        # self.hardware.measure_to_tray()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_2(self):
        # Send command
        # self.hardware.pump_to_measure()
        time.sleep(1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_3(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()
        time.sleep(1)

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def cycle_stage_4(self):
        # Send command
        # parallel_action_handle(self.hardware.measure_DLS, self.hardware.measure_UV)

        if self.cnt == 0:
            self.is_bottle_on_tray = False

        self.cnt -= 1

        # transition
        self.trigger("command_finished")

    def cycle_stage_branch(self):
        # Send command
        # self.hardware.tray_to_pump()

        # transition
        self.trigger("command_finished")

    def cycle_stage_6(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def cycle_stage_7(self):
        # Send command
        # self.hardware.fill_bottle()

        # transition
        self.trigger("command_finished")

    ########################################

    def after_cycle_stage(self):
        # Send command
        self.feedback = self.hardware.rotate_table_p()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_2(self):
        # Send command
        # self.hardware.measure_to_tray()

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_3(self):
        # Send command
        # self.hardware.pump_to_measure()

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_4(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_5(self):
        # Send command
        parallel_action_handle(
            self.hardware.measure_DLS,
            self.hardware.measure_UV,
            self.hardware.measure_to_tray,
        )

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_6(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_7(self):
        # Send command
        # parallel_action_handle(self.hardware.measure_DLS, self.hardware.measure_to_tray)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_8(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def after_cycle_stage_9(self):
        # Send command
        # self.hardware.measure_to_tray()

        # transition: last state finished => end the server
        self.machine.stop_server()
        sys.exit()

    def auto_run(self):
        while True:
            action = getattr(self, self.state, lambda: "No action for this state")
            if action:
                action()
            time.sleep(1)


if __name__ == "__main__":
    # Create the table state machine
    table = StateMachine()
