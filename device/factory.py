from device.midevice import Plug, MiSmartPowerPlug2, MiSmartPowerPlug3
from model.device import Device


class PlugFactory:

    @staticmethod
    def generate_plug(device: Device) -> Plug:
        if device.model == "chuangmi.plug.212a01":
            return MiSmartPowerPlug2(device.host, device.token, device.did)
        elif device.model == "cuco.plug.v3":
            return MiSmartPowerPlug3(device.host, device.token)
