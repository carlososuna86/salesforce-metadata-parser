#!/usr/bin/env python3

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .base import XmlNode
from .metadata import Metadata

# Documentation: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_genaiprompttemplate.htm

class GenAiPromptTemplateStatus(Enum):
    PUBLISHED = "Published"
    """Published version of a prompt template. The active version of the prompt template must be published."""

    DRAFT = "Draft"
    """Draft version of a prompt template."""


class GenAiPromptTemplateType(Enum):
    """
    Required. Represents the template type that the prompt template is based on. Valid values are:
        einstein_gpt__fieldCompletion
        einstein_gpt__salesEmail
        einstein_gpt__recordSummary
        einstein_gpt__flex
        einstein_gpt__caseEmailDraft
    """
    FIELD_COMPLETION = "einstein_gpt__fieldCompletion"
    SALES_EMAIL = "einstein_gpt__salesEmail"
    RECORD_SUMMARY = "einstein_gpt__recordSummary"
    FLEX = "einstein_gpt__flex"
    CASE_EMAIL_DRAFT = "einstein_gpt__caseEmailDraft"


class GenAiPromptTemplateVisibilityType(Enum):
    """
    Indicates the scope of visibility for the prompt template. Valid values are:
        API
        Global
    """
    API = 'API'
    GLOBAL = 'Global'


@dataclass
class GenAiPromptTemplateDataProviderParam(XmlNode):
    # Documentation: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_genaiprompttemplate.htm#genaiprompttemplatedataproviderparam

    definition: Optional[str] = None
    """Required. URI definition of the parameter. For example,  SOBJECT://User</definition>."""

    isRequired: Optional[bool] = None
    """Required. Specifies whether the parameter is required (true) or optional (false)."""

    parameterName: Optional[str] = None
    """Required. Name of the parameter."""

    valueExpression: Optional[str] = None
    """Value or expression of the parameter to use in prompt template text. For example, {!$Input:Recipient}."""


@dataclass
class GenAiPromptTemplateDataProvider(XmlNode):
    # Documentation: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_genaiprompttemplate.htm#genaiprompttemplatedataprovider

    definition: Optional[str] = None
    """Required. The URI definition of the data provider, such as flow://ns__CallToActionFlow."""

    parameters: List[GenAiPromptTemplateDataProviderParam] = field(default_factory=list)
    """An array of parameters associated with the data provider."""

    referenceName: Optional[str] = None
    """Required. Name of the data provider to use in expressions."""

    sub_classes: Optional[dict] = field(repr=False, default=lambda: {
        "parameters": GenAiPromptTemplateDataProviderParam
    })

@dataclass
class GenAiPromptTemplateInput(XmlNode):
    # Documentation: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_genaiprompttemplate.htm#genaiprompttemplateinput

    apiName: Optional[str] = None
    """Required. Name of the prompt template input parameter."""

    definition: Optional[str] = None
    """Required. The URI definition of the input parameter. For example, SOBJECT://Account and SOBJECT://Account/Description."""

    description: Optional[str] = None
    """Description of the prompt template input parameter."""

    masterLabel: Optional[str] = None
    """A user-friendly name for GenAiPromptTemplateInput, which is defined when the GenAiPromptTemplateInput is created."""

    referenceName: Optional[str] = None
    """Required. Name of the prompt template input to use in expressions. For example, Input:Recipient and Input:Sender</referenceName>."""

    required: Optional[bool] = None
    """Required. Specifies whether this input parameter is required (True) or optional (False)."""


@dataclass
class GenAiGenerationTemplateConfig(XmlNode):
    """Undocumented class"""

    generationConfigDeveloperName: Optional[str] = None


@dataclass
class GenAiPromptTemplateVersion(XmlNode):
    # Documentation: https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_genaiprompttemplate.htm#genaiprompttemplateversion

    content: Optional[str] = None
    """Required. Text of the prompt template version."""

    description: Optional[str] = None
    """Description of the prompt template version."""

    generationTemplateConfigs: List = field(default_factory=list)
    """Undocumented"""

    inputs: List[GenAiPromptTemplateInput] = field(default_factory=list)
    """An array of prompt template inputs associated with the prompt template version."""

    primaryModel: Optional[str] = None
    """The model associated with the prompt template version."""

    status: Optional[GenAiPromptTemplateStatus] = None
    """
    Required. Indicates the status of the prompt template in Prompt Builder. Valid values are:
        
        Published—Published version of a prompt template. The active version of the prompt template must be published.
            Published prompt templates can't be edited with UI or Metadata API.
        
        Draft—Draft version of a prompt template.
    """

    templateDataProviders: List[GenAiPromptTemplateDataProvider] = field(default_factory=list)
    """An array of data providers associated with the prompt template version."""

    # versionNumber: int
    # """
    # Required. Version number of the prompt template version. Versions are counted sequentially from 1.
    # This tag will be deprecated in 63.0 and will not work in 64.0 and later. Use versionIdentifier instead.
    # """

    versionIdentifier: Optional[str] = None
    """Required. Identifier for the version."""

    sub_classes: Optional[dict] = field(repr=False, default=lambda: {
        "generationTemplateConfigs": GenAiGenerationTemplateConfig,
        "inputs": GenAiPromptTemplateInput,
        "status": GenAiPromptTemplateStatus,
        "templateDataProviders": GenAiPromptTemplateDataProvider,
    })

    tag_name: Optional[str] = field(repr=False, default="templateVersions")


@dataclass
class GenAiPromptTemplate(Metadata):

    # activeVersion: int
    # """This tag will be deprecated in 63.0 and will not work in 64.0 and later. Use activeVersionIdentifier instead."""

    activeVersionIdentifier: Optional[str] = None
    """Specifies the version identifier of the active prompt template version. This tag will use versionIdentifier as the value for the active version."""

    description: Optional[str] = None
    """A description of the prompt template."""

    developerName: Optional[str] = None
    """Developer name of the prompt template, derived from the XML filename."""

    masterLabel: Optional[str] = None
    """Required. A user-friendly name for GenAiPromptTemplate, which is defined when the GenAiPromptTemplate is created."""

    overrideSource: Optional[str] = None
    """Undocumented"""

    relatedEntity: Optional[str] = None
    """The Salesforce record type that the prompt template is associated with."""

    relatedField: Optional[str] = None
    """The Salesforce field that the prompt template is associated with."""

    templateVersions: List[GenAiPromptTemplateVersion] = field(default_factory=list)
    """Required. An array of prompt template versions."""

    type: Optional[GenAiPromptTemplateType] = None
    """
    Required. Represents the template type that the prompt template is based on. Valid values are:
        einstein_gpt__fieldCompletion
        einstein_gpt__salesEmail
        einstein_gpt__recordSummary
        einstein_gpt__flex
        einstein_gpt__caseEmailDraft
    """

    visibility: Optional[GenAiPromptTemplateVisibilityType] = None
    """
    Indicates the scope of visibility for the prompt template. Valid values are:
        API
        Global
    """

    _Suffix: Optional[str] = field(repr=False, default=".genAiPromptTemplate")
    _Directory: Optional[str] = field(repr=False, default="genAiPromptTemplates")
    _TypeName: Optional[str] = field(repr=False, default="GenAiPromptTemplate")

    sub_classes: Optional[dict] = field(repr=False, default=lambda: {
        "templateVersions": GenAiPromptTemplateVersion,
        "type": GenAiPromptTemplateType,
        "visibility": GenAiPromptTemplateVisibilityType,
    })
