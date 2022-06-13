from lxml import etree as ET
import os
from datetime import datetime


#test date

print(datetime.now().strftime('%Y%m%d%H%M%S%f'))

xml_encoding = 'ISO-8859-1'

script_path = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

path_to_xml_essais = os.path.join(script_path, 'Xml Template', 'xml_template_essais.xml')
path_to_xml_eprouvette = os.path.join(script_path, 'Xml Template', 'xml_template_eprouvette.xml')
path_to_xml_parametre = os.path.join(script_path, 'Xml Template', 'xml_template_parametre.xml')
# récupération des templates
# Essais
root_essais = ET.parse(path_to_xml_essais).getroot()
# Eprouvette
root_eprouvette = ET.parse(path_to_xml_eprouvette).getroot()
# Parametre
root_parametre = ET.parse(path_to_xml_parametre).getroot()


# Dans un premier temps on remplie la partie parametre
root_parametre.find("./NumPara").text = "NumPara"
root_parametre.find("./ValuePara").text = "ValuePara"
root_parametre.find("./ValueParaT").text = "ValueParaT"
root_parametre.find("./SequenceResult").text = "SequenceResult"
root_parametre.find("./SequenceEssEpr").text = "SequenceEssEpr"

# insert para dans eprouvette
root_eprouvette.find("./Parametres").insert(0, root_parametre)
#eprouvette_para.insert(0, root_parametre)

#On complete eprouvette
root_eprouvette.find("./SeqEssais").text = "SeqEssais"

# insert eprouvette dans essais
root_essais.find("./__Essai/Eprouvettes").insert(0, root_eprouvette)

#On complete essais
root_essais.find("./__Essai/Source").text = "Source"
root_essais.find("./__Essai/TimeStamp").text = "TimeStamp"
root_essais.find("./__Essai/NoCommande").text = "NoCommande"
root_essais.find("./__Essai/NoPoste").text = "NoPoste"
root_essais.find("./__Essai/Batch").text = "Batch"
root_essais.find("./__Essai/SequenceLoc").text = "SequenceLoc"

ET.indent(root_essais)
ET.ElementTree(root_essais).write('test.xml', pretty_print=True, encoding=xml_encoding)


