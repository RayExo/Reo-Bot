import random
import discord

red = 0xff0000
green = 0x00ff2a
blue = 0x0000ff
orange = 0xff9500
yellow = 0xfff700
aqua = 0x00eeff
purple = 0x5900ff
pink = 0xee00ff
white = 0xffffff
black = 000000
gray = 0x808080
cyan = 0x00eeff

def random_color():
    return discord.Colour(random.randint(0, 0xFFFFFF))