# Pixel Strand BLE GATT Service
This document defines a BLE GATT service for identifying and controlling a 
strand of RGB/RGBW LED pixels (such as NeoPixels!). This service supports 
editing individual pixels as well as quickly editing ranges (see Pixel Select 
Mode). It also supports enabling/disabling custom animations.

## Characteristic Descriptions
Here is a list of all the BLE characteristics included in the Pixel Strand
service. 

1. __Color Format__ (Read only)
    * ASCII-encoded value that gives the number of individual LEDs within each
        pixel, their order, and the number of bits expected for each.
    * Each LED is represented as a letter ('R', 'G', 'B', or 'W') followed by an integer 
    * Letters may be either upper or lower case. Only alphanumeric characters are allowed.
    * Typical example value: `'R8G8B8'`. This would mean each pixel requires 24 bits
        to specify a color: 8 bits for red, 8 for green, and 8 for blue, in that order.
1. __Number of Pixels__ (Read only)
    * Gives number of pixels in the strand.
1. __Pixel Select__ (Read/Write)
    * Index of the currently selected pixel. Indices start at 0.
    * Select a pixel by writing that pixel's index to this characteristic.
1. __Pixel Select Mode__ (Read/Write)
    * `0x01` = Automatically increment Pixel Select after every write to the
        Pixel Color characteristic, wrapping around at the end of the strip.
    * `0x00` = Writing the Pixel Color characteristic has no effect on the Pixel Select
        characteristic.
    * Other values are undefined.
1. __Pixel Color__ (Read/Write)
    * Read this characteristic to get the color of the currently selected pixel.
    * Write this characteristic to set the color of the currenly selected pixel.
    * Color format should conform to the given Pixel Style and Color Resolution.
1. __Animation Enable__ (Read/Write)
    * `0x00` = None. Animations are disabled.
    * `0x01` = Enable custom animation 1
    * `0x02` = Enable custom animation 2
    * etc. 
    
## Attribute Table
This table gives a more detailed (ATT-level) view of the Pixel Strand service. 
It defines the service and characteristic UUIDs and their properties.

TBD
