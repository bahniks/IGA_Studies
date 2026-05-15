from tkinter import *
from tkinter import ttk
from time import perf_counter
import random
import urllib.request
import urllib.parse

from common import InstructionsFrame, Wait
from constants import URL, TRUST_ENDOWMENT, MARKET_ENDOWMENT, MARKET_WIN, MARKET_LOSS, COORDINATION_SUCCESS, COORDINATION_PREFERENCE


games = """V první části studie se zúčastníte několika nezávislých rozhodovacích úloh. Některá Vaše rozhodnutí budou odměněna na základě skutečných peněžních výsledků.

Přestože jsou odpovědi v úlohách anonymní, některé preference mohou být zobrazeny ostatním účastníkům.

Prosím, čtěte instrukce pečlivě, protože Vaše odměna závisí jak na Vašich rozhodnutích, tak na rozhodnutích ostatních účastníků, a obdobně jejich odměna závisí na Vašich."""



trustResultTextA = """V úloze s dělením peněz bylo náhodně vybráno kolo {} role hráče A. Rozhodl(a) jste se poslat {} Kč. Tato částka byla ztrojnásobena na {} Kč. Ze svých {} Kč Vám poslal hráč B {} Kč. V této úloze jste tedy získal(a) {} Kč a hráč B {} Kč."""

trustResultTextB = """V úloze s dělením peněz bylo náhodně vybráno kolo {} role hráče B. Hráč A se rozhodl(a) poslat {} Kč. Tato částka byla ztrojnásobena na {} Kč. Ze svých {} Kč jste poslal(a) hráči A {} Kč. V této úloze jste tedy získal(a) {} Kč a hráč A {} Kč."""

marketResultText = """V úloze vstupu na trh bylo náhodně vybráno kolo {}. Vy jste se rozhodl(a) {} a druhý účastník {}. V tomto kole jste tedy získal(a) {} Kč."""
marketResultBothEnterText = """Oba jste vstoupili na trh. Váš výsledek v kvízu byl {} správně, druhý účastník měl {} správně."""
marketResultTieText = """Skóre bylo shodné, proto byl výherce určen náhodně: {}."""

coordinationResultText = """V koordinační úloze bylo náhodně vybráno {} kolo s {} partnerem. Vy jste měl(a) roli {} a zvolil(a) možnost {}. Druhý účastník zvolil možnost {}. V tomto kole jste tedy získal(a) {} Kč."""




class WaitResults(Wait):
    def __init__(self, root):
        super().__init__(
            root,
            what="results"
        )
        # Override the text and progress bar are already set by Wait.__init__
        # which sets:
        # text="Čekejte na data od ostatních účastníků studie"
        # and creates progressBar

    def _coordination_payoffs(self, role, my_decision, partner_decision):
        """Return (my_payoff, partner_payoff) for the coordination game.

        Role 1 prefers A, role 2 prefers B. Both get success bonus when choices match.
        """
        my_payoff = 0
        partner_payoff = 0

        if role == "1":
            if my_decision == "A":
                my_payoff += COORDINATION_PREFERENCE
            if partner_decision == "B":
                partner_payoff += COORDINATION_PREFERENCE
        elif role == "2":
            if my_decision == "B":
                my_payoff += COORDINATION_PREFERENCE
            if partner_decision == "A":
                partner_payoff += COORDINATION_PREFERENCE

        if my_decision == partner_decision:
            my_payoff += COORDINATION_SUCCESS
            partner_payoff += COORDINATION_SUCCESS

        return my_payoff, partner_payoff

    def checkUpdate(self):
        t0 = perf_counter() - 4
        while True:
            self.update()
            if perf_counter() - t0 > 5:
                t0 = perf_counter()
                if URL == "TEST":
                    response = self.test()
                else:
                    try:
                        data = urllib.parse.urlencode({"id": self.id, "round": "wait", "offer": "results"})
                        data = data.encode("ascii")
                        with urllib.request.urlopen(URL, data=data) as f:
                            response = f.read().decode("utf-8")
                    except Exception:
                        continue
                if response:
                    self.processResponse(response)
                    self.write(response)
                    self.progressBar.stop()
                    self.nextFun()
                    return

    def run(self):
        self.progressBar.start()
        self.checkUpdate()

    def test(self):
        # Simulate the new format for all three games
        # Coordination
        co_decisions = self.root.status.get("co_decisions", {})
        if co_decisions:
            block = random.choice(list(co_decisions.keys()))
            trials = co_decisions[block]
            trial_keys = list(trials.keys())
            trial = random.choice(trial_keys) if trial_keys else 1
            co_self = trials.get(trial, {}).get("decision", "A")
            co_other = random.choice(["A", "B"])
            co_part = f"coordination:{block},{trial},{co_self},{co_other}"
        else:
            co_part = "coordination:1,1,A,B"

        # Market
        me_decisions = self.root.status.get("me_decisions", {})
        me_quiz_scores = self.root.status.get("me_quiz_scores", {})
        if me_decisions:
            block = random.choice(list(me_decisions.keys()))
            decision_self = me_decisions[block]
            quiz_self = me_quiz_scores.get(block, random.randint(0, 5))
            decision_other = random.choice(["enter", "stayout"])
            quiz_other = random.randint(0, 5)
            tie_winner = random.choice(["Y", "N"])
            me_part = f"market:{block},{decision_self},{quiz_self},{decision_other},{quiz_other},{tie_winner}"
        else:
            me_part = "market:1,enter,3,stayout,2,Y"

        # Trust
        decisions = self.root.status.get("trust_decisions", {})
        if decisions:
            chosen_round = random.choice(list(decisions.keys()))
            d = decisions[chosen_round]
            role = str(d.get("role", "1"))
            if role == "1":
                sentA = int(d.get("sentA", TRUST_ENDOWMENT // 2))
                max_return = TRUST_ENDOWMENT + sentA * 3
                sentB = random.choice(list(range(0, max_return + 1, 8)))
            else:
                sentA_points = [0, 8, 16, 24, 32, 40]
                sentA = random.choice(sentA_points)
                sentB_list = d["sentB_list"]
                idx = sentA_points.index(sentA)
                sentB = int(sentB_list[idx])
            trust_part = f"trust:{chosen_round},{role},{sentA},{sentB}"
        else:
            trust_part = f"trust:1,1,{TRUST_ENDOWMENT//2},{TRUST_ENDOWMENT//2}"

        return f"{co_part}|{me_part}|{trust_part}"

    def processResponse(self, response):
        # Parse format: coordination:<round>,<trial>,<self>,<other>|market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>,<tie_winner>|trust:<round>,<role>,<sentA>,<sentB>        
        sections = response.split("|")
        results = self.root.status.get("results")
        if not isinstance(results, list):
            results = []
        reward_so_far = self.root.status.get("reward", 0)
        if not isinstance(reward_so_far, (int, float)):
            reward_so_far = 0

        for section in sections:
            if section.startswith("coordination:"):
                # coordination:<round>,<trial>,<self>,<other>
                _, data = section.split(":", 1)
                parts = data.split(",")
                if len(parts) == 4:
                    round_idx = int(parts[0])
                    trial_idx = int(parts[1])
                    co_self = parts[2]
                    co_other = parts[3]
                    role = self.root.status["co_roles"][round_idx]
                    payoff, partner_payoff = self._coordination_payoffs(role, co_self, co_other)
                    partner_ordinals = {1: "prvním", 2: "druhým", 3: "třetím"}
                    partner_label = partner_ordinals.get(round_idx, f"{round_idx}.")
                    role_label = f"Hráč {role}"
                    result_text = coordinationResultText.format(
                        trial_idx, partner_label, role_label, co_self, co_other, payoff, partner_payoff
                    )
                    results.append(result_text)
                    self.root.status["coordination_result"] = {
                        "round": round_idx,
                        "trial": trial_idx,
                        "role": role,
                        "my_decision": co_self,
                        "partner_decision": co_other,
                        "reward": payoff,
                        "partner_reward": partner_payoff,
                    }
                    reward_so_far += payoff

            elif section.startswith("market:"):
                # market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>,<tie_winner>
                _, data = section.split(":", 1)
                parts = data.split(",")
                if len(parts) == 6:
                    round_idx = int(parts[0])
                    decision_self = parts[1].strip().lower()
                    quiz_self = int(parts[2])
                    decision_other = parts[3].strip().lower()
                    quiz_other = int(parts[4])
                    tie_winner = parts[5].strip()

                    self_entered = decision_self in ("in", "enter")
                    other_entered = decision_other in ("in", "enter")

                    self_text = "vstoupit na trh" if self_entered else "nevstoupit na trh"
                    other_text = "vstoupil(a) na trh" if other_entered else "nevstoupil(a) na trh"

                    # Calculate payoff
                    if self_entered and other_entered:
                        if quiz_self > quiz_other:
                            payoff = MARKET_WIN
                        elif quiz_self < quiz_other:
                            payoff = MARKET_LOSS
                        else:
                            # Tie: use tie_winner
                            if tie_winner == "Y":
                                payoff = MARKET_WIN
                                winner_text = "výhru jste získal(a) Vy"
                            elif tie_winner == "N":
                                payoff = MARKET_LOSS
                                winner_text = "výhru získal druhý účastník"
                            else:
                                payoff = random.choice([MARKET_WIN, MARKET_LOSS])
                                winner_text = "výhru získal(a) Vy" if payoff == MARKET_WIN else "výhru získal druhý účastník"
                        result_text = marketResultText.format(round_idx, self_text, other_text, payoff)
                        result_text += " " + marketResultBothEnterText.format(quiz_self, quiz_other)
                        if quiz_self == quiz_other:
                            result_text += " " + marketResultTieText.format(winner_text)
                    elif self_entered:
                        payoff = MARKET_WIN
                        result_text = marketResultText.format(round_idx, self_text, other_text, payoff)
                    else:
                        payoff = MARKET_ENDOWMENT
                        result_text = marketResultText.format(round_idx, self_text, other_text, payoff)
                    results.append(result_text)
                    self.root.status["market_result"] = {
                        "round": round_idx,
                        "decision_self": decision_self,
                        "quiz_self": quiz_self,
                        "decision_other": decision_other,
                        "quiz_other": quiz_other,
                        "tie_winner": tie_winner,
                        "reward": payoff,
                    }
                    reward_so_far += payoff

            elif section.startswith("trust:"):
                # trust:<round>,<role>,<sentA>,<sentB>
                _, data = section.split(":", 1)
                parts = data.split(",")
                if len(parts) == 4:
                    round_idx = int(parts[0])
                    role = str(parts[1])
                    sentA = int(parts[2])
                    sentB = int(parts[3])
                    if role == "1":
                        reward = TRUST_ENDOWMENT - sentA + sentB
                        result_text = trustResultTextA.format(
                            round_idx,
                            sentA,
                            sentA * 3,
                            TRUST_ENDOWMENT + sentA * 3,
                            sentB,
                            TRUST_ENDOWMENT - sentA + sentB,
                            TRUST_ENDOWMENT + sentA * 3 - sentB,
                        )
                    elif role == "2":
                        reward = TRUST_ENDOWMENT + sentA * 3 - sentB
                        result_text = trustResultTextB.format(
                            round_idx,
                            sentA,
                            sentA * 3,
                            TRUST_ENDOWMENT + sentA * 3,
                            sentB,
                            TRUST_ENDOWMENT + sentA * 3 - sentB,
                            TRUST_ENDOWMENT - sentA + sentB,
                        )
                    else:
                        raise ValueError(f"Invalid trust role value: {role}")
                    results.append(result_text)
                    self.root.status["trust_result"] = {
                        "round": round_idx,
                        "role": role,
                        "sentA": sentA,
                        "sentB": sentB,
                        "reward": reward,
                    }
                    reward_so_far += reward

        self.root.status["results"] = results
        self.root.status["reward"] = reward_so_far

    def write(self, response):
        self.file.write("Final Results\n")        
        self.file.write(self.id + "\t" + response.replace("|", "\t") + "\n\n")




GamesIntro = (InstructionsFrame, {"text": games, "proceed": True, "height": "auto"})