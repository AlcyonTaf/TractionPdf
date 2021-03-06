import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
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

essais_eprouvettes = essais.find("./__Essai/Eprouvettes")

essais_eprouvettes.append(root_eprouvette)





# for elm in root_essais.iter():
#     print(elm.tag)



xmlpretty = minidom.parseString(ET.tostring(root_essais, encoding='ISO-8859-1').decode('ISO-8859-1')).toprettyxml()
with open('test.xml','w') as f:
    f.write(ET.tostring(root_essais, encoding='ISO-8859-1').decode('ISO-8859-1'))