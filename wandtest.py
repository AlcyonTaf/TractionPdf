# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os

# convert.exe  .\temp.tiff -compress rle -type palette -define tiff:rows-per-strip=4 -density 150  .\Testcomandline.tif
#os.environ['MAGICK_HOME'] = 'E:\Logiciel\TestDll'
magick_home = ".\\ImageMagickDLL\\"
gs_path = ".\\gs9.56.1\\bin\\"
print( os.pathsep + magick_home + os.sep)
os.environ["PATH"] += os.pathsep + magick_home + os.sep
os.environ["PATH"] += os.pathsep + gs_path + os.sep
os.environ["MAGICK_HOME"] = magick_home
os.environ["MAGICK_CODER_MODULE_PATH"] = magick_home + os.sep + "modules" + os.sep + "coders"
from wand.image import Image
from wand.color import Color



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ny = Image(filename='test.pdf', resolution=200)
    ny.format = 'tiff'
    ny.options['tiff:rows-per-strip'] = '4' # important
    ny.background_color = Color("white")
    ny.alpha_channel = 'remove'
    ny.type = 'palette'
    ny.compression = 'rle'
    ny.resolution = [150,150] # doit etre 150 pour annexe apparement

    print(ny.type)
    ny.save(filename='Z6681-Z6682.tif')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
