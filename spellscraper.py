import requests
from re import sub, compile, findall
from pickle import dump, load
from os import path, mkdir
import pathlib
from time import time
from bs4 import BeautifulSoup
PATH = pathlib.Path().resolve()
tags = compile('<.*?>')
brackets = compile(' \(.*?\)')
symbols = compile('&.*?;')
schools = ["abjuration", "conjuration", "divination", "enchantment",
           "evocation", "illusion", "necromancy", "transmutation"]


if not path.isdir('spells'):
    mkdir("spells")


def menu(options, prompt):
    if len(options) == 0:
        return 'No Options'
    for x in range(len(options)):
        print(f'{x+1}: {options[x]}')
    choice = True
    while choice:
        dec = input(prompt)
        try:
            dec = int(dec)
            if dec in list(range(1, len(options)+1)):
                return options[dec-1]
        except:
            pass
        print("Pick an option\n")


def capital(st):
    return " ".join([x.capitalize() if len(x) >= 2 else x for x in st.split(" ")])


def clean_html(text):
    text = sub(tags, "", text)
    text = sub(symbols, " ", text)
    return text


def clean_table(table):
    table = table.replace(
        '<table class="wiki-content-table">', '').replace("</table>", "")
    text_bits = table.replace("<tr>", "TEXTBIT").replace("<td>", "TEXTBIT").replace(
        "<th>", "TEXTBIT").replace("</tr>", "TEXTBIT").replace("</td>", "TEXTBIT").replace("</th>", "TEXTBIT").split("TEXTBIT")
    text_bits = [x for x in text_bits if x != ""]
    lengths = list(map(len, text_bits))
    paddedlength = max(lengths) + 2

    table_string = ''
    for ii in range(0, len(text_bits), 2):
        table_string += f"{text_bits[ii].ljust(paddedlength)}{text_bits[ii+1]}\n"
        if ii == 0:
            table_string += "\n"
    return table_string[:-1]


def clean_table3(table):
    # Seperate into tables
    different_tables = []
    soup = BeautifulSoup(table, "html.parser")
    rows = soup.find_all("tr")
    rows = [str(x) for x in rows]
    head = rows[0]
    body = []
    for row in rows[1:]:
        if "<th" in row:
            different_tables.append((head, body))
            head = row
            body = []
        else:
            body.append(row)
    different_tables.append((head, body))

    table_text = ''

    for head, body in different_tables:
        headers = [clean_html(x) for x in head.split(
            "</th>") if clean_html(x) != ""]

        clean_rows = []
        for row in body:
            clean_rows.append([clean_html(x) for x in row.split(
                "</td>") if clean_html(x) != ""])

        # Finding actual max buffer size

        lengths = [[len(x) for x in row]
                   for row in clean_rows+headers if len(row) == len(headers)]
        column_widths = [len(x)+2 for x in headers]
        for ii in range(len(headers)):
            for n in lengths:
                if n[ii]+2 > column_widths[ii]:
                    column_widths[ii] = n[ii]+2

        if len(column_widths) == 1:
            column_widths[0] = 1

        for ii in range(len(headers)):
            item = headers[ii]
            table_text += item.ljust(column_widths[ii])
        table_text += "\n\n"
        for row in clean_rows:
            for ii in range(len(row)):
                if len(row) == len(headers):
                    table_text += row[ii].ljust(column_widths[ii])
                else:
                    table_text += row[ii] + "  "

            table_text += '\n'

        table_text += "\n\n\n"

    return table_text[:-4]


def get_spell(name):
    table_in = False
    appo = "'"
    if "-ua" in name or "-hb" in name:
        name = "-".join(name.lower().split(" ")).replace("/",
                                                         "-").replace(":", "").replace(appo, "-")
    else:
        name = "-".join(name.lower().split(" ")).replace("/",
                                                         "-").replace(":", "").replace(appo, "")

    spellpage = requests.get(
        f'http://dnd5e.wikidot.com/spell:{name}')
    if spellpage.status_code != 200:
        if "-hb" or "-ua" in name:
            spellpage = requests.get(
                f'http://dnd5e.wikidot.com/spell:{name.replace("-hb", "").replace("-ua", "")}')

        if spellpage.status_code != 200:
            if "-hb" or "-ua" in name and "-s-" in name:
                spellpage = requests.get(
                    f'http://dnd5e.wikidot.com/spell:{name.replace("-s-", "s-")}')

            if spellpage.status_code != 200:
                return -1
    spell = spellpage.text.split(
        '<div class="content-separator" style="display: none:"></div>')[1].replace("\n", "").split("</p><p>")

    spell = spell[1:]

    levelplus = clean_html(spell[0]).split(" ")
    if "-" in spell[0]:
        level = [x for x in levelplus[0].replace("-", " ") if x.isdigit()][0]
        spelltype = levelplus[1]
    else:
        level = levelplus[1]
        spelltype = levelplus[0]

    if len(levelplus) > 2:
        notes = " ".join(levelplus[2:])
    else:
        notes = ''

    parameterstring = spell[1].split("<br />")
    parameters = {}
    for ii in parameterstring:
        parameters[clean_html(ii.split(":</strong>")[0])
                   ] = ii.split("</strong>")[1].lstrip()

    description = spell[2]
    for ii in spell[3:]:
        description += "\n\n" + ii
    if "</table>" in description:
        table_in = True

        table = description.split(
            "</table>")[0].split('<table class="wiki-content-table">')[1]
        fixed_table = f"\n\n{clean_table3(table)}\n\n"
        description = description.split(
            '<table class="wiki-content-table">')[0]+'<table class="wiki-content-table">' + fixed_table + '</table>' + description.split('</table>')[1]

    keyword = ''
    if "Spell Lists." in description:
        keyword = "Spell Lists."
    elif "Spell Lists:" in description:
        keyword = "Spell Lists:"
    elif "Spell lists." in description:
        keyword = "Spell lists."
    else:
        return -1

    description = description.split(keyword)[0]
    if keyword == "Spell lists.":
        users = spell[-1].split(f"{keyword}</strong> ")[1].split(", ")
    else:
        users = spell[-1].split(f"{keyword}</em></strong> ")[1].split(", ")

    if max([len(x) for x in users]) >= 20 or len(users) > 6:
        new_users = []

        for x in users:
            if len(clean_html(x)) < 15 and '<table class="wiki-content-table">' not in x:
                new_users.append(clean_html(x))
            else:
                new_users.append(clean_html(x.split("</p>")[0]))
                break
        users = new_users
    description = clean_html(description)

    if table_in and fixed_table not in description:
        description += fixed_table

    return (level, spelltype, notes, parameters, description, users)


class Spell():
    def __init__(self, name, scrape=True):
        '''Creates the spell object by webscraping http://dnd5e.wikidot.com/'''
        self.valid = True
        if not scrape:
            spell = self.get_spell_data()
            if spell == -1:
                self.valid = False
            else:
                description, stats = spell
                self.homebrew = stats["homebrew"]
                self.name = stats["name"].lower()
                self.level = stats["level"].lower()
                self.spelltype = stats["spelltype"].lower()
                self.notes = stats["notes"].lower()
                self.cast = stats["cast"].lower()
                self.range = stats["range"].lower()
                self.components = stats["components"].lower()
                self.duration = stats["duration"].lower()
                self.description = description
                self.users = [x.lower() for x in stats["users"].split(", ")]
                self.concentration = stats["concentration"]
        else:
            spell = get_spell(name)
            if spell == -1:
                self.valid = False
                pass
            else:
                self.valid = True
                self.homebrew = False
                if "-ua" in name:
                    name = name.split("-ua")[0]
                elif "-hb" in name:
                    name = name.split("-hb")[0]
                self.name = "-".join(name.lower().split(" ")).replace("/",
                                                                      "-").replace(":", "").replace("'", "")
                self.level = spell[0].lower()
                self.spelltype = spell[1].lower()
                self.notes = spell[2].lower()
                self.cast = spell[3]["Casting Time"].lower()
                self.range = spell[3]["Range"].lower()
                self.components = spell[3]["Components"].lower()
                self.duration = spell[3]["Duration"].lower()
                if "concentration" in self.duration:
                    self.concentration = True
                    self.duration = self.duration.replace(
                        "concentration, ", "")
                else:
                    self.concentration = False
                self.description = spell[4]
                self.users = [x.lower() for x in spell[5]]
        if self.valid:
            self.save()

    def save(self):
        if not self.valid:
            return -1
        file = open(
            f"{PATH}/spells/{self.name.lower().replace(' ' , '-')}.spll", "wb")
        dump(self, file)
        file.close()

    def get_spell_data(self):
        data = self.file_load()

        status = self.check_data(data)
        if status[0] != 200:
            print(f"Load Failed\nError {status[0]}: {status[1]}")
            return -1

        if data[1]['homebrew'].lower() == "false":
            data[1]['homebrew'] = False
        else:
            data[1]['homebrew'] = True
        if data[1]['concentration'].lower() == "false":
            data[1]['concentration'] = False
        else:
            data[1]['concentration'] = True

        return data

    def file_load(self):
        filename = input("Filename > ")
        try:
            file = open(filename, "r")
            data = [x[:-1] for x in file.readlines()]
            file.close()
        except:
            return -1
        description = ''
        attributes = {}
        for ii, line in enumerate(data):
            if ":" in line and ii <= 10:
                key, term = line.split(":")
                attributes[key] = term
            else:
                description += line + "\n\n"
        description = description[:-2]

        return description, attributes

    def check_data(self, data):
        if data == -1:
            return 404, "File not found"

        desc, attributes = data
        required = set(["name", "level", "spelltype", "cast", "range",
                        "components", "duration", "concentration", "users", "homebrew", "notes"])
        if required != set(attributes.keys()):
            return 400, "Wrong spell attributes found"

        if not attributes["level"].isdigit() and not attributes["level"].lower() == "cantrip":
            return 400, "level not accepted"
        if not min([sub(brackets, "", x.strip().lower()) in ["v", "s", "m"] for x in attributes["components"].split(", ")]):
            return 400, "components not accepted"
        if attributes["concentration"].lower() not in ["true", "false"]:
            return 400, "concentration not true or false"
        if attributes["homebrew"].lower() not in ["true", "false"]:
            return 400, "homebrew not true or false"
        if attributes["spelltype"].lower() not in schools:
            return 400, "spelltype not accepted"

        return 200, "good"

    def __str__(self):
        if not self.valid:
            return "Spell not valid"
        printable = ''
        printable += f'Name: {capital(self.name.replace("-", " "))}\nLevel: {capital(self.level)}\nType: {capital(self.spelltype)}\n {capital(self.notes)}\n\n '
        printable += f'Stats\n\nCast time: {capital(self.cast)}\nDuration: {capital(self.duration)}\nRange: {capital(self.range)}\n'
        printable += f'Components: {self.components}\nConcentration: {self.concentration}\nUsed by: {capital(", ".join(self.users))}\n\n'
        printable += f'{self.description}\n'
        return printable


if __name__ == "__main__":
    a = Spell('', scrape=False)
    '''
    while True:
        name = input("> ")
        if name == "":
            break
        levitate = Spell(name)
        print("\n\n")
        print(levitate)
    '''
