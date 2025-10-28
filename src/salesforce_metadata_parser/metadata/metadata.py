#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import Any, Optional

# Salesforce namespace constant
SFDC_NAMESPACE = 'http://soap.sforce.com/2006/04/metadata'

# XML Schema Instance namespace constant
XSI_NAMESPACE = 'http://www.w3.org/2001/XMLSchema-instance'


@dataclass(kw_only=True)
class XmlNode():
    """Represents an XML Node"""

    _sub_classes: Optional[dict] = field(repr=False, default_factory=lambda: {})
    """Overwritable field. Tells the Parser which Class to use when creating new instances of list items"""

    def _to_dict(self) -> dict:
        return { key: value for key, value in self.__dict__ if not key.startswith("_") }


@dataclass
class XmlRoot:
    """Represents the XML Root node of the Document"""

    _namespaces: Optional[dict] = field(repr=False, default_factory=lambda: {
        'ns': SFDC_NAMESPACE,
        # 'xsi': XSI_NAMESPACE,
    })

    _xml_declaration: Optional[dict] = field(repr=False, default_factory=lambda: {
        "version": "1.0",
        "encoding": "UTF-8",
    })

    _Suffix: Optional[str] = field(repr=False, default=None)
    _Directory: Optional[str] = field(repr=False, default=None)
    _TypeName: Optional[str] = field(repr=False, default=None)


class Metadata(XmlRoot):
    # Source: https://developer.salesforce.com/docs/atlas.en-us.258.0.api_meta.meta/api_meta/metadata.htm
    """The base class for all metadata types. You can’t edit this object. A component is an instance of a metadata type.
Metadata is analogous to sObject, which represents all standard objects. Metadata represents all components and fields in the Metadata API. Instead of identifying each component with an ID, each custom object or custom field has a unique fullName, which must be distinct from standard object names, as it must be when you create custom objects or custom fields in the Salesforce user interface.

"""

    fullName: Optional[str] = field(repr=False, default=None)
    """"
    Required. The name of the component. For components with parent objects, such as fields and list views, the name must specify the name of the parent, for example Account.FirstName. The __c suffix must be appended to custom object names and custom field names when you’re setting the fullName. For example, a custom field in a custom object could have a fullName of MyCustomObject__c.MyCustomField__c.
    To reference a component in a package, prepend the package’s namespace prefix to the component name in the fullName field. Use the following syntax: namespacePrefix__ComponentName. For example, for the custom field component MyCustomObject__c.MyCustomField__c and the namespace MyNS, the full name is MyNS__MyCustomObject__c.MyCustomField__c.

    A namespace prefix is a 1-character to 15-character alphanumeric identifier that distinguishes your package and its contents from other publishers’ packages. For more information, see Create and Register Your Namespace for Second-Generation Managed Packages.
    """
