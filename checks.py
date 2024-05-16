import discord

OWNER_IDS = [1174000666012823565, 1108126443638116382]
DEV_IDS = [952344652604903435, 1174000666012823565, 1028698287999553556]


def is_owner(ctx):
    return ctx.message.author.id in OWNER_IDS


def is_dev(ctx):
    return ctx.message.author.id in DEV_IDS
