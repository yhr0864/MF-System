import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from transitions import Machine

from state_machine import StateMachine
from hardware import Hardware
from utils import states_dispense, transitions_dispense


def parallel_action_handle(*args):
    futures = []
    with ThreadPoolExecutor() as executor:
        for arg in args:
            futures.append(executor.submit(arg))

        for future in futures:
            future.result()


class StateMachineDispense(StateMachine):
    def before_cycle_stage_1(self):
        # Send command
        # Check the boundary condition

        print(
            f"before_cycle_stage_1: tray_to_pump - cur_bottles: {self.current_num_bottles}"
        )
        # self.hardware.tray_to_pump()
        self.current_num_bottles -= 1

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_2(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("before_cycle_stage_2: rotate_table_p")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_3(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 2:
            print(
                f"before_cycle_stage_3: fill_bottle + tray_to_pump - cur_bottles: {self.current_num_bottles}"
            )
            # parallel_action_handle(
            #     self.hardware.fill_bottle, self.hardware.tray_to_pump
            # )
            self.current_num_bottles = max(0, self.current_num_bottles - 1)

        else:
            print(
                f"before_cycle_stage_3: fill_bottle - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.fill_bottle()

        # transition
        self.trigger("command_finished")

    def cycle_stage_1(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("cycle_stage_1: rotate_table_p")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def cycle_stage_2(self):
        # Send command
        if self.num_bottles >= 2:
            print(
                f"cycle_stage_2: fill_bottle + pump_to_tray - cur_bottles: {self.current_num_bottles}"
            )
            # parallel_action_handle(
            #     self.hardware.fill_bottle, self.hardware.pump_to_tray
            # )

        else:
            print(
                f"cycle_stage_2: pump_to_tray - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.pump_to_tray()

            print("Experiment Finished!")
            sys.exit()

        if self.current_num_bottles == 0:
            self.is_bottle_on_tray = False

        # transition
        self.trigger("command_finished")

    def cycle_stage_3(self):
        # Send command
        # Check the boundary condition

        print(f"cycle_stage_3: tray_to_pump - cur_bottles: {self.current_num_bottles}")
        # self.hardware.tray_to_pump()
        self.current_num_bottles = max(0, self.current_num_bottles - 1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("after_cycle_stage: rotate_table_p")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def after_cycle_stage_2(self):
        # Send command
        print(
            f"after_cycle_stage_2: pump_to_tray - cur_bottles: {self.current_num_bottles}"
        )
        # self.hardware.pump_to_tray()
        print("Experiment Finished!")
        sys.exit()


if __name__ == "__main__":
    sm = StateMachineDispense(
        states=states_dispense,
        transitions=transitions_dispense,
        name="State Machine Dispense",
        num_bottles=5,
    )

    sm.auto_run()
