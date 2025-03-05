import os

from mf_system.logic.state_machine_dispense import StateMachineDispense
from mf_system.logic.state_machine_measure import StateMachineMeasure
from mf_system.logic.state_machine_boundary_con import StateMachine
from mf_system.logic.utils import (
    states,
    states_dispense,
    states_measure,
    transitions,
    transitions_dispense,
    transitions_measure,
)


class Controller:
    def __init__(
        self,
        user_input,
        config_root_path="c:/Users/Yu/Desktop/mf-system/src/mf_system/database/",
    ):
        self.user_input = user_input
        self.hw_config_path = os.path.join(config_root_path, "hardware_config.yaml")
        self.sample_config_path = os.path.join(config_root_path, "sample_config.json")

    def data_parse(self):
        after_parsed_data = self.user_input
        return after_parsed_data

    def generate_experiment(self):
        select = self.data_parse()

        if select == "Dispense Only":
            self.sm = StateMachineDispense(
                states=states_dispense,
                transitions=transitions_dispense,
                name="State Machine Dispense",
                num_bottles=5,
                test_mode=True,
                hardware_config_path=self.hw_config_path,
                sample_config_path=self.sample_config_path,
            )

        elif select == "Measure Only":
            self.sm = StateMachineMeasure(
                states=states_measure,
                transitions=transitions_measure,
                name="State Machine Measure",
                num_bottles=4,
                test_mode=True,
                hardware_config_path=self.hw_config_path,
                sample_config_path=self.sample_config_path,
            )

        else:
            self.sm = StateMachine(
                states=states,
                transitions=transitions,
                name="State Machine",
                num_bottles=5,
                test_mode=True,
                hardware_config_path=self.hw_config_path,
                sample_config_path=self.sample_config_path,
            )

    def run_experiment(self):
        self.generate_experiment()
        self.sm.auto_run()
