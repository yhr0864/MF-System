class Pump:
    __is_opened = False
    _name = "pump"

    @classmethod
    def open_bus(cls):
        cls.__is_opened = True
        print("Bus opened")

    @classmethod
    def close_bus(cls):
        cls.__is_opened = False
        print("Bus closed")

    @classmethod
    def is_running(cls):
        return cls.__is_opened


p1 = Pump()
p2 = Pump()
p1._name = "bump"
print(p1._name)
import hardware, logic, ui
