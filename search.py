import pathlib
from re import search
from os import listdir
from pickle import load
from time import time
from spellscraper import Spell
PATH = str(pathlib.Path().resolve())


def load_spells(selected_spells):
    spelllist = []
    for x in selected_spells:
        file = open(f'{PATH}/spells/{x}', 'rb')
        spelllist.append(load(file))
        file.close()
    return spelllist


def spell_search(query, results=-1):
    '''Search for spell by query, should be in format:
    "name=thunderbolt, user=sorcerer, level=1" '''
    spellfiles = listdir(PATH+'\\spells\\')
    possible_spells = []
    if "name=" in query:
        name = search(r"name=(.*?), ",
                      query).group(1).lower().replace(" ", "-")

        if f'{name}.spll' in spellfiles:
            file = open(f"{PATH}/spells/{name}.spll", "rb")
            c_spell = load(file)
            criteria = c_spell.__dict__
            for x in query.split(", "):
                term, answer = x.split("=")
                if term == "name":
                    continue
                elif term == "level":
                    if criteria["level"] == "cantrip":
                        check = "cantrip"
                    else:
                        check = [x for x in criteria["level"] if x.isdigit()]
                elif term not in criteria.keys():
                    return -1
                else:
                    check = criteria[term]

                if check != answer:
                    return -1
            return [c_spell]

        else:
            for ii in spellfiles:
                if name.lower().replace(" ", "-") in ii:
                    file = open(
                        f'{PATH}\\spells\\{ii}', "rb")
                    possible_spells.append(load(file))
                    file.close()
    else:
        possible_spells = load_spells(spellfiles)
    new_possible_spells = []
    for spell in possible_spells:
        add = True
        criteria = spell.__dict__
        for x in query.split(", ")[:-1]:
            term, answer = x.split("=")
            if term == "name":
                continue
            elif term == "level":
                if criteria["level"] == "cantrip":
                    check = "cantrip"
                else:
                    check = [x for x in criteria["level"] if x.isdigit()][0]
            elif term not in criteria.keys():
                print(spell.name)
                return -1
            else:
                check = criteria[term]

            if check in (True, False):
                check = str(check).lower()

            if term == "users" or term == "user" or term == "components":
                answer = answer.split(" ")
                for x in answer:
                    if x.lower() not in [x.lower() for x in check]:
                        add = False
            elif check != answer.lower():
                add = False
        if add:
            new_possible_spells.append(spell)
    return new_possible_spells


if __name__ == "__main__":
    query = 'homebrew=true, '

    print([x.name for x in spell_search(query)])
