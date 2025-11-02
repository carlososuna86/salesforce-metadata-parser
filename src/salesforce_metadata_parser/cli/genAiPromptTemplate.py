# Standard Library imports
import copy
import logging
import os
import re

# Dependency imports
import click

# Project imports
from salesforce_metadata_parser.parser.metadata_parser import XmlParser
from salesforce_metadata_parser.metadata.genaiprompttemplate import GenAiPromptTemplate

logger = logging.getLogger(__name__)

class PromptTemplateHelper:

    classes = {
        "genAiPromptTemplate": GenAiPromptTemplate
    }


    @staticmethod
    def _generate_default_prompt_template_path(api_name: str, variant: str = None):
        templates_dir = "force-app/main/default/genAiPromptTemplates"

        if variant:
            file_name = f"{api_name}-{variant}.genAiPromptTemplate-meta.xml"
        else:
            file_name = f"{api_name}.genAiPromptTemplate-meta.xml"

        return os.path.join(templates_dir, file_name)


    @staticmethod
    def _get_version_identifier(version_id: str) -> tuple:
        m = re.match(r"(?P<versionId>.*)=_(?P<versionNumber>\d+)", version_id)
        if m:
            id = m.group("versionId")
            num = int(m.group("versionNumber"))

            return id, num
        
        logging.warning(f"Unexpected versionIdentifier format: {version_id}")
        return version_id, 0


    @staticmethod
    def _increment_version_identifier(version_id: str):
        id, num = PromptTemplateHelper._get_version_identifier(version_id)

        num += 1

        return f"{id}=_{num}"

    @staticmethod
    def clone_prompt(metadata: GenAiPromptTemplate, api_suffix: str, label_suffix: str):
        # Rename based on convention
        new_metadata = copy.deepcopy(metadata)

        # Update naming
        newApiName =  f"{new_metadata.developerName}_{api_suffix}"
        newLabel = f"{new_metadata.masterLabel} {label_suffix}"
        logger.debug(f'ApiName: "{new_metadata.developerName}" -> "{newApiName}"')
        logger.debug(f'Label: "{new_metadata.masterLabel}" -> "{newLabel}"')
        new_metadata.developerName = newApiName
        new_metadata.masterLabel = newLabel

        new_metadata = PromptTemplateHelper.filter_last_version(new_metadata)

        # Strip version, it will be pulled after first deployment
        new_metadata.activeVersionIdentifier = None
        new_metadata.templateVersions[0].versionIdentifier = None

        return new_metadata

    @staticmethod
    def create_new_version(metadata: GenAiPromptTemplate) -> GenAiPromptTemplate:
        count = len(metadata.templateVersions)
        if count == 0:
            logger.warning(f"No Template Versions found")
            return

        lastVersion = metadata.templateVersions[-1]
        newVersion = copy.deepcopy(lastVersion)
        newVersion.status = GenAiPromptTemplateStatus.DRAFT
        if lastVersion.versionIdentifier:
            newVersion.versionIdentifier = PromptTemplateHelper._increment_version_identifier(lastVersion.versionIdentifier)

        logger.info(f"Creating new Version: {newVersion.versionIdentifier}")
        metadata.templateVersions.append(new_version)


    @staticmethod
    def filter_active_version(metadata: GenAiPromptTemplate) -> GenAiPromptTemplate:
        """Modifies this Prompt Template to contain only the currently action PromptTemplateVersion"""

        if metadata.activeVersionIdentifier is None:
            logger.warning(f"Prompt Template has no Active version")
            return

        activeVersion = None
        logger.debug(f"Searching version: {metadata.activeVersionIdentifier}")
        for version in metadata.templateVersions:
            logger.debug(f"VersionId: {version.versionIdentifier}")

            if version.versionIdentifier == metadata.activeVersionIdentifier:
                activeVersion = version
                break

        if activeVersion is not None:
            logger.info(f"Selecting ActiveVersionId: {activeVersion.versionIdentifier}")
            metadata.templateVersions = [ activeVersion ]
        else:
            logger.warning(f"Active version not found")

        return metadata


    @staticmethod
    def filter_last_n_versions(metadata: GenAiPromptTemplate, count: int):
        version_count = len(metadata.templateVersions)
        if version_count == 0:
            logger.warning(f"No Template Versions found")
            return
        elif version_count <= count:
            logger.info(f"Only {version_count} Template Versions found. No action taken")
            return

        lastVersions = metadata.templateVersions[ -count : ]
        logger.info(f"Selecting Last {count} Versions:")
        metadata.templateVersions = lastVersions


    @staticmethod
    def filter_last_version(metadata: GenAiPromptTemplate) -> GenAiPromptTemplate:
        # return PromptTemplateHelper.filter_last_n_versions(metadata, 1)

        count = len(metadata.templateVersions)
        if count == 0:
            logger.warning(f"No Template Versions found")
            return metadata
        elif count == 1:
            logger.info("Only one Template Version found. No action taken")
            return metadata

        lastVersion = metadata.templateVersions[-1]
        logger.info(f"Selecting Last Version: {lastVersion.versionIdentifier}")
        metadata.templateVersions = [ lastVersion ]
        metadata.activeVersionIdentifier = lastVersion.versionIdentifier

        return metadata


    @staticmethod
    def _set_status(metadata: GenAiPromptTemplate, status: str) -> GenAiPromptTemplate:
        """Set the status of the last Version"""

        metadata.templateVersions[-1].status = status

        return metadata


    @staticmethod
    def load_prompt_from_file(source_file: str) -> GenAiPromptTemplate:
        if source_file is None:
            logger.error("source file or api name not provided")
            raise ValueError()

        click.echo(f"Parsing metadata file: {source_file}")
        metadata = XmlParser.from_xml_file(source_file, classes=PromptTemplateHelper.classes)
        return metadata
    
    @staticmethod
    def load_prompt_from_api_name(api_name: str, variant: str = None) -> GenAiPromptTemplate:
        source_file = PromptTemplateHelper._generate_default_prompt_template_path(api_name, variant)

        return PromptTemplateHelper.load_prompt_from_file(source_file)

    @staticmethod
    def save_prompt_to_file(metadata: GenAiPromptTemplate, target_file: str):
        click.echo(f"Saving metadata file: {target_file}")
        XmlParser.to_xml_file(metadata, target_file)
    

    @staticmethod
    def save_prompt_to_api_name(metadata: GenAiPromptTemplate, api_name: str, variant: str = None):
        assert metadata is not None, "Metadata not provided"

        target_file = PromptTemplateHelper._generate_default_prompt_template_path(api_name, variant)
        
        XmlParser.to_xml_file(metadata, target_file)

    @staticmethod
    def save_split_prompts(metadata: GenAiPromptTemplate, api_name: str):
        for templateVersion in metadata.templateVersions:
            newMetadata = copy.deepcopy(metadata)
            newMetadata.templateVersions = [ templateVersion ]
            newMetadata.activeVersionIdentifier = templateVersion.versionIdentifier

            versionId, versionNum = PromptTemplateHelper._get_version_identifier(templateVersion.versionIdentifier)
            fakeApiName = f"{newMetadata.developerName}-v{versionNum}"
            newMetadataFileName = PromptTemplateHelper._generate_default_prompt_template_path(fakeApiName)

            PromptTemplateHelper.save_prompt_to_file(newMetadata, newMetadataFileName)


@click.group(chain=True)
@click.pass_context
def prompt_template(ctx):
    logger.debug("Group: Prompt Template")
    if ctx.obj is None:
        ctx.obj = dict()
    pass


@prompt_template.command()
@click.option('--source-file', 'source_file', type=click.Path(exists=False))
@click.option('--api-name', 'api_name', type=click.STRING)
@click.option('--variant', 'variant', type=click.STRING)
@click.pass_obj
def load_prompt(obj: dict, source_file: str = None, api_name: str = None, variant: str = None):
    """Parse a Salesforce metadata file."""

    if source_file:
        metadata = PromptTemplateHelper.load_prompt_from_file(source_file)
    else:
        metadata = PromptTemplateHelper.load_prompt_from_api_name(api_name, variant)

    assert metadata is not None
    obj["metadata"] = metadata


@prompt_template.command()
@click.pass_obj
def filter_active_version(obj: dict):
    metadata: GenAiPromptTemplate = obj["metadata"]

    metadata = PromptTemplateHelper.filter_active_version(metadata)

    assert metadata is not None
    obj["metadata"] = metadata


@prompt_template.command()
@click.pass_obj
def filter_last_version(obj: dict):
    metadata: GenAiPromptTemplate = obj["metadata"]

    metadata = PromptTemplateHelper.filter_last_version(metadata)

    assert metadata is not None
    obj["metadata"] = metadata


@prompt_template.command()
@click.option("--count", "count", type=click.INT)
@click.pass_obj
def last_n_versions(obj: dict, count: int):
    metadata: GenAiPromptTemplate = obj["metadata"]

    metadata = PromptTemplateHelper.filter_last_n_versions(metadata, count)

    assert metadata is not None
    obj["metadata"] = metadata


@prompt_template.command()
@click.pass_obj
def new_version(obj: dict):
    metadata: GenAiPromptTemplate = obj["metadata"]
    assert metadata is not None, "Metadata not provided in the context"

    PromptTemplateHelper.create_new_version(metadata)

    assert metadata is not None
    obj["metadata"] = metadata


@prompt_template.command()
@click.option("--target-file", "target_file", type=click.Path(exists=False, writable=True))
@click.option('--api-name', 'api_name', type=click.STRING)
@click.option('--variant', 'variant', type=click.STRING)
@click.pass_obj
def save_prompt(obj: dict, target_file: str = None, api_name: str = None, variant: str = None):
    """Saves the manipulated Metadata into a new file"""
    metadata: GenAiPromptTemplate = obj["metadata"]
    assert metadata is not None, "Metadata not provided in the context"

    if target_file:
        PromptTemplateHelper.save_prompt_to_file(metadata, target_file)
    else:
        PromptTemplateHelper.save_prompt_to_api_name(metadata, api_name, variant)


@prompt_template.command()
@click.pass_obj
def save_split_prompts(obj: dict):
    metadata: GenAiPromptTemplate = obj["metadata"]

    PromptTemplateHelper.save_split_prompts(metadata)


@prompt_template.command()
@click.option('--source-file', 'source_file', type=click.Path(exists=True))
@click.option("--target-file", "target_file", type=click.Path(exists=False, writable=True))
@click.pass_obj
def copy_prompt(obj: dict, source_file: str, target_file: str):
    metadata = PromptTemplateHelper.load_prompt_from_file(source_file)

    PromptTemplateHelper.save_prompt(metadata, target_file)


@prompt_template.command()
@click.option('--api-suffix', 'api_suffix', type=click.STRING)
@click.option('--label-suffix', 'label_suffix', type=click.STRING)
@click.pass_obj
def clone_prompt(obj: dict, api_suffix: str, label_suffix: str):
    metadata: GenAiPromptTemplate = obj["metadata"]

    metadata = PromptTemplateHelper.clone_prompt(metadata, api_suffix, label_suffix)

    assert metadata is not None
    obj["metadata"] = metadata


@prompt_template.command()
@click.option('--status', 'status', type=click.STRING)
@click.pass_obj
def set_status(obj: dict, status: str):
    """Set the status of the last Version"""
    metadata: GenAiPromptTemplate = obj["metadata"]

    metadata.templateVersions[-1].status = status

    assert metadata is not None
    obj["metadata"] = metadata
