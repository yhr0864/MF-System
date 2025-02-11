import sys
import time
import logging

from mf_system.hardware.hardware import Hardware
from mf_system.logic.utils import states, transitions, parallel_action_handle
from mf_system.logic.state_machine import StateMachine


class StateMachine(StateMachine):
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
            self.hardware.fill_bottle()

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_4(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("before_cycle_stage_4: rotate_table_p")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_5(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 2:
            print(
                f"before_cycle_stage_5: fill_bottle + pump_to_measure - cur_bottles:{self.current_num_bottles}"
            )
            # parallel_action_handle(
            #     self.hardware.fill_bottle, self.hardware.pump_to_measure
            # )

        else:
            print(
                f"before_cycle_stage_5: pump_to_measure - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.pump_to_measure()

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_6(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("before_cycle_stage_6: rotate_table_m")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_7(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 3:
            print(
                f"before_cycle_stage_7: tray_to_pump + measure_UV - cur_bottles: {self.current_num_bottles}"
            )
            # parallel_action_handle(self.hardware.tray_to_pump, self.hardware.measure_UV)
            self.current_num_bottles = max(0, self.current_num_bottles - 1)
        else:
            print(
                f"before_cycle_stage_7: measure_UV - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.measure_UV()

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_8(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("before_cycle_stage_8: rotate_table_p")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_9(self):
        # Send command
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                print(
                    f"before_cycle_stage_9: pass - cur_bottles: {self.current_num_bottles}"
                )
                pass
            case 2:
                # self.hardware.pump_to_measure()
                print(
                    f"before_cycle_stage_9: pump_to_measure - cur_bottles: {self.current_num_bottles}"
                )
            case _:
                # parallel_action_handle(
                #     self.hardware.fill_bottle, self.hardware.pump_to_measure
                # )
                print(
                    f"before_cycle_stage_9: pump_to_measure + fill_bottle - cur_bottles: {self.current_num_bottles}"
                )

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_10(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("before_cycle_stage_10: rotate_table_m")
        if self.feedback:
            self.feedback = None

            # transition
        self.trigger("command_finished")

    def before_cycle_stage_11(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 4:
            print(
                f"before_cycle_stage_11: tray_to_pump - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.tray_to_pump()
            self.current_num_bottles = max(0, self.current_num_bottles - 1)
        else:
            print(
                f"before_cycle_stage_11: pass - cur_bottles: {self.current_num_bottles}"
            )
            pass

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_12(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("before_cycle_stage_12: rotate_table_p")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_13(self):
        # Send command
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                # self.hardware.measure_DLS()
                print(
                    f"before_cycle_stage_13: measure_DLS - cur_bottles: {self.current_num_bottles}"
                )
            case 2:
                print(
                    f"before_cycle_stage_13: measure_DLS + measure_UV - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS, self.hardware.measure_UV
                # )
            case 3:
                print(
                    f"before_cycle_stage_13: measure_DLS + measure_UV + pump_to_measure - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.pump_to_measure,
                #     self.hardware.measure_DLS,
                #     self.hardware.measure_UV,
                # )
            case _:
                print(
                    f"before_cycle_stage_13: measure_DLS + measure_UV + pump_to_measure + fill_bottle - cur_bottles: {self.current_num_bottles}"
                )
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
        # self.feedback = self.hardware.rotate_table_m()
        print("before_cycle_stage_14: rotate_table_m")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_15(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 5:
            print(
                f"before_cycle_stage_15: tray_to_pump - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.tray_to_pump()
            self.current_num_bottles = max(0, self.current_num_bottles - 1)
        else:
            print(
                f"before_cycle_stage_15: pass - cur_bottles: {self.current_num_bottles}"
            )
            pass

        # transition
        self.trigger("command_finished")

    def before_cycle_stage_16(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("before_cycle_stage_16: rotate_table_p")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def before_cycle_stage_17(self):
        # Send command
        # Check the boundary condition
        match self.num_bottles:
            case 1:
                print(
                    f"before_cycle_stage_17: pass - cur_bottles: {self.current_num_bottles}"
                )
            case 2:
                print(
                    f"before_cycle_stage_17: measure_DLS - cur_bottles: {self.current_num_bottles}"
                )
                # self.hardware.measure_DLS()
            case 3:
                print(
                    f"before_cycle_stage_17: measure_DLS + measure_UV - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS,
                #     self.hardware.measure_UV,
                # )
            case 4:
                print(
                    f"before_cycle_stage_17: measure_DLS + measure_UV - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS,
                #     self.hardware.measure_UV,
                # )
            case _:
                print(
                    f"before_cycle_stage_17: measure_DLS + measure_UV + fill_bottle - cur_bottles: {self.current_num_bottles}"
                )
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
        print(
            f"cycle_stage_1: measure_to_tray - cur_bottles: {self.current_num_bottles}"
        )
        # self.hardware.measure_to_tray()  # 1st measure_to_tray

        if self.num_bottles == 1:
            print("Experiment Finished!")
            self.stop()

        # transition
        self.trigger("command_finished")

    def cycle_stage_2(self):
        # Send command
        # Check the boundary condition
        if self.num_bottles >= 4:
            print(
                f"cycle_stage_2: pump_to_measure - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.pump_to_measure()
        else:
            print("cycle_stage_2: pass")
            pass

        # transition
        self.trigger("command_finished")

    def cycle_stage_3(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("cycle_stage_3: rotate_table_m")

        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def cycle_stage_4(self):
        # Send command
        # Check the boundary condition (3rd DLS and 4th UV)
        match self.num_bottles:
            case 1 | 2:
                print(f"cycle_stage_4: pass - cur_bottles: {self.current_num_bottles}")
            case 3:
                print(
                    f"cycle_stage_4: measure_DLS - cur_bottles: {self.current_num_bottles}"
                )
                # self.hardware.measure_DLS()
            case _:
                print(
                    f"cycle_stage_4: measure_DLS + measure_UV - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS, self.hardware.measure_UV
                # )

        # transition
        self.trigger("command_finished")

    def cycle_stage_5(self):
        # Send command
        print(f"cycle_stage_5: tray_to_pump - cur_bottles: {self.current_num_bottles}")
        # self.hardware.tray_to_pump()
        self.current_num_bottles = max(0, self.current_num_bottles - 1)

        # transition
        self.trigger("command_finished")

    def cycle_stage_6(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_p()
        print("cycle_stage_6: rotate_table_p")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def cycle_stage_7(self):
        # Send command
        print(f"cycle_stage_7: fill_bottle - cur_bottles: {self.current_num_bottles}")
        # self.hardware.fill_bottle()

        # transition
        self.trigger("command_finished")

    ########################################

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
        # Check the boundary condition (2nd measure_to_tray)
        # self.hardware.measure_to_tray()
        print(
            f"after_cycle_stage_2: measure_to_tray - cur_bottles: {self.current_num_bottles}"
        )
        if self.num_bottles == 2:
            print("Experiment Finished!")
            self.stop()

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_3(self):
        # Send command
        # Check the boundary condition (5th pump_to_measure)
        if self.num_bottles >= 5:
            print(
                f"after_cycle_stage_3: pump_to_measure - cur_bottles: {self.current_num_bottles}"
            )
            # self.hardware.pump_to_measure()
        else:
            print(
                f"after_cycle_stage_3: pass - cur_bottles: {self.current_num_bottles}"
            )
            pass

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_4(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("after_cycle_stage_4: rotate_table_m")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def after_cycle_stage_5(self):
        # Send command
        # Check the boundary condition
        match self.num_bottles:
            case 1 | 2:
                print(
                    f"after_cycle_stage_5: pass - cur_bottles: {self.current_num_bottles}"
                )
            case 3:
                print(
                    f"after_cycle_stage_5: measure_to_tray - cur_bottles: {self.current_num_bottles}"
                )
                # self.hardware.measure_to_tray()
                print("Experiment Finished!")
                self.stop()
            case 4:
                print(
                    f"after_cycle_stage_5: measure_to_tray + measure_DLS - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS, self.hardware.measure_to_tray
                # )
            case _:
                print(
                    f"after_cycle_stage_5: measure_to_tray + measure_DLS + measure_UV - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS,
                #     self.hardware.measure_UV,
                #     self.hardware.measure_to_tray,
                # )

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_6(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("after_cycle_stage_6: rotate_table_m")
        if self.feedback:
            self.feedback = None
            # transition
        self.trigger("command_finished")

    def after_cycle_stage_7(self):
        # Send command
        # Check the boundary condition
        match self.num_bottles:
            case 1 | 2 | 3:
                print(
                    f"after_cycle_stage_7: pass - cur_bottles: {self.current_num_bottles}"
                )
            case 4:
                print(
                    f"after_cycle_stage_7: measure_to_tray - cur_bottles: {self.current_num_bottles}"
                )
                # self.hardware.measure_to_tray()
                print("Experiment Finished!")
                self.stop()
            case _:
                print(
                    f"after_cycle_stage_7: measure_to_tray + measure_DLS - cur_bottles: {self.current_num_bottles}"
                )
                # parallel_action_handle(
                #     self.hardware.measure_DLS, self.hardware.measure_to_tray
                # )

        # transition
        self.trigger("command_finished")

    def after_cycle_stage_8(self):
        # Send command
        # self.feedback = self.hardware.rotate_table_m()
        print("after_cycle_stage_8: rotate_table_m")
        if self.feedback:
            self.feedback = None
        # transition
        self.trigger("command_finished")

    def after_cycle_stage_9(self):
        # Send command
        # Check the boundary condition

        print(
            f"after_cycle_stage_9: measure_to_tray - cur_bottles: {self.current_num_bottles}"
        )
        # self.hardware.measure_to_tray()
        print("Experiment Finished!")
        self.stop()


if __name__ == "__main__":
    # Create the table state machine
    table = StateMachine(
        states=states, transitions=transitions, name="State Machine", num_bottles=5
    )

    table.auto_run()
