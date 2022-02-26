from download_all_spells import download_all
from spellscraper import Spell, menu, capital
from search import spell_search
import pathlib
from re import search, sub
from os import listdir, path, mkdir
from pickle import load
PATH = str(pathlib.Path().resolve())
if not path.isdir('spells'):
    mkdir("spells")


def spell_lookup():
    spellfiles = listdir(PATH+'\\spells\\')
    spellname = input("\nSpell name (exit to leave): ").replace(
        " ", "-").replace("'", "")
    if spellname.lower() == "exit" or spellname == '':
        return ""
    if spellname.lower()+'.spll' in spellfiles:
        file = open(f"{PATH}/spells/{spellname}.spll", "rb")
        spell = load(file)
        file.close()
        return spell

    spell = Spell(spellname)
    bracket = search(r'\([^()]*\)', spellname)
    if bracket != None:
        bracket = bracket[0].split("(")[1].split(")")[0]
        spellname = sub(r'\([^()]*\)', '', spellname)

        if spellname[-1] == "-":
            spellname = spellname[:-1]
        spellname += f"-{bracket}"
    if spellname[-1] == "-":
        spellname = spellname[:-1]
    try:
        a = Spell(spellname)
        if a.valid:
            return a
    except:
        pass
    return "\nSpell not found"


def search_handler():
    print(
        "Searches for spell with all criteria.\nSeperate multiple criteria by space (users or components)")
    name = input("Name (whole or partial) > ")
    spelltype = input("Spelltype (school) > ")
    level = input("Level (cantrip, 2 etc.) > ")
    cast = input("Cast time (1 minute, 1 Action) > ")
    range = input("Spell range (self, 120 feet) > ")
    components = input("Components (V S M) > ")
    duration = input("Spell duration (up to 1 minute, Instantaneous) > ")
    concentration = input("Concentration (true, false) > ")
    users = input("Spell users (wizard sorcerer  (singular) etc) > ")
    homebrew = input("Is the spell homebrew (true, false) > ")
    query = ''
    if len(name) != 0:
        query += f'name={name}, '
    if len(spelltype) != 0:
        query += f'spelltype={spelltype}, '
    if len(level) != 0:
        query += f'level={level}, '
    if len(cast) != 0:
        query += f'cast={cast}, '
    if len(range) != 0:
        query += f'range={range}, '
    if len(components) != 0:
        query += f'components={components}, '
    if len(duration) != 0:
        query += f'duration={duration}, '
    if len(concentration) != 0:
        query += f'concentration={concentration}, '
    if len(users) != 0:
        query += f'users={users}, '
    if len(homebrew) != 0:
        query += f'homebrew={homebrew}, '
    if len(query) == 0:
        spells = []
    else:
        spells = spell_search(query)
    if len(spells) == 0:
        print("\nNo spells match criteria")
        return -1
    if len(spells) == 1:
        print(spells[0])
        return spells[0]
    selected = -1
    while True:
        choice = menu([capital(x.name.replace("-", " "))
                      for x in spells] + ["Exit"], "Choose a spell > ")
        if choice == "Exit":
            return selected
        selected = spells[[capital(x.name.replace("-", " "))
                           for x in spells].index(choice)]
        print()
        print()
        print(selected)
        print()


if __name__ == "__main__":
    running = True
    options = ["Spell Lookup", "Advanced Search",
               "Manually Add Spell", "Download all spells", "Exit"]

    while running:
        print()
        choice = menu(options, "> ")
        if choice == "Exit":
            running = False
            break
        elif choice == "Spell Lookup":
            spell = spell_lookup()
            print(f'\n{spell}')
        elif choice == "Advanced Search":
            spell = search_handler()
        elif choice == "Manually Add Spell":
            spell = Spell('', scrape=False)
        elif choice == "Download all spells":
            secondchoice = menu(["Yes", "No"], "Are you sure? > ")
            if secondchoice == "Yes":
                download_all()
