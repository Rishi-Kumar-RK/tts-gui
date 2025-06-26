import click

from tts_gui import main

@click.command()
def tts_main():
    main.tts_main()