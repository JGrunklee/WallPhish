"""
pixelstrand.py

Implement a custom Pixel Strand BLE Service using python-bluezero 
https://github.com/ukBaz/python-bluezero

rsync -r . pi@raspberrypi:~/Documents/WallPhish

"""

import math

from bluezero import adapter
from bluezero import peripheral

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

class PixelStrand:
    def __init__(self, color_format, num_pixels, color_callback=None, animate_callback = None):
        self.colorCallback = color_callback
        self.animateCallback = animate_callback
        
        self.colors = ColorList(color_format, num_pixels)
        
        #################################
        # Create Bluezero GATT Peripheral
        #################################
        self.server = peripheral.Peripheral(adapter_address, local_name='Fishy')
        
        # Pixel strand service 
        self.server.add_service(srv_id=1, uuid=PIXS_SVC, primary=True)
        
        # Color Format characteristic
        self.server.add_characteristic(srv_id=1, chr_id=1, uuid=PIXS_CHR_FORMAT,
                                        notifying=False, flags=['read'],
                                        value=[ord(c) for c in color_format]
                                        )
        # Number of Pixels characteristic
        self.count = num_pixels        
        self.server.add_characteristic(srv_id=1, chr_id=3, uuid=PIXS_CHR_COUNT,
                                        notifying=False, flags=['read'],
                                        value = PixelStrand.IntToByteList(num_pixels)
                                        )
        # Pixel Select characteristic 
        self.select = 0
        self.server.add_characteristic(srv_id=1, chr_id=4, uuid=PIXS_CHR_SELECT,
                                        notifying=False, flags=['read', 'write'],
                                        value = PixelStrand.IntToByteList(self.select),
                                        write_callback=self._SelectChrWriteCallback)
        # Pixel Select Mode characteristic
        self.mode = 0
        self.server.add_characteristic(srv_id=1, chr_id=5, uuid=PIXS_CHR_MODE,
                                        notifying=False, flags=['read', 'write'],
                                        value = PixelStrand.IntToByteList(self.mode),
                                        write_callback=self._ModeChrWriteCallback)
        # Pixel Color characteristic
        self.server.add_characteristic(srv_id=1, chr_id=6, uuid=PIXS_CHR_COLOR,
                                        value=[], notifying=False,
                                        flags=['read', 'write'],
                                        read_callback=None,
                                        write_callback=self._ColorChrWriteCallback)
        # Animation Enable characteristic
        self.server.add_characteristic(srv_id=1, chr_id=7, uuid=PIXS_CHR_ANIMATE,
                                        value=[], notifying=False,
                                        flags=['read', 'write'],
                                        write_callback=self._AnimateChrWriteCallback)
        # Let's go!
        self.server.publish()
    
    def _SelectChrWriteCallback(value, options):
        # todo validate
        self.select = value;
    
    def _ModeChrWriteCallback(value, options):
        # todo validate
        self.mode = value;
    
    def _ColorChrWriteCallback(value, options):
        # set local color array
        self.colors[self.select] = value
        
        if(self.color_callback): 
            self.color_callback(value, self.select)
            
        self.select += self.mode % self.count
    
    def _AnimateChrWriteCallback(value, options):
        if (self.animate_callback):
            self.animateCallback(value)
    
    @staticmethod 
    def IntToByteList(value, is_signed=False, num_bytes=4):
        return list(value.to_bytes(num_bytes, byteorder='little', signed=is_signed))
        
class ColorList:
    def __init__(self, color_format, num_colors):
        self.format = formatFromString(color_format)
        self.length = num_colors
        
        bitspercolor = 0
        for color in self.format:
            bitspercolor += self.format[color]
        bytespercolor = math.ceil(bitspercolor/8)
        
        self.colors = [(0).to_bytes(bytespercolor) for i in range(self.length)]
            
    def __getitem__(self, index):
        return self.colors[index]
    def __setitem__(self, index, color):
        self.colors[index] = color
    
    @staticmethod
    def formatFromString(color_format);
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

def main(adapter_address):
    strand = peripheral.Peripheral(adapter_address, local_name='Fishy')
    
    # Pixel strand service 
    strand.add_service(srv_id=1, uuid=PIXS_SVC, primary=True)
    
    # Color Format characteristic 
    strand.add_characteristic(srv_id=1, chr_id=1, uuid=PIXS_CHR_FORMAT,
                                value=[], notifying=False,
                                flags=['read'])
    # Pixel Count characteristic                             
    strand.add_characteristic(srv_id=1, chr_id=3, uuid=PIXS_CHR_COUNT,
                                value=[], notifying=False,
                                flags=['read'])
    # Select characteristic 
    strand.add_characteristic(srv_id=1, chr_id=4, uuid=PIXS_CHR_SELECT,
                                value=[], notifying=False,
                                flags=['read', 'write'],
                                write_callback=None)
    # Select Mode characteristic
    strand.add_characteristic(srv_id=1, chr_id=5, uuid=PIXS_CHR_MODE,
                                value=[], notifying=False,
                                flags=['read', 'write'],
                                write_callback=None)
    # Color characteristic
    strand.add_characteristic(srv_id=1, chr_id=6, uuid=PIXS_CHR_COLOR,
                                value=[], notifying=False,
                                flags=['read', 'write'],
                                read_callback=None,
                                write_callback=None)
    # Animation Enable characteristic
    strand.add_characteristic(srv_id=1, chr_id=7, uuid=PIXS_CHR_ANIMATE,
                                value=[], notifying=False,
                                flags=['read', 'write'],
                                write_callback=None)
    # Let's go!
    strand.publish()



if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
    