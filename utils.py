from pyfiglet import Figlet

figlet = Figlet(font="smslant")


def create_banner(text: str):
    return figlet.renderText(text)
