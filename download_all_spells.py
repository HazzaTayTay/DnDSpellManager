from bs4 import BeautifulSoup
from requests import get
from re import findall, search, sub
from time import time
from spellscraper import Spell

try:
    from tqdm import tqdm
except:
    pass

    def tqdm(a, b):
        return a


def download_all():
    roll20 = get("http://dnd5e.wikidot.com/spells/javascript;").text
    goodsoup = BeautifulSoup(roll20, "html.parser")

    spell_html = goodsoup.find_all("div", class_="yui-content")

    spellhtml = spell_html[0].findChildren("a", recursive=True)

    spell_names = [x.text.lower().replace(" ", "-") for x in spellhtml]

    for ii in tqdm(spell_names, "Spells downloaded"):
        bracket = search(r'\([^()]*\)', ii)
        if bracket != None:
            bracket = bracket[0].split("(")[1].split(")")[0]
            ii = sub(r'\([^()]*\)', '', ii)

            if ii[-1] == "-":
                ii = ii[:-1]
            ii += f"-{bracket}"
        if ii[-1] == "-":
            ii = ii[:-1]
        try:
            a = Spell(ii)
        except:
            pass


if __name__ == "__main__":
    download_all()
