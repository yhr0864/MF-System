from concurrent.futures import ThreadPoolExecutor


def parallel_action_handle(*args):
    futures = []
    with ThreadPoolExecutor() as executor:
        for arg in args:
            futures.append(executor.submit(arg))

        for future in futures:
            future.result()


states = [
    "initialize",
    "before_cycle_stage_1",
    "before_cycle_stage_2",
    "before_cycle_stage_3",
    "before_cycle_stage_4",
    "before_cycle_stage_5",
    "before_cycle_stage_6",
    "before_cycle_stage_7",
    "before_cycle_stage_8",
    "before_cycle_stage_9",
    "before_cycle_stage_10",
    "before_cycle_stage_11",
    "before_cycle_stage_12",
    "before_cycle_stage_13",
    "before_cycle_stage_14",
    "before_cycle_stage_15",
    "before_cycle_stage_16",
    "before_cycle_stage_17",
    "cycle_stage_1",
    "cycle_stage_2",
    "cycle_stage_3",
    "cycle_stage_4",
    "cycle_stage_5",
    "cycle_stage_6",
    "cycle_stage_7",
    "after_cycle_stage",
    "after_cycle_stage_2",
    "after_cycle_stage_3",
    "after_cycle_stage_4",
    "after_cycle_stage_5",
    "after_cycle_stage_6",
    "after_cycle_stage_7",
    "after_cycle_stage_8",
    "after_cycle_stage_9",
]

transitions = [
    {
        "trigger": "initialize_finished",
        "source": "initialize",
        "dest": "before_cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_1",
        "dest": "before_cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_2",
        "dest": "before_cycle_stage_3",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_3",
        "dest": "before_cycle_stage_4",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_4",
        "dest": "before_cycle_stage_5",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_5",
        "dest": "before_cycle_stage_6",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_6",
        "dest": "before_cycle_stage_7",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_7",
        "dest": "before_cycle_stage_8",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_8",
        "dest": "before_cycle_stage_9",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_9",
        "dest": "before_cycle_stage_10",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_10",
        "dest": "before_cycle_stage_11",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_11",
        "dest": "before_cycle_stage_12",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_12",
        "dest": "before_cycle_stage_13",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_13",
        "dest": "before_cycle_stage_14",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_14",
        "dest": "before_cycle_stage_15",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_15",
        "dest": "before_cycle_stage_16",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_16",
        "dest": "before_cycle_stage_17",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_17",
        "dest": "cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_1",
        "dest": "cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_2",
        "dest": "cycle_stage_3",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_3",
        "dest": "cycle_stage_4",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_4",
        "dest": "cycle_stage_5",
        "conditions": "is_bottle_on_tray",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_5",
        "dest": "cycle_stage_6",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_6",
        "dest": "cycle_stage_7",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_7",
        "dest": "cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_4",
        "dest": "after_cycle_stage",
        "unless": "is_bottle_on_tray",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage",
        "dest": "after_cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_2",
        "dest": "after_cycle_stage_3",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_3",
        "dest": "after_cycle_stage_4",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_4",
        "dest": "after_cycle_stage_5",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_5",
        "dest": "after_cycle_stage_6",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_6",
        "dest": "after_cycle_stage_7",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_7",
        "dest": "after_cycle_stage_8",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_8",
        "dest": "after_cycle_stage_9",
    },
]

states_dispense = [
    "initialize",
    "before_cycle_stage_1",
    "before_cycle_stage_2",
    "before_cycle_stage_3",
    "cycle_stage_1",
    "cycle_stage_2",
    "cycle_stage_3",
    "after_cycle_stage",
    "after_cycle_stage_2",
]

transitions_dispense = [
    {
        "trigger": "initialize_finished",
        "source": "initialize",
        "dest": "before_cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_1",
        "dest": "before_cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_2",
        "dest": "before_cycle_stage_3",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_3",
        "dest": "cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_1",
        "dest": "cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_2",
        "dest": "cycle_stage_3",
        "conditions": "is_bottle_on_tray",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_3",
        "dest": "cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_2",
        "dest": "after_cycle_stage",
        "unless": "is_bottle_on_tray",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage",
        "dest": "after_cycle_stage_2",
    },
]

states_measure = [
    "initialize",
    "before_cycle_stage_1",
    "before_cycle_stage_2",
    "before_cycle_stage_3",
    "before_cycle_stage_4",
    "before_cycle_stage_5",
    "cycle_stage_1",
    "cycle_stage_2",
    "cycle_stage_3",
    "after_cycle_stage",
    "after_cycle_stage_2",
    "after_cycle_stage_3",
    "after_cycle_stage_4",
]

transitions_measure = [
    {
        "trigger": "initialize_finished",
        "source": "initialize",
        "dest": "before_cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_1",
        "dest": "before_cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_2",
        "dest": "before_cycle_stage_3",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_3",
        "dest": "before_cycle_stage_4",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_4",
        "dest": "before_cycle_stage_5",
    },
    {
        "trigger": "command_finished",
        "source": "before_cycle_stage_5",
        "dest": "cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_1",
        "dest": "cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_2",
        "dest": "cycle_stage_3",
        "conditions": "is_bottle_on_tray",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_3",
        "dest": "cycle_stage_1",
    },
    {
        "trigger": "command_finished",
        "source": "cycle_stage_2",
        "dest": "after_cycle_stage",
        "unless": "is_bottle_on_tray",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage",
        "dest": "after_cycle_stage_2",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_2",
        "dest": "after_cycle_stage_3",
    },
    {
        "trigger": "command_finished",
        "source": "after_cycle_stage_3",
        "dest": "after_cycle_stage_4",
    },
]
