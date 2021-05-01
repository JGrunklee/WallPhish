"""
pixelstrand.py

Implement a custom Pixel Strand BLE Service using python-bluezero 
https://github.com/ukBaz/python-bluezero

rsync -r . pi@raspberrypi:~/Documents/WallPhish

"""

from bluezero import adapter
from bluezero import peripheral

# CONSTANTS
# Custom service UUID
PIXS_SVC        = '70697865-6c73-7472-616e-64626c650000'
# Pixel Style Characteristic UUID
PIXS_CHR_STYLE  = '70697865-6c73-7472-616e-64626c650001'
# Color Resolution Characteristic UUID
PIXS_CHR_RES    = '70697865-6c73-7472-616e-64626c650002'
# Pixel Count Characteristic UUID
PIXS_CHR_COUNT  = '70697865-6c73-7472-616e-64626c650003'
# Pixel Select Characteristic UUID
PIXS_CHR_SELECT = '70697865-6c73-7472-616e-64626c650004'
# Pixel Select Mode Characteristic UUID
PIXS_CHR_MODE   = '70697865-6c73-7472-616e-64626c650005'
# Pixel Color Characteristic UUID
PIXS_CHR_COLOR  = '70697865-6c73-7472-616e-64626c650006'
# Animation Enable Characteristic UUID
PIXS_CHR_ANIMATE = '70697865-6c73-7472-616e-64626c650007'

#class PixelStrand:

def main(adapter_address):
    strand = peripheral.Peripheral(adapter_address, local_name='Fishy')
    
    # Pixel strand service 
    strand.add_service(srv_id=1, uuid=PIXS_SVC, primary=True)
    
    # Style characteristic 
    strand.add_characteristic(srv_id=1, chr_id=1, uuid=PIXS_CHR_STYLE,
                                value=[], notifying=False,
                                flags=['read'])
    # Resolution characteristic                             
    strand.add_characteristic(srv_id=1, chr_id=2, uuid=PIXS_CHR_RES,
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
    strand.add_characteristic(srv_id=1, chr_id=6, uuid=PIXS_CHR_SELECT,
                                value=[], notifying=False,
                                flags=['read', 'write'],
                                read_callback=None,
                                write_callback=None)
    # Animation Enable characteristic
    strand.add_characteristic(srv_id=1, chr_id=7, uuid=PIXS_CHR_SELECT,
                                value=[], notifying=False,
                                flags=['read', 'write'],
                                write_callback=None)
    # Let's go!
    strand.publish()



if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)