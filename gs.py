import sys
import locale
import ghostscript

print(sys.argv)

# todo : mettre les parametres dans le config.ini
args = [
    "ps2pdf", # actual value doesn't matter
    "-dNOPAUSE", "-dBATCH", "-dSAFER",
    "-r150",
    "-sDEVICE=tiff24nc",
    "-sCompression=pack",
    "-sOutputFile=E:/test.tiff",
    "E:/Romain/Documents/Avis_de_taxe_d_habitation_CAP_2019.pdf"
    ]

# arguments have to be bytes, encode them
#encoding = locale.getpreferredencoding()
#args = [a.encode(encoding) for a in args]

ghostscript.Ghostscript(*args)