from .parser import AdParser
from .match import Match
from datetime import datetime


class Ad:
    __parser = AdParser()

    def __init__(self, data) -> None:
        self.ad = data

        self.title = self.ad["title"]["value"]
        self.account_age = self.__get_age()
        self.is_only_pickup = self.__is_only_pickup()
        self.link = self.ad["link"][-1]["href"]

        self.uid = self.link.split("/")[-1].split("-")[0]

        # date in dd/MM/yyyy format
        self.date = datetime.now().strftime("%d/%m/%Y")

        try:
            self.price = self.ad["price"]["amount"]["value"]
        except:
            self.price = None
        try:
            self.description = self.ad["description"]["value"]
        except:
            self.description = None
        try:
            self.poster_name = self.ad["contact-name"]["value"]
        except:
            self.poster_name = None
        try:
            self.zip_code = self.ad["ad-address"]["zip-code"]
        except:
            self.zip_code = None

        self.is_damaged = self.__is_damaged(
        ) or "defekt" in f"{self.title} {self.description}".lower()

        self.matches: list[Match] = self.__parser.find_matches(
            self.title, self.description)
        self.offer_price = self.__parser.get_offer_price(self.matches, self)

    def __get_age(self):
        date_str = self.ad["user-since-date-time"]["value"]
        date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        date = datetime.strptime(date_str, date_format)
        current_date = datetime.now(date.tzinfo)
        days_passed = (current_date - date).days
        return days_passed

    def __is_only_pickup(self):
        holder = []
        try:
            for attribute in self.ad["attributes"]["attribute"]:
                if attribute["localized-label"] == "Versand":

                    try:
                        holder.extend(attribute["value"])
                    except TypeError:
                        holder.append(attribute["value"])

                    for value in holder:
                        if value["localized-label"] == "Nur Abholung":
                            return True

            return False
        except:
            return False

    def __is_damaged(self):
        holder = []
        try:
            for attribute in self.ad["attributes"]["attribute"]:
                if attribute["localized-label"] == "Zustand":

                    try:
                        holder.extend(attribute["value"])
                    except TypeError:
                        holder.append(attribute["value"])

                    for value in holder:
                        if value["localized-label"] == "Defekt":
                            return True

            return False
        except:
            return False

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "link": self.link,
            "acc_age": self.account_age,
            "only_pickup": self.is_only_pickup,
            "damaged": self.is_damaged,
            "zip_code": self.zip_code,
            "poster_name": self.poster_name,
        }
