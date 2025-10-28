#!/usr/bin/env python3

# from dataclasses import dataclass
import dataclasses
import json
import importlib
import logging
import os
import re
import typing
from typing import Any
import xml.dom.minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import xml.sax.saxutils


# import xmltodict
from ..metadata.metadata import XmlNode, XmlRoot, Metadata

logger = logging.getLogger(__name__)

xml_entities = {
    '\"': "&quot;",
    "\'": "&apos;",
    "\xA0": " ",
}

patterns = {
    "tagPattern": re.compile(r"(P?<namespace>\{.*\})?(?P<tag>[a-z_]+)"),
    # "listPattern": re.compile(r"typing\.List\[(?P<type>(?P<module>[A-Za-z]+\.)*(?P<class>[A-Za-z]+))\]"),
    "entityDoublePatterm": re.compile(r"&amp;(?P<entity>[a-z]+);"),
}


class XmlParser:

    @staticmethod
    def _getListItemTagName(metadata: Any) -> str:
        if not dataclasses.is_dataclass(metadata):
            logger.warning(f"This is not a dataclass: {type(metadata)} {metadata}")
            return None

        return f"{metadata.__class__.__name__}s"


    @staticmethod
    def _escapeXmlEntities(xml_content: str, entities: dict) -> str:
        return xml.sax.saxutils.escape(xml_content, entities)


    @staticmethod
    def _unescape_double_entities(xml_content: str) -> str:
        return patterns["entityDoublePatterm"].sub(lambda m: f"&{m.group("entity")};", xml_content)


    @staticmethod
    def _get_visible_dict(metadata: XmlNode) -> dict:
        return { key: value for key, value in metadata.__dict__.items() if not key[0] == "_" }


    @staticmethod
    def _get_invisible_dict(metadata: XmlNode) -> dict:
        return { key: value for key, value in metadata.__dict__.items() if key[0] == "_" }

    @staticmethod
    def _getListSubclass(metadata, field_name: str) -> Any:
        if not dataclasses.is_dataclass(metadata):
            logger.error(f"Unexpected Type: {type(metadata)}")
            return None

        # Extract the Class associated with the tag name
        sub_classes = metadata.__dict__.get("_sub_classes", {})
        logger.debug(f"sub_classes: {sub_classes}")
        cls2 = sub_classes.get(field_name, None)
        if not cls2:
            logger.debug(f"No dataclass found for: {field_name}")
            
        return cls2


    @staticmethod
    def _getTagName(element: Element) -> str:
        if not isinstance(element, Element):
            logger.error(f"Unexpected Type: {type(element)}")
            return None

        m = patterns["tagPattern"].match(element.tag)
        if m:
            tag = m.group("tag")
            # logger.debug(f"Match: {tag}")
        elif "}" in element.tag:
            _, _, tag = element.tag.rpartition("}")
            # logger.debug(f"rpartition: {tag}")

        if tag:
            return tag
        else:
            return element.tag


    @staticmethod
    def _parse_xml(parent: Element, metadata: XmlNode):
        parent_tag = XmlParser._getTagName(parent)

        if not dataclasses.is_dataclass(metadata):
            logger.error(f"Unexpected Type: {type(metadata)}")
            return None

        namespaces = metadata.__dict__.get("namespaces", None)

        for child in parent.findall("./", namespaces=namespaces):
            child_tag = XmlParser._getTagName(child)
            logger.debug(f'tagName: {parent_tag}.{child_tag}')
            if child.text and not child.text.isspace():
                if len(child.text) > 40:
                    logger.debug(f'text: "{child.text[ : 40]}..."')
                else:
                    logger.debug(f'text: = "{child.text}"')
                metadata.__dict__[child_tag] = child.text
                continue

            # Instantiate a sub-node
            cls2 = XmlParser._getListSubclass(metadata, child_tag)
            if cls2:
                logger.debug(f"sub_class: {type(cls2)} = {cls2.__name__}")
                metadata2 = cls2()
            else:
                metadata2 = XmlNode()

            if child_tag not in metadata.__dict__.keys():
                metadata.__dict__[child_tag] = list()

            metadata.__dict__[child_tag].append(metadata2)
            XmlParser._parse_xml(child, metadata2)


    def _unparse_xml(parent_element: Element, key: str, value: Any):
        logger.debug(f"Parent: {type(parent_element)} = {parent_element.tag}")
        logger.debug(f"key: {type(key)} = {key}")
        logger.debug(f"value: {type(value)} = {value}")

        if value is None:
            logger.debug(f"Value not set for {key}")
            return

        if isinstance(value, str) and not value.isspace():
            element = ET.SubElement(parent_element, key)
            element.text = XmlParser._escapeXmlEntities(value, xml_entities)
            logger.debug(f"Adding text node {parent_element.tag}.{key}")
            return

        if isinstance(value, XmlNode):
            logger.debug(f"{type(value)} = {value.__dict__}")
            element = ET.SubElement(parent_element, key)
            logger.debug(f"Adding object node {parent_element.tag}.{element.tag}")

            node_dict = XmlParser._get_visible_dict(value)
            for field_name, field in node_dict.items():
                logger.debug(f"fields[{field_name}] = {field}")
                key2 = field_name
                value2 = value.__dict__[key2]
                XmlParser._unparse_xml(element, key2, value2)

            return

        if isinstance(value, list):
            for item in value:
                XmlParser._unparse_xml(parent_element, key, item)

            return
        
        logger.error(f"Unexpected type {type(value)}: [{key}] = {value}")

    @staticmethod
    def _encode_string(pretty_string: bytes, xml_declaration: dict = {}):
        logger.debug(f"Converting from Bytes to UTF-8 String")
        if xml_declaration.get("encoding", None):
            return str(pretty_string, encoding=xml_declaration["encoding"])
        return str(pretty_string, encoding="utf-8")


    @staticmethod
    def _to_pretty_string(root: ET.Element, xml_declaration: dict = {}, indent: str = "    ") -> str:
        logger.debug(f"root: {root.tag}")

        rough_string = ET.tostring(
            element=root,
            encoding="unicode",
            method="xml",
            xml_declaration=True,
            # default_namespace=root.namespace,
            short_empty_elements=True,
            # pretty_print=True
        )
    
        # Pretty print the XML
        logger.debug(f"begin: {rough_string[ : 200]}")
        logger.debug(f"end: {rough_string[-200 : ]}")
        reparsed = xml.dom.minidom.parseString(rough_string)

        pretty_string = reparsed.toprettyxml(
            indent=indent,
            encoding=xml_declaration.get("encoding", None),
            standalone=xml_declaration.get("standalone", None)
        )

        if isinstance(pretty_string, bytes):
            pretty_string = XmlParser._encode_string(pretty_string, xml_declaration)

        pretty_string = XmlParser._unescape_double_entities(pretty_string)
        logger.debug(f"begin: {pretty_string[ : 200]}")
        logger.debug(f"end: {pretty_string[-200 : ]}")

        return pretty_string

    @staticmethod
    def from_xml_string(xml_string: str, classes: dict = {}) -> Metadata:
        # Parse the XML string

        root: Element = ET.fromstring(xml_string)
        logger.debug(f"root: {root.tag}")

        tag = XmlParser._getTagName(root)
        cls = classes.get(tag, Metadata)
        logger.debug(f"Metadata type: {cls.__name__}")
        if cls:
            metadata = cls()
        else:
            metadata = Metadata()

        metadata._TypeName = tag

        XmlParser._parse_xml(root, metadata)

        # logger.debug(json.dumps(metadata.__repr__(), indent=2))            
        
        return metadata


    @staticmethod
    def from_xml_file(xml_file_path, classes: dict = {}) -> Metadata:
        with open(xml_file_path, "r", encoding="utf-8") as xml_file:
            logger.info(f"Reading Metadata from: {xml_file_path}")
            content = xml_file.read()

        metadata = XmlParser.from_xml_string(content, classes)

        xml_dir_path, xml_file_name = os.path.split(xml_file_path)

        if metadata._Directory is None:
            metadata._Directory =  xml_dir_path

        if metadata._Suffix is None:
            m = re.match(r".*\.(?P<suffix>.*)-meta\.xml", xml_file_name)
            if m:
                metadata._Suffix = m.group("suffix")

        return metadata


    @staticmethod
    def to_xml_string(metadata: Metadata) -> str:

        # Create the root Node
        private_dict = XmlParser._get_invisible_dict(metadata)
        logger.debug(f"Private: {json.dumps(private_dict, indent=2)}")
        root = ET.Element(metadata._TypeName)

        ns = metadata._namespaces.get("ns", None)
        if ns:
            root.set('xmlns', ns)
        
        node_dict = XmlParser._get_visible_dict(metadata)
        for key, value in node_dict.items():            
            XmlParser._unparse_xml(root, key, value)

        return XmlParser._to_pretty_string(root, metadata._xml_declaration, "    ")


    @staticmethod
    def to_xml_file(metadata: Metadata, xml_file_name: str) -> None:
        content = XmlParser.to_xml_string(metadata)
        assert isinstance(content, str), f"Wrong type for content: {type(content)}"
        assert xml_file_name is not None, f"xml_file_name is NULL"

        with open(xml_file_name, "w", encoding="utf-8") as xml_file:
            logger.info(f"Writing Metadata to: {xml_file_name}")
            xml_file.write(content)
