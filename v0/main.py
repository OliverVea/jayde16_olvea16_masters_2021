from wfs import WMTS
from utility import prints
from get_gps import GPSConnection

from PIL import Image

wmts = WMTS('https://services.datafordeler.dk/GeoDanmarkOrto/orto_foraar_wmts/1.0.0/WMTS?',
    username='VCSWRCSUKZ',
    password='hrN9aTirUg5c!np',
    layer='orto_foraar_wmts',
    tile_matrix_set='KortforsyningTilingDK')

conn = GPSConnection(address='10.147.18.175', port=7789)
coords = conn.get_coords()

wmts.get_map(style='default', tile_matrix=12, center=coords)



## MAKE THIS INTO FUNCTION

'''
for tile_matrix in range(2)[:1]:
    tile_matrix = 2
    n, m = [(2, 3), (3, 5), (6, 9), (12, 17), (23, 34), (46, 68), (92, 135)][tile_matrix]

    img = Image.new('RGB', (n * 256, m * 256))
    prints('start')
    for i in range(n):
        for j in range(m):
            img.paste(im, (256 * j, 256 * i))
    prints('stop')

    img.save(f'map_{tile_matrix}.png')
    img.show()
'''