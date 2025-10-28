# Standard Library imports
import logging

# Dependency imports
import click

# Logger configuration
from salesforce_metadata_parser.logging.config import configure_root_logger
configure_root_logger()
logger = logging.getLogger(__name__)

# Other Project imports
import salesforce_metadata_parser.cli.metadata
import salesforce_metadata_parser.cli.genAiPromptTemplate

# Passes a namespace to store variables
# it can be used to chain results between commands
pass_ns = click.make_pass_decorator(dict, ensure=True)

@click.command()
@pass_ns
def version():
    """Show the version of the parser."""
    click.echo("Salesforce Metadata Parser v0.1.0")

@click.group()
@click.pass_context
def cli(ctx):
    """Salesforce Metadata Parser - A CLI tool for parsing Salesforce metadata files."""
    if ctx.obj is None:
        ctx.obj = dict()

    logger.info("Salesforce Metadata Parser - A CLI tool for parsing Salesforce metadata files.")

# Add commands
cli.add_command(salesforce_metadata_parser.cli.metadata.metadata)
cli.add_command(salesforce_metadata_parser.cli.genAiPromptTemplate.prompt_template)
cli.add_command(version)


if __name__ == "__main__":
    cli()
