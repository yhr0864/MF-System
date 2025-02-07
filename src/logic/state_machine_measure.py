import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from src.logic.state_machine import StateMachine
from src.hardware.hardware import Hardware
from src.logic.utils import states_measure, transitions_measure, parallel_action_handle


class StateMachineMeasure(StateMachine):
    def before_cycle_stage_1(self):
        # Send command
        # Check the boundary condition
        print(
            f"before_cycle_stage_1: tray_to_measure - cur_bottles: {self.current_num_bottles}"
        )
        # self.hardware.tray_to_measure()
        self.current_num_bottles -= 1

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_2(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("before_cycle_stage_2: rotate_table_m")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_3(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 2:
            print(
                f"before_cycle_stage_3: measure_UV + tray_to_measure - cur_bottles: {self.current_num_bottles}"
            )
            # parallel_action_handle(
            #     self.hardware.measure_UV, self.hardware.tray_to_measure
            # )
            self.current_num_bottles = max(0, self.current_num_bottles - 1)

        else:
            print(
                f"before_cycle_stage_3: measure_UV - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.measure_UV()

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_4(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("before_cycle_stage_4: rotate_table_m")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_5(self):
        # Send command
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                print(
                    f"before_cycle_stage_5: measure_DLS - cur_bottles: {self.current_num_bottles}"
                )
                # self.hardware.measure_DLS()
            case 2:

                print(
                    f"before_cycle_stage_5: measure_UV + measure_DLS - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_UV, self.hardware.measure_DLS
                # )
            case _:
                print(
                    f"before_cycle_stage_5: measure_UV + measure_DLS + Tray_to_measrue - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_UV,
                #     self.hardware.measure_DLS,
                #     self.hardware.tray_to_measure,
                # )
                self.current_num_bottles = max(0, self.current_num_bottles - 1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_1(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("cycle_stage_1: rotate_table_m")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def cycle_stage_2(self):
        # Send command
        match self.num_bottles:
            case 1:
                print(
                    f"cycle_stage_2: Measure_to_tray - cur_bottles: {self.current_num_bottles}"
                )
                # self.hardware.measure_to_tray()
                print("Experiment Finished!")
                sys.exit()
            case 2:
                print(
                    f"cycle_stage_2: measure_DLS + Measure_to_tray - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS, self.hardware.measure_to_tray
                # )
            case _:
                print(
                    f"cycle_stage_2: measure_UV + measure_DLS + Measure_to_tray - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_UV,
                #     self.hardware.measure_DLS,
                #     self.hardware.measure_to_tray,
                # )

        # transition
        self.trigger("command_finished")

    def cycle_stage_3(self):
        # Send command
        # Check the boundary condition

        print(
            f"cycle_stage_3: tray_to_measure - cur_bottles: {self.current_num_bottles}"
        )
        # self.hardware.tray_to_measure()
        self.current_num_bottles = max(0, self.current_num_bottles - 1)

        # transition
        self.trigger("command_finished")

    def after_cycle_stage(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("after_cycle_stage: rotate_table_m")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def after_cycle_stage_2(self):
        # Send command
        match self.num_bottles:
            case 1:
                print(
                    f"after_cycle_stage_2: pass - cur_bottles: {self.current_num_bottles}"
                )
            case 2:
                print(
                    f"after_cycle_stage_2: Measure_to_tray - cur_bottles: {self.current_num_bottles}"
                )
                # self.hardware.measure_to_tray()
                print("Experiment Finished!")
                sys.exit()
            case _:
                print(
                    f"after_cycle_stage_2: measure_DLS + Measure_to_tray - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(self.hardware.measure_DLS, self.hardware.measure_to_tray)

        self.trigger("command_finished")

    def after_cycle_stage_3(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("after_cycle_stage_3: rotate_table_m")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def after_cycle_stage_4(self):
        # Send command
        print(
            f"after_cycle_stage_4: Measure_to_tray - cur_bottles: {self.current_num_bottles}"
        )
        # self.hardware.measure_to_tray()
        print("Experiment Finished!")
        sys.exit()


if __name__ == "__main__":
    sm = StateMachineMeasure(
        states=states_measure,
        transitions=transitions_measure,
        name="State Machine Measure",
        num_bottles=4,
    )

    sm.auto_run()
