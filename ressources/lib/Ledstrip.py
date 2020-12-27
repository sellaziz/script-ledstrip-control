from bluepy import btle
import numpy as np
import logging

UUID_CHARACTERISTIC_RECV = btle.UUID('ffd1')
UUID_CHARACTERISTIC_WRITE = btle.UUID('ffd5')
UUID_CHARACTERISTIC_DEVICE_NAME = btle.UUID('2a00')
mac_address='07:1A:02:00:0D:B3'

class LedStrip(btle.Peripheral):
    def __init__(self, deviceAddr=mac_address, addrType=btle.ADDR_TYPE_PUBLIC, iface=None):
        super(LedStrip, self).__init__(deviceAddr=None, addrType=btle.ADDR_TYPE_PUBLIC, iface=None)
        self._oldRGB = 0,0,0
        self._RGBhandle = 0
        self.mac_address=mac_address
        self.fade_mode=True
        self.fade_step = 20
        self.setup()
    
    def setup(self):
        try:
            self.connect(self.mac_address)
            self.getRGBHandle()
            self.is_connected=True
            logging.debug('Device connected')
        except ConnectionError as exp:
            print("ConnectionError {}".format(exp))
    
    def getRGBHandle(self):
        """Figure out the Handle for the values of RGB
        """
        self._RGBhandle = self.getServiceByUUID(UUID_CHARACTERISTIC_WRITE).getCharacteristics()[1].getHandle()
    
    def setRGB(self, R=0, G=0, B=0):
        """Set values of RGB for the ledstrip. It sends the value to the Bluetooth LE controller in the corresponding format : 56 RR GG BB 00 f0 aa

        Args:
            R (int): value of Red. Defaults to 0.
            G (int): value of Green. Defaults to 0.
            B (int): value of Blue. Defaults to 0.
        """
        valstring = """56{0}{1}{2}00f0aa""".format( "0x{:02x}".format(R)[2:],"0x{:02x}".format(G)[2:],  "0x{:02x}".format(B)[2:])
        val = bytearray.fromhex(valstring)
        logging.debug("Send bytes array {}".format(valstring))
        self.writeCharacteristic(self._RGBhandle, val)
        self._oldRGB=R,G,B
    
    def fadeIntoRGB(self, R=0, G=0, B=0, step=50):
        """Set values of RGB for the ledstrip to make a transition between old and new RGB value

        Args:
            R (int): value of Red. Defaults to 0.
            G (int): value of Green. Defaults to 0.
            B (int): value of Blue. Defaults to 0.
            step (int): number of transitions. Defaults to 50.
        """
        R_arr = np.linspace(self._oldRGB[0], R, step)
        G_arr = np.linspace(self._oldRGB[1], G, step)
        B_arr = np.linspace(self._oldRGB[2], B, step)
        for k in range(step):
            self.setRGB(int(R_arr[k]),int(G_arr[k]),int(B_arr[k]))

if __name__ == "__main__":
    ledstrip = LedStrip(mac_address)
    ledstrip.setRGB(0, 0, 255)
    ledstrip.disconnect()
    pass
