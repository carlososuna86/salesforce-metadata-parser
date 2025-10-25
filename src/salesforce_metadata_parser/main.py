import click

@click.group()
def cli():
    """Salesforce Metadata Parser - A CLI tool for parsing Salesforce metadata files."""
    pass

@cli.command()
def version():
    """Show the version of the parser."""
    click.echo("Salesforce Metadata Parser v0.1.0")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def parse(input_file):
    """Parse a Salesforce metadata file."""
    click.echo(f"Parsing metadata file: {input_file}")
    # Implementation will go here

if __name__ == "__main__":
    cli()
