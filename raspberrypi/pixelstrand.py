"""
pixelstrand.py

Implement a custom Pixel Strand BLE Service using python-bluezero
PixelStrand Service: See GATT.md
Bluezero: https://github.com/ukBaz/python-bluezero

rsync -r . pi@raspberrypi:~/Documents/WallPhish

"""

import math
import logging

from bluezero import adapter
from bluezero import peripheral
from bluezero import tools as bztools

# Create module logger
logger = bztools.create_module_logger(__name__)

# CONSTANTS
# Custom service UUID
PIXS_SVC            = '70697865-6c73-7472-616e-64626c650000'
# Color Format Characteristic UUID
PIXS_CHR_FORMAT     = '70697865-6c73-7472-616e-64626c650001'
# Pixel Count Characteristic UUID
PIXS_CHR_COUNT      = '70697865-6c73-7472-616e-64626c650002'
# Pixel Select Characteristic UUID
PIXS_CHR_SELECT     = '70697865-6c73-7472-616e-64626c650003'
# Pixel Select Mode Characteristic UUID
PIXS_CHR_MODE       = '70697865-6c73-7472-616e-64626c650004'
# Pixel Color Characteristic UUID
PIXS_CHR_COLOR      = '70697865-6c73-7472-616e-64626c650005'
# Animation Enable Characteristic UUID
PIXS_CHR_ANIMATE    = '70697865-6c73-7472-616e-64626c650006'

class PixelStrandService:
    def __init__(self, adapter_address, num_pixels, color_format_str, local_name='PixelStrand',
                    write_color_cback=None, read_color_cback=None, write_animate_cback=None):
        """
        Initialize the PixelStrandService.
        Creates a Bluezero BLE Peripheral and adds the Pixel Strand BLE GATT Service.
        """
        logger.debug("PixelStrandService.__init__")

        # Save callback functions
        self.WriteColorCback = write_color_cback
        self.ReadColorCback = read_color_cback
        self.WriteAnimateCback = write_animate_cback
        
        # Create Bluezero GATT Peripheral
        self._server = peripheral.Peripheral(adapter_address, local_name)

        # Pixel strand service 
        self._server.add_service(srv_id=1, uuid=PIXS_SVC, primary=True)
        
        # Color Format characteristic
        self._server.add_characteristic(srv_id=1, chr_id=1, uuid=PIXS_CHR_FORMAT,
                                        notifying=False, flags=['read'],
                                        value=[ord(c) for c in color_format_str]
                                        )
        # Number of Pixels characteristic
        self._count = num_pixels        
        self._server.add_characteristic(srv_id=1, chr_id=3, uuid=PIXS_CHR_COUNT,
                                        notifying=False, flags=['read'],
                                        value = PixelStrandService.IntToByteList(num_pixels)
                                        )
        # Pixel Select characteristic 
        self._select = 0
        self._server.add_characteristic(srv_id=1, chr_id=4, uuid=PIXS_CHR_SELECT,
                                        notifying=False, flags=['read', 'write'],
                                        value = PixelStrandService.IntToByteList(self._select),
                                        read_callback=self._SelectChrReadCback,
                                        write_callback=self._SelectChrWriteCback
                                        )
        # Pixel Select Mode characteristic
        self._mode = 0
        self._server.add_characteristic(srv_id=1, chr_id=5, uuid=PIXS_CHR_MODE,
                                        notifying=False, flags=['read', 'write'],
                                        value=[self._mode],
                                        read_callback=self._ModeChrReadCback,
                                        write_callback=self._ModeChrWriteCback
                                        )
        # Pixel Color characteristic
        self._server.add_characteristic(srv_id=1, chr_id=6, uuid=PIXS_CHR_COLOR,
                                        value=[], notifying=False,
                                        flags=['read', 'write'],
                                        read_callback=self._ColorChrReadCback,
                                        write_callback=self._ColorChrWriteCback
                                        )
        # Animation Enable characteristic
        self._server.add_characteristic(srv_id=1, chr_id=7, uuid=PIXS_CHR_ANIMATE,
                                        value=[0], notifying=False,
                                        flags=['read', 'write'],
                                        write_callback=self._AnimateChrWriteCback
                                        )
        
    def Run(self):
        """
        Run the Bluezero BLE Peripheral!
        
        This is a blocking call. The server will be cleaned up (inactive) on return.
        """
        
        #Register connect/disconnect loggers
        self._server.on_connect = lambda device : (
            logger.info(f'PixelStrandService connected to {device.address}')
            )
        self._server.on_disconnect = lambda adapter_address, device_address : (
            logger.info(f'PixelStrandService disconnected from {device_address}')
            )
        
        logger.info("PixelStrandService is starting ...")
        # Go!
        self._server.publish()
        logger.info("PixelStrandService is exiting ...")
    
    def _SelectChrReadCback(self):
        logger.debug('PixelStrandService._SelectChrReadCback')
        return PixelStrandService.IntToByteList(self._select)
        
    def _SelectChrWriteCback(self, value, options):
        select = PixelStrandService.ByteListToInt(value) # select between up to ((2^32)-1) pixels!
        logger.debug(f'PixelStrandService._SelectChrWriteCback(value={select}, options={options}')
        if (select >= 0 and select <self._count): # select must be a valid index to the pixel array
            self._select = select
            
    def _ModeChrReadCback(self):
        logger.debug('PixelStrandService._ModeChrReadCback')
        return PixelStrandService.IntToByteList(self._mode, num_bytes=1)
    
    def _ModeChrWriteCback(self, value, options):
        mode = value[0] # mode is a 1-byte value
        logger.debug(f'PixelStrandService._ModeChrWriteCback(value={value}, options={options})')
        if (mode == 0 or mode == 1): # mode may only be 0 ("don't increment") or 1 ("increment")
            self._mode = mode;
    
    def _ColorChrWriteCback(self, value, options):
        logger.debug(f'PixelStrandService._ColorChrWriteCback(value={value}, options={options})')
        
        # set local color array
        self.colors[self.select] = value
        
        if(self.WriteColorCback): 
            self.WriteColorCback(value, self.select)
            
        self._select += self.mode % self.count
        
    def _ColorChrReadCback(self):
        logger.debug('PixelStrandService._ColorChrReadCback')
        if (self.ReadColorCback):
            return self.ReadColorCback(self._select)
        else:
            return 4*[0];
    
    def _AnimateChrWriteCback(self, value, options):
        logger.debug(f'PixelStrandService._AnimateChrWriteCback(value={value}, options={options}')
        if (self.animateCback):
            self.animateCback(value[0]) # animate is a 1-byte value
    
    @staticmethod 
    def IntToByteList(value, is_signed=False, num_bytes=4):
        """
        Convert an integer into a bluezero-style GATT value (a.k.a. a "bytelist")
        """
        return list(value.to_bytes(num_bytes, byteorder='little', signed=is_signed))
    
    @staticmethod
    def ByteListToInt(blist, is_signed=False):
        """
        Convert a bluezero-style GATT value into a python integer
        """
        return int.from_bytes(bytes(blist), byteorder='little', signed=is_signed)
        
class ColorList:
    def __init__(self, color_format, num_colors):
        self.format = ColorList.formatFromString(color_format)
        self.length = num_colors
        
        bitspercolor = 0
        for color in self.format:
            bitspercolor += self.format[color]
        bytespercolor = math.ceil(bitspercolor/8)
        
        self.colors = [(0).to_bytes(bytespercolor, byteorder='little') for i in range(self.length)]
            
    def __getitem__(self, index):
        return self.colors[index]
    def __setitem__(self, index, color):
        self.colors[index] = color
    
    @staticmethod
    def formatFromString(color_format):
        result = dict()
        currentColor = ''
        for char in color_format.lower():
            if char in 'rgbw': # this character represents a color
                currentColor = char
                result[char] = ''
            elif char in '0123456789': #this character represents a bit count
                result[currentColor] += char
            else:
                #invalid color string
                raise Something
        
        return {color:int(count) for (color,count) in result.items()}

if __name__ == '__main__':
    # Logging levels (see python docs for logging module)
    # logger.setLevel(logging.DEBUG) # set local logger to debug
    logging.getLogger().setLevel(logging.DEBUG) # Set all logs to debug 
    
    # Get BLE adapter address
    adapter_address = list(adapter.Adapter.available())[0].address
    
    # Create service instance and run
    pixs = PixelStrandService(adapter_address, num_pixels=10, color_format_str='R8G8B8')
    pixs.Run()

# end of pixelstrand.py

    