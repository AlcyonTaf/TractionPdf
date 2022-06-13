from lxml import etree as ET
import os

m_encoding = 'ISO-8859-1'

script_path = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

print(script_path)
path_to_xml_essais = os.path.join(script_path, 'Xml Template', 'xml_template_essais.xml')
path_to_xml_eprouvette = os.path.join(script_path, 'Xml Template', 'xml_template_eprouvette.xml')
path_to_xml_parametre = os.path.join(script_path, 'Xml Template', 'xml_template_parametre.xml')
# récupération des templates
# Essais
essais = ET.parse(path_to_xml_essais)
root_essais = essais.getroot()
# Eprouvette
eprouvette = ET.parse(path_to_xml_eprouvette)
root_eprouvette = eprouvette.getroot()
# Parametre
parametre = ET.parse(path_to_xml_parametre)
root_parametre = parametre.getroot()

#for element in root_essais.iter():
#    print(element)

Numpara = root_parametre.find("./NumPara")
Numpara.text = "test"



eprouvette_para = root_eprouvette.find("./Parametres")
eprouvette_para.insert(0, root_parametre)

essais_eprouvette = root_essais.find("./__Essai/Eprouvettes")
essais_eprouvette.insert(0, root_eprouvette)

ET.indent(root_essais)
ET.ElementTree(root_essais).write('test.xml', pretty_print=True, encoding='ISO-8859-1')


