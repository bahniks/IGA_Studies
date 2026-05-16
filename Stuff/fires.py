#! python3
# -*- coding: utf-8 -*-

import os
import random

from common import InstructionsFrame, InstructionsAndUnderstanding
from questionnaire import BlockQuestionnaire
from gui import GUI

from Tutorial_fire import FireTutorialGame
from Tutorial_sprinkler import SprinklerTutorialGame
from Tutorial_layout import LayoutTutorialGame
from experiment_game import ExperimentGame


################################################################################
# TEXTS

fires_intro_1 = """Tímto skončila část studie s úlohami, kde jste interagovali s ostatními účastníky. 

Nyní Vás čeká další část studie."""

fires_intro_2 = """V této části studie budete hrát počítačovou hru.

Nejprve absolvujete krátký trénink, ve kterém se naučíte, jak hra funguje. Poté odehrajete dvě kola hry.

Před každým kolem dostanete přesné informace o tom, jak se bude výsledek daného kola vyhodnocovat.
Po skončení této části bude jedno z hlavních kol náhodně vybráno jako rozhodné pro výplatu podle pravidel, která budou uvedena v průběhu hry.

Prosíme, čtěte veškeré instrukce pozorně."""

fires_rules = """Každé kolo budete začínat s počáteční částkou 100 Kč.

V průběhu hry se budou na obrazovce objevovat ohně. Za každý nový oheň se z částky okamžitě odečte 0,85 Kč. Každou sekundu se odečítá dalších 0,04 Kč za každý aktivní oheň. Pokud tedy hoří více ohňů najednou, ztráty se sčítají.

Každé kolo trvá 120 sekund, ale ihned skončí, pokud se částka sníží na 0 Kč.

Ohně můžete hasit dvěma způsoby: 

<i>První možností</i> je hasit jednotlivé ohně pomocí kyblíku. Uhašení jednoho ohně zastaví další průběžné ztráty z tohoto ohně, ale další ohně se budou objevovat dál do konce kola.

<i>Druhou možností</i> je spustit zavlažovací systém. To provedete tak, že postupně otevřete čtyři ventily ve správném pořadí. Jakmile otevřete čtvrtý ventil, spustí se zavlažovací systém, aktivní ohně se automaticky uhasí a další ohně se už nebudou objevovat. 

V tutoriálu se nyní naučíte oba způsoby hašení ohňů."""

fires_tutorial_bucket = """<center>V této části se naučíte, jak hasit jednotlivé ohně pomocí kyblíku.</center>"""

fires_tutorial_sprinkler = """<center>Tutoriál hašení ohňů je hotový. 

Nyní se naučíte, jak spustit zavlažovací systém.</center>"""

fires_tutorial_layout = """<center>Tutoriál zavlažovacího systému je hotový. 

Poslední část tutoriálu Vám ukáže celkové rozložení obrazovky, jak bude vypadat při hře.</center>"""

fires_understanding_intro = """Než hra začne, odpovězte na několik otázek, které ověří, že ovládání a pravidlům rozumíte."""

fires_understanding_questions = [
    [
        "Co se děje potom, co uhasíte jeden oheň pomocí kyblíku?",
        [
            "V daném kole se už žádné další ohně neobjeví.",
            "Další ohně se budou objevovat do konce kola či dokud se přidělená částka nesníží na 0 Kč.",
            "Po uhašení jednoho ohně se automaticky spustí zavlažovací systém.",
        ],
        [
            "To není správně. Uhašení jednoho ohně zastaví pouze postupné ztráty daného ohně; další ohně se budou nadále objevovat.",
            "Správně. Uhašení jednoho ohně zastaví pouze postupné ztráty daného ohně, další ohně se budou nadále objevovat.",
            "To není správně. Uhašení jednoho ohně zastaví pouze postupné ztráty daného ohně, další ohně se budou nadále objevovat. Postřikovač není možné spustit hašením ohňů.",
        ],
    ],
    [
        "Které tvrzení o kyblíku je správné?",
        [
            "Jedním naplněním kyblíku lze uhasit více ohňů.",
            "Kyblík se naplní jen tehdy, když podržíte kurzor v jezeře dostatečně dlouho, a jedním naplněním lze uhasit jeden oheň.",
            "Kyblík se naplní automaticky pokaždé, když se dotknete jezera.",
        ],
        [
            "To není správně. Jedním naplněným kyblíkem je možné uhasit právě jeden oheň. Po uhašení je potřeba opět kyblík v jezeře naplnit.",
            "Správně. Kyblík je potřeba držet nad jezerem, dokud se celý nenaplní. Když je plný, tak je možné uhasit právě jeden oheň. Po uhašení je potřeba opět kyblík v jezeře naplnit.",
            "To není správně. Kyblík je potřeba držet nad jezerem, dokud se celý nenaplní. Když je plný, tak je možné uhasit právě jeden oheň. Po uhašení je potřeba opět kyblík v jezeře naplnit.",
        ],
    ],
    [
        "Které tvrzení o zavlažovacím systému je správné?",
        [
            "Ventily je možné otevřít v libovolném pořadí a každý z nich hned snižuje počet nových ohňů.",
            "Stačí otevřít jeden ventil a postřikovač se spustí.",
            "Ventily je potřeba otevřít ve správném pořadí a po otevření všech čtyř se spustí zavlažovací systém.",
        ],
        [
            "To není správně. Ventily je potřeba otevřít ve správném pořadí a po otevření všech čtyř se spustí postřikovač a další ohně se poté přestanou objevovat.",
            "To není správně. Ventily je potřeba otevřít ve správném pořadí a po otevření všech čtyř se spustí postřikovač a další ohně se poté přestanou objevovat.",
            "Správně. Ventily je potřeba otevřít ve správném pořadí a po otevření všech čtyř se spustí postřikovač a další ohně se poté přestanou objevovat.",
        ],
    ],
]

fires_round_self = """V tomto kole hrajete <b>o svou vlastní finanční odměnu</b>.
V případě, že bude vylosováno toto kolo, tak částka, která Vám zbyde na konci tohoto kola, <b>bude přičtena k Vaší celkové odměně</b>.

Každý nově vzniklý oheň způsobí okamžitou finanční ztrátu a každý oheň, který zůstane aktivní, bude způsobovat další ztráty v čase.

Ohně můžete hasit dvěma způsoby. Můžete hasit jednotlivé ohně pomocí kyblíku, nebo můžete spustit zavlažovací systém postupným otevřením ventilů ve správném pořadí."""

fires_round_charity = """V tomto kole hrajete <b>o finanční výsledek určený pro charitativní účel</b>.
V případě, že bude vylosováno toto kolo, tak částka, která Vám zbyde na konci tohoto kola, <b>bude poslána na účet Nadace Dobrý anděl</b>.

Nadace Dobrý anděl je charitativní organizace, která díky příspěvkům dárců, Dobrých andělů, každý měsíc podporuje tisíce rodin s dětmi, které se ocitly v těžké životní situaci vlivem vážného onemocnění některého z členů rodiny, ať už dítěte, maminky nebo tatínka.
Dobří andělé podporují rodiny, v nichž se dítě nebo jeden z rodičů potýká s onkologickým nebo jiným vážným onemocněním a které se vlivem této nemoci ocitly ve složité životní situaci. Každý dar jim může pomoci lépe zvládat těžké chvíle související s náročnou léčbou.
Cílem nadace je vytvořit svět, kde naděje a podpora mají své místo a kde se lidé spojují, aby si navzájem pomáhali překonávat ty nejtěžší chvíle spjaté s vážným onemocněním.

Každý nově vzniklý oheň způsobí okamžitou finanční ztrátu a každý oheň, který zůstane aktivní, bude způsobovat další ztráty v čase.

Ohně můžete hasit dvěma způsoby. Můžete hasit jednotlivé ohně pomocí kyblíku, nebo můžete spustit zavlažovací systém postupným otevřením ventilů ve správném pořadí."""

fires_questionnaire_intro = """Ohodnoťte prosím následující tvrzení podle toho, jak jste hru prožíval(a).
Použijte škálu od 1 (silně nesouhlasím) do 7 (silně souhlasím)."""

selfResult = """V tomto kole zbylo {} Kč z původních 100 Kč. Pokud bude vylosováno toto kolo, tak bude tato částka přičtena k Vaší finální odměně."""
charityResult = """V tomto kole zbylo {} Kč z původních 100 Kč. Pokud bude vylosováno toto kolo, tak bude tato částka poslána na účet Nadace Dobrý anděl."""


################################################################################
# SCREENS

FiresIntro1 = (InstructionsFrame, {"text": fires_intro_1, "height": "auto"})
FiresIntro2 = (InstructionsFrame, {"text": fires_intro_2, "height": "auto"})
FiresRules = (InstructionsFrame, {"text": fires_rules, "height": "auto"})

FiresTutorialBucket = (InstructionsFrame, {"text": fires_tutorial_bucket, "height": "auto"})
FiresTutorialSprinkler = (InstructionsFrame, {"text": fires_tutorial_sprinkler, "height": "auto"})
FiresTutorialLayout = (InstructionsFrame, {"text": fires_tutorial_layout, "height": "auto"})

FiresUnderstanding = (
    InstructionsAndUnderstanding,
    {
        "text": fires_understanding_intro,
        "controlTexts": fires_understanding_questions,
        "name": "FiresInstructionsAndUnderstanding",
        "randomize": False,
        "height": "auto",
        "finalButton": "Pokračovat",
    },
)

FiresRoundSelf = (InstructionsFrame, {"text": fires_round_self, "height": "auto"})
FiresRoundCharity = (InstructionsFrame, {"text": fires_round_charity, "height": "auto"})


class FiresRoundIntro(InstructionsFrame):
    def __init__(self, root):
        if "fires_round_order" not in root.status:
            order = ["self", "charity"]
            random.shuffle(order)
            root.status["fires_round_order"] = order
            root.status["fires_round_index"] = 0
            root.status["fires_round_chosen"] = random.choice(order)
        order = root.status["fires_round_order"]
        condition = order[root.status["fires_round_index"]]
        root.status["fires_round_index"] += 1
        trial = root.status["fires_round_index"]
        chosen = root.status.get("fires_round_chosen", "NA")
        text = fires_round_self if condition == "self" else fires_round_charity
        root.file.write("FiresRound\n")
        root.file.write("\t".join([root.id, str(trial), condition, str(chosen)]) + "\n\n")
        super().__init__(root, text=text, height="auto")


class ResultGame(InstructionsFrame):
    def __init__(self, root):
        condition = root.status["fires_round_order"][root.status["fires_round_index"] - 1]
        reward = root.status["fires_round_reward"]
        text = selfResult.format(reward) if condition == "self" else charityResult.format(reward)
        super().__init__(root, text=text, height="auto")


FiresQuestionnaire = (
    BlockQuestionnaire,
    {
        "perpage": 4,
        "file": "fires_items.txt",
        "name": "FiresQuestionnaire",
        "left": "silně nesouhlasím",
        "right": "silně souhlasím",
        "options": 7,
        "shuffle": False,
        "instructions": fires_questionnaire_intro,
        "wraplength": 900,
        "center": True,
    },
)


################################################################################


def main():
    os.chdir(os.path.dirname(os.getcwd()))
    from login import Login
    from intros import Ending

    GUI([
        Login,
        #FiresIntro1,
        #FiresIntro2,
        #FiresRules,
        # FiresTutorialBucket,
        # FireTutorialGame,
        # FiresTutorialSprinkler,
        # SprinklerTutorialGame,
        # FiresTutorialLayout,
        # LayoutTutorialGame,
        # FiresUnderstanding,
        FiresRoundIntro,
        ExperimentGame,
        ResultGame,
        FiresQuestionnaire,
        FiresRoundIntro,
        ExperimentGame,
        ResultGame,
        FiresQuestionnaire,
        Ending,
    ])


if __name__ == "__main__":
    main()
