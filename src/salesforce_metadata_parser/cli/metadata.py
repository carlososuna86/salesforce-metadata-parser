import click
import logging

from ..parser.metadata_parser import XmlParser

logger = logging.getLogger(__name__)

@click.group()
def metadata():
    pass

@metadata.command()
@click.option('--source-file', 'source_file', type=click.Path(exists=True))
@click.pass_context
def parse(ctx, source_file):
    """Parse a Salesforce metadata file."""
    # Implementation will go here
    logger.debug(f"source_file: {source_file}")

    click.echo(f"Parsing metadata file: {source_file}")
    metadata = XmlParser.from_xml_file(source_file)
    ctx.obj["metadata"] = metadata
