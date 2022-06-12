import xml.etree.ElementTree as ET
import xml.dom.minidom

m_encoding = 'UTF-8'

root = ET.Element("data")
doc = ET.SubElement(root, "status", date="20210123")
ET.SubElement(doc, "name", name="john").text = "some value1"
ET.SubElement(doc, "class", name="abc").text = "some vlaue2"

dom = xml.dom.minidom.parseString(ET.tostring(root))
xml_string = dom.toprettyxml()
part1, part2 = xml_string.split('?>')

with open("FILE.xml", 'w') as xfile:
    xfile.write(part1 + 'encoding=\"{}\"?>\n'.format(m_encoding) + part2)
    xfile.close()