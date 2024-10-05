from app.clients import KleinanzeigenClient

invalid_offers = ["2881433479", "2881569505", "2881981202"]
valid_offers = ["2883723380", "2883723380"]
kc = KleinanzeigenClient()
inv = kc.get_ad(invalid_offers[0])
val = kc.get_ad(valid_offers[0])

print("INvalid")
print(inv.ad)

print("Valid")
print(val.ad)
