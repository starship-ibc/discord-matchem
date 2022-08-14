from venv import create
from .card import create_cards

cards = create_cards(4)

cards["combined_image"].save(filename="card.png")
print(f"Match = {cards['match_info']}")
