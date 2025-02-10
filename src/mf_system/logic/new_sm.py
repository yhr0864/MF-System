from transitions import Machine
from concurrent.futures import ThreadPoolExecutor
import time


class BottleFillingSystem:
    states = [
        "idle",
        "arm_placing_on_slot1",
        "turntable_rotating_to_slot2",
        "dispensing_and_placing",
        "turntable_rotating_to_slot1",
        "arm_picking_filled",
        "done",
    ]

    def __init__(self, total_bottles=50):
        self.total_bottles = total_bottles
        self.processed_bottles = 0  # Track completed bottles
        self.current_bottle_on_slot1 = None  # Track the bottle on Slot 1

        # Initialize the state machine
        self.machine = Machine(
            model=self, states=BottleFillingSystem.states, initial="idle"
        )

        # Define transitions
        self.machine.add_transition("start", "idle", "arm_placing_on_slot1")
        self.machine.add_transition(
            "empty_placed", "arm_placing_on_slot1", "turntable_rotating_to_slot2"
        )
        self.machine.add_transition(
            "rotated_to_slot2", "turntable_rotating_to_slot2", "dispensing_and_placing"
        )
        self.machine.add_transition(
            "dispensing_complete",
            "dispensing_and_placing",
            "turntable_rotating_to_slot1",
        )
        self.machine.add_transition(
            "rotated_to_slot1", "turntable_rotating_to_slot1", "arm_picking_filled"
        )
        self.machine.add_transition(
            "filled_placed",
            "arm_picking_filled",
            "arm_placing_on_slot1",
            after="check_completion",
        )

    def check_completion(self):
        self.processed_bottles += 1
        if self.processed_bottles >= self.total_bottles:
            self.to_done()

    # State entry actions
    def on_enter_arm_placing_on_slot1(self):
        print(
            f"[Bottle {self.processed_bottles + 1}] Robotic arm placing empty bottle on Slot 1..."
        )
        # self.hardware.tray_to_pump()  # Pick up empty bottle and place on Slot 1
        self.empty_placed()

    def on_enter_turntable_rotating_to_slot2(self):
        print(
            f"[Bottle {self.processed_bottles + 1}] Turntable rotating 180° to move Slot 1 to Slot 2..."
        )
        # self.hardware.rotate_table()  # Rotate turntable 180°
        self.rotated_to_slot2()

    def on_enter_dispensing_and_placing(self):
        print(
            f"[Bottle {self.processed_bottles + 1}] Starting dispensing and placing next bottle in parallel..."
        )

        # Start dispensing in a separate thread
        def dispense():
            # self.hardware.dispense()  # Dispense liquid into the bottle at Slot 2
            self.dispensing_complete()  # Transition after dispensing is done

        # Start placing the next empty bottle in a separate thread
        def place_next_bottle():
            # self.hardware.tray_to_pump()  # Pick up the next empty bottle and place on Slot 1
            pass

        # Run both tasks in parallel
        with ThreadPoolExecutor() as executor:
            f1 = executor.submit(dispense)
            f2 = executor.submit(place_next_bottle)

            f1.result()
            f2.result()

    def on_enter_turntable_rotating_to_slot1(self):
        print(
            f"[Bottle {self.processed_bottles + 1}] Turntable rotating 180° to move Slot 2 back to Slot 1..."
        )
        # self.hardware.rotate_table()  # Rotate turntable 180°
        self.rotated_to_slot1()

    def on_enter_arm_picking_filled(self):
        print(
            f"[Bottle {self.processed_bottles + 1}] Robotic arm picking up filled bottle from Slot 1..."
        )
        # self.hardware.pump_to_tray()  # Pick up filled bottle and place on tray
        self.filled_placed()

    def on_enter_done(self):
        print(f"Process completed! All {self.total_bottles} bottles are filled.")


if __name__ == "__main__":
    # Run the system
    system = BottleFillingSystem(total_bottles=10)

    system.start()
