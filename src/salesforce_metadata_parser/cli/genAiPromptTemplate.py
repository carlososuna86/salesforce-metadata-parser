# Standard Library imports
import copy
import logging
import re

# Dependency imports
import click

# Project imports
from salesforce_metadata_parser.parser.metadata_parser import XmlParser
from salesforce_metadata_parser.metadata.genaiprompttemplate import GenAiPromptTemplate

logger = logging.getLogger(__name__)

classes = {
    "genAiPromptTemplate": GenAiPromptTemplate
}


def _generate_default_prompt_template_path(api_name: str):
    return f"force-app/main/default/genAiPromptTemplates/{api_name}.genAiPromptTemplate-meta.xml"


def _increment_version_identifier(version_id: str):
    m = re.match(r"(?P<versionId>.*)=_(?P<versionNumber>\d+)", version_id)
    if m:
        id = m.group("versionId")
        num = int(m.group("versionNumber")) + 1
        return f"{id}=_{num}"
    
    logging.warning(f"Unexpected versionIdentifier format: {version_id}")
    return version_id


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
@click.pass_obj
def load_prompt(obj: dict, source_file: str, api_name: str):
    """Parse a Salesforce metadata file."""

    if source_file is None:
        if not api_name is None:
            source_file = _generate_default_prompt_template_path(api_name)

    if source_file is None:
        logger.error("source file or api name not provided")
        raise ValueError()

    click.echo(f"Parsing metadata file: {source_file}")
    metadata = XmlParser.from_xml_file(source_file, classes=classes)
    obj["metadata"] = metadata


@prompt_template.command()
@click.pass_obj
def active_version(obj: dict):
    metadata: GenAiPromptTemplate = obj["metadata"]

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

    obj["metadata"] = metadata


@prompt_template.command()
@click.pass_obj
def last_version(obj: dict):
    metadata: GenAiPromptTemplate = obj["metadata"]

    count = len(metadata.templateVersions)
    if count == 0:
        logger.warning(f"No Template Versions found")
        return
    elif count == 1:
        logger.info("Only one Template Version found. No action taken")
        return

    lastVersion = metadata.templateVersions[-1]
    logger.info(f"Selecting Last Version: {lastVersion.versionIdentifier}")
    metadata.templateVersions = [ lastVersion ]
    metadata.activeVersionIdentifier = lastVersion.versionIdentifier

    obj["metadata"] = metadata


@prompt_template.command()
@click.pass_obj
def new_version(obj: dict):
    metadata: GenAiPromptTemplate = obj["metadata"]

    count = len(metadata.templateVersions)
    if count == 0:
        logger.warning(f"No Template Versions found")
        return

    lastVersion = metadata.templateVersions[-1]
    newVersion = copy.deepcopy(lastVersion)
    newVersion.status = "Draft"
    if lastVersion.versionIdentifier:
        newVersion.versionIdentifier = _increment_version_identifier(lastVersion.versionIdentifier)

    logger.info(f"Creating new Version: {newVersion.versionIdentifier}")
    metadata.templateVersions.append(new_version)
    

    obj["metadata"] = metadata


@prompt_template.command()
@click.option("--target-file", "target_file", type=click.Path(exists=False, writable=True))
@click.pass_obj
def save_prompt(obj: dict, target_file: str):
    """Saves the manipulated Metadata into a new file"""

    logger.debug(f"obj: {obj}")
    logger.debug(f"target_file: {target_file}")

    click.echo(f"Saving metadata file: {target_file}")
    XmlParser.to_xml_file(obj["metadata"], target_file)


@prompt_template.command()
@click.option('--source-file', 'source_file', type=click.Path(exists=True))
@click.option("--target-file", "target_file", type=click.Path(exists=False, writable=True))
@click.pass_obj
def copy_prompt(obj: dict, source_file: str, target_file: str):

    logger.debug(f"obj: {obj}")
    logger.debug(f"source_file: {target_file}")
    logger.debug(f"target_file: {target_file}")

    load_prompt(obj, source_file)
    save_prompt(obj, target_file)


@prompt_template.command()
@click.option('--api-suffix', 'api_suffix', type=click.STRING)
@click.option('--label-suffix', 'label_suffix', type=click.STRING)
@click.pass_obj
def clone_prompt(obj: dict, api_suffix: str, label_suffix: str):
    metadata: GenAiPromptTemplate = obj["metadata"]

    # Remove the overrideSource
    metadata.overrideSource = None

    # Rename based on convention
    newApiName =  f"{metadata.developerName}_{api_suffix}"
    newLabel = f"{metadata.masterLabel} {label_suffix}"
    logger.debug(f'ApiName: "{metadata.developerName}" -> "{newApiName}"')
    logger.debug(f'Label: "{metadata.masterLabel}" -> "{newLabel}"')
    metadata.developerName = newApiName
    metadata.masterLabel = newLabel

    obj["metadata"] = metadata


@prompt_template.command()
@click.option('--status', 'status', type=click.STRING)
@click.pass_obj
def set_status(obj: dict, status: str):
    """Set the status of the last Version"""
    metadata: GenAiPromptTemplate = obj["metadata"]

    metadata.templateVersions[-1].status = status

    obj["metadata"] = metadata
