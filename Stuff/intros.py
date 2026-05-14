#! python3

import os
import urllib.request
import urllib.parse

from math import ceil
from time import sleep

from common import InstructionsFrame
from gui import GUI

from constants import PARTICIPATION_FEE, URL, ATTENTION_BONUS
from login import Login


################################################################################
# TEXTS intros

intro = """Studie se skládá z několika různých úkolů a otázek. Níže je uveden přehled toho, co Vás čeká:

<b>1) Skupiny:</b> Budete uvádět, jaké skupiny jsou Vám blízké.
<b>2) Rozhodovací úlohy:</b> Čeká Vás několik typů interaktivních úloh s opakovanými rozhodnutími, jejichž výsledky závisí na Vašich volbách a na volbách ostatních účastníků.
<b>3) Hra s hašením ohňů:</b> Nejprve absolvujete krátký tutoriál, poté odehrajete dvě hlavní kola hry.
<b>4) Výběr výrobků:</b> Ve dvou blocích budete vybírat výrobky, které budete moct získat.
<b>5) Dotazníky:</b> Vyplníte několik krátkých dotazníků.
<b>6) Závěrečné otázky:</b> Uvedete základní demografické údaje.
<b>7) Konec studie a platba:</b> Poté, co skončíte, půjdete do vedlejší místnosti, kde podepíšete pokladní doklad, na základě kterého obdržíte vydělané peníze v hotovosti. Jelikož v dokumentu bude uvedena pouze celková suma, experimentátor, který Vám bude vyplácet odměnu, nebude vědět, kolik jste vydělali v jednotlivých částech studie.

Veškeré interakce s ostatními účastníky studie proběhnou pouze přes počítač a anonymně. Nikdy nebudete navzájem vědět, s kým v rámci experimentu interagujete.

V případě, že máte otázky nebo narazíte na technický problém během úkolů, prosíme, zvedněte ruku a tiše vyčkejte příchodu výzkumného asistenta.

Všechny informace, které v průběhu studie uvidíte, jsou pravdivé a nebudete za žádných okolností klamáni či jinak podváděni."""


ending = """Toto je konec experimentu.
{}
Za účast na studii dostáváte {} Kč.

<b>Vaše odměna za tuto studii je tedy dohromady {} Kč, zaokrouhleno na desítky korun nahoru získáváte {} Kč. Napište prosím tuto (zaokrouhlenou) částku do příjmového dokladu na stole před Vámi.</b>

Výsledky studie založené na datech získaných v tomto experimentu budou volně dostupné na stránkách Decision Lab Prague (decisionlab.vse.cz) krátce po vyhodnocení dat a publikaci výsledků. 

<b>Žádáme Vás, abyste nesděloval(a) detaily této studie možným účastníkům, aby jejich volby a odpovědi nebyly ovlivněny a znehodnoceny.</b>
  
Můžete si vzít všechny svoje věci a vyplněný příjmový doklad, a aniž byste rušil(a) ostatní účastníky, odeberte se do vedlejší místnosti za výzkumným asistentem, od kterého obdržíte svoji odměnu. 

Děkujeme za Vaši účast!
 
Decision Lab Prague při FPH VŠE""" 


login = """Vítejte na výzkumné studii pořádané Fakultou podnikohospodářskou Vysoké školy ekonomické v Praze ve spolupráci s Univerzitou Karlovou! 

Za účast na studii obdržíte {} Kč. Kromě toho můžete vydělat další peníze v průběhu studie. 

Studie bude trvat cca 50-70 minut.

Děkujeme, že jste vypnuli své mobilní telefony, a že nebudete s nikým komunikovat v průběhu studie. Pokud s někým budete komunikovat, nebo pokud budete nějakým jiným způsobem narušovat průběh studie, budete požádáni, abyste opustili laboratoř, bez nároku na vyplacení peněz. Používání telefonů či psaní poznámek je během studie zakázáno, pokud budete používat telefon či si budete psát poznámky, budete požádáni, abyste opustili laboratoř bez nároku na vyplacení peněz. Prosíme, dodržujte tato pravidla, aby průběh studie byl pro všechny zúčastněné příjemný.

Pokud jste již tak neučinili, přečtěte si informovaný souhlas a podepište ho.""".format(PARTICIPATION_FEE)


################################################################################


# self.root.status["results"] += [charityNotChosenText] dat vsude, kde se popisuji vysledky


class Ending(InstructionsFrame):
    def __init__(self, root):
        root.texts["results"] = "\n" + "\n\n".join(root.status["results"]) + "\n"

        root.texts["reward"] = str(root.status["reward"])
        root.texts["rounded_reward"] = ceil(root.status["reward"] / 10) * 10
        root.texts["participation_fee"] = PARTICIPATION_FEE
        updates = ["results", "participation_fee", "reward", "rounded_reward"]
        super().__init__(root, text = ending, keys = ["g", "G"], proceed = False, height = "auto", update = updates, width = 100)
        self.file.write("Ending\n")
        self.file.write(self.id + "\t" + root.texts["reward"] + "\n\n")

    def run(self):
        self.sendInfo()

    def sendInfo(self):
        while True:
            self.update()    
            data = urllib.parse.urlencode({'id': self.root.id, 'round': -99, 'offer': self.root.texts["reward"]})
            data = data.encode('ascii')
            if URL == "TEST":
                response = "ok"
            else:
                try:
                    with urllib.request.urlopen(URL, data = data) as f:
                        response = f.read().decode("utf-8") 
                except Exception:
                    pass
            if "ok" in response:                     
                break              
            sleep(5)

    def gothrough(self):
        self.update()
        # Wait slightly above InstructionsFrame default wait=2 before triggering proceed.
        sleep(2.1)
        # KeyPress is sufficient because the frame binds progression on key press.
        self.update_idletasks()
        self.after(100, lambda: self.event_generate("<KeyPress-G>", when="tail"))






Intro = (InstructionsFrame, {"text": intro, "proceed": True, "height": "auto"})
Initial = (InstructionsFrame, {"text": login, "proceed": False, "height": "auto", "keys": ["g", "G"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,
         Initial, 
         Intro,
         Ending])
