import random
from copy import deepcopy
from random import randint
from typing import List

from wand.image import Image

from .assets import images as image_assets


def pick_images(count: int):
    options = deepcopy(image_assets)
    images = []
    while len(images) < count:
        n = randint(0, len(options) - 1)
        images.append(options.pop(n))
    return images


def create_card(image_infos: List):
    card = Image(filename="images/bg.png")
    images = [Image(filename=i["image"]) for i in image_infos]
    print(f"images = {[i['id'] for i in image_infos]}")
    for image in images:
        s = random.randint(100, 220)
        image.resize(width=s, height=s)
        image.rotate(random.randint(0, 360))

    image = images.pop(random.randint(0, len(images) - 1))
    l, t = int(128 - (image.width / 2)), int(128 - (image.height / 2))
    card.composite_channel("0", image, "dissolve", l, t)

    image = images.pop(random.randint(0, len(images) - 1))
    l, t = int(384 - (image.width / 2)), int(128 - (image.height / 2))
    card.composite_channel("0", image, "dissolve", l, t)

    image = images.pop(random.randint(0, len(images) - 1))
    l, t = int(384 - (image.width / 2)), int(384 - (image.height / 2))
    card.composite_channel("0", image, "dissolve", l, t)

    image = images.pop(random.randint(0, len(images) - 1))
    l, t = int(128 - (image.width / 2)), int(384 - (image.height / 2))
    card.composite_channel("0", image, "dissolve", l, t)

    return card


def create_cards(images_per_card: int):
    image_set = pick_images(images_per_card * 2 - 1)
    cards = []
    cards.append(create_card(image_set[:images_per_card]))
    cards.append(create_card(image_set[images_per_card - 1 :]))

    border = 5
    image = Image(width=cards[0].width * 2 + border, height=cards[0].height)
    image.composite_channel("0", cards[0], "dissolve", 0, 0)
    image.composite_channel("1", cards[1], "dissolve", cards[0].width + border, 0)

    return {
        "cards": cards,
        "combined_image": image,
        "match_info": image_set[3],
        "card_info": image_set,
    }
