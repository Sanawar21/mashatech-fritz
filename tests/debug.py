from app.clients import KleinanzeigenClient
from app.models.parser import AdParser

kc = KleinanzeigenClient()
ad = kc.get_ad("2923849354")
p = AdParser()
print(p.get_offer_price(ad.matches, ad))
print("Cause:")
print(f"{ad.account_age <= 7=}")
print(f"{ad.is_damaged=}")
print(f"{ad.is_only_pickup=}")
print(f"{not ad.price=}")
print(f"{not ad.is_buy_now_available=}")
