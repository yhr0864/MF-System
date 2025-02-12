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
    def __init__(self, user_input, config_file=1):
        self.user_input = user_input
        self.config = config_file

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
            )

        elif select == "Measure Only":
            self.sm = StateMachineMeasure(
                states=states_measure,
                transitions=transitions_measure,
                name="State Machine Measure",
                num_bottles=4,
            )

        else:
            self.sm = StateMachine(
                states=states,
                transitions=transitions,
                name="State Machine",
                num_bottles=5,
            )

    def run_experiment(self):
        self.generate_experiment()
        self.sm.auto_run()
