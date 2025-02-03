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
        self.num_bottles = 3
        self.current_num_bottles = self.num_bottles
        self.is_bottle_on_tray = True

    def initialize(self):
        # Initialize all the hardwares
        self.hardware.initialize()

        # transition
        self.trigger("initialize_finished")

    def before_cycle_stage_1(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 1:
            self.hardware.tray_to_pump()
            self.current_num_bottles -= 1

        else:
            print("No bottles. Experiment stops!")
            sys.exit()

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
        # Check the boundary condition
        if self.num_bottles >= 2:
            parallel_action_handle(
                self.hardware.fill_bottle, self.hardware.tray_to_pump
            )
            self.current_num_bottles = max(0, self.current_num_bottles - 1)

        else:
            self.hardware.fill_bottle()

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
        # Check the boundary condition
        if self.num_bottles >= 2:
            parallel_action_handle(
                self.hardware.fill_bottle, self.hardware.pump_to_measure
            )

        else:
            self.hardware.pump_to_measure()

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
        # Check the boundary condition
        if self.num_bottles >= 3:
            parallel_action_handle(self.hardware.tray_to_pump, self.hardware.measure_UV)
            self.current_num_bottles = max(0, self.current_num_bottles - 1)
        else:
            self.hardware.measure_UV()

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
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                pass
            case 2:
                self.hardware.pump_to_measure()
            case _:
                parallel_action_handle(
                    self.hardware.fill_bottle, self.hardware.pump_to_measure
                )

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
        # Check the boundary condition
        if self.num_bottles >= 4:
            self.hardware.tray_to_pump()
            self.current_num_bottles = max(0, self.current_num_bottles - 1)
        else:
            pass

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
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                self.hardware.measure_DLS()
            case 2:
                parallel_action_handle(
                    self.hardware.measure_DLS, self.hardware.measure_UV
                )
            case 3:
                parallel_action_handle(
                    self.hardware.pump_to_measure,
                    self.hardware.measure_DLS,
                    self.hardware.measure_UV,
                )
            case _:
                parallel_action_handle(
                    self.hardware.fill_bottle,
                    self.hardware.pump_to_measure,
                    self.hardware.measure_DLS,
                    self.hardware.measure_UV,
                )

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
        # Check the boundary condition
        if self.num_bottles >= 5:
            self.hardware.tray_to_pump()
            self.current_num_bottles = max(0, self.current_num_bottles - 1)
        else:
            pass

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
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                pass
            case 2:
                self.hardware.measure_DLS()
            case 3:
                parallel_action_handle(
                    self.hardware.measure_DLS,
                    self.hardware.measure_UV,
                )
            case 4:
                parallel_action_handle(
                    self.hardware.measure_DLS,
                    self.hardware.measure_UV,
                )
            case _:
                parallel_action_handle(
                    self.hardware.fill_bottle,
                    self.hardware.measure_DLS,
                    self.hardware.measure_UV,
                )

        # transition
        self.trigger("command_finished")

    ############################

    def cycle_stage_1(self):
        # Send command
        self.hardware.measure_to_tray()  # 1st measure_to_tray

        # transition
        self.trigger("command_finished")

    def cycle_stage_2(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 4:
            self.hardware.pump_to_measure()
        else:
            pass

        # transition
        self.trigger("command_finished")

    def cycle_stage_3(self):
        # Send command
        self.feedback = self.hardware.rotate_table_m()

        if self.feedback:
            self.feedback = None
            # transition
            self.trigger("command_finished")

    def cycle_stage_4(self):
        # Send command
        # Check the boundary condition (3rd DLS and 4th UV)
        match self.num_bottles:
            case 1:
                pass
            case 2:
                pass
            case 3:
                self.hardware.measure_DLS()
            case _:
                parallel_action_handle(
                    self.hardware.measure_DLS, self.hardware.measure_UV
                )

        if self.current_num_bottles == 0:
            self.is_bottle_on_tray = False

        # transition
        self.trigger("command_finished")

    def cycle_stage_branch(self):
        # Send command
        self.hardware.tray_to_pump()
        self.current_num_bottles = max(0, self.current_num_bottles - 1)

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
        self.hardware.fill_bottle()

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
        # Check the boundary condition (2nd measure_to_tray)
        if self.num_bottles >= 2:
            self.hardware.measure_to_tray()
        else:
            pass

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_3(self):
        # Send command
        # Check the boundary condition (5th pump_to_measure)
        if self.num_bottles >= 5:
            self.hardware.pump_to_measure()
        else:
            pass

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
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                pass
            case 2:
                pass
            case 3:
                self.hardware.measure_to_tray()
            case 4:
                parallel_action_handle(
                    self.hardware.measure_DLS, self.hardware.measure_to_tray
                )
            case _:
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
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                pass
            case 2:
                pass
            case 3:
                pass
            case 4:
                self.hardware.measure_to_tray()
            case _:
                parallel_action_handle(
                    self.hardware.measure_DLS, self.hardware.measure_to_tray
                )

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
        # Check the boundary condition
        if self.num_bottles >= 5:
            self.hardware.measure_to_tray()
        else:
            pass

        # transition: last state finished => end the server

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
