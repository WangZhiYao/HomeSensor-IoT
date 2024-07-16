from abc import abstractmethod

from miio import DeviceFactory


class MiDevice(DeviceFactory):

    def __init__(self, host: str, token: str):
        self.device = DeviceFactory.create(host, token)


class Plug(MiDevice):

    @abstractmethod
    def is_switch_on(self) -> bool:
        pass

    @abstractmethod
    def toggle(self, on: bool):
        pass


class MiSmartPowerPlug2(Plug):

    def __init__(self, host: str, token: str, did: str):
        super().__init__(host, token)
        self.did = did

    def is_switch_on(self):
        result = self.device.send(command="get_properties", parameters=[{'did': self.did, 'siid': 2, 'piid': 1}])
        return result[0]['value']

    def toggle(self, on: bool):
        self.device.send(
            command="set_properties",
            parameters=[{'did': self.did, 'siid': 2, 'piid': 1, 'value': on}]
        )


class MiSmartPowerPlug3(Plug):

    def is_switch_on(self):
        result = self.device.send(command="get_properties", parameters=[{'siid': 2, 'piid': 1}])
        return result[0]['value']

    def toggle(self, on: bool):
        self.device.send(
            command="set_properties",
            parameters=[{'siid': 2, 'piid': 1, 'value': on}]
        )
