from tkinter import *
from tkinter import ttk
from time import perf_counter
import random
import urllib.request
import urllib.parse

from common import InstructionsFrame, Wait
from constants import URL, TRUST_ENDOWMENT, MARKET_ENDOWMENT, MARKET_WIN, MARKET_LOSS, COORDINATION_SUCCESS


games = """V první části studie se zúčastníte několika nezávislých rozhodovacích úloh. Některá Vaše rozhodnutí budou odměněna na základě skutečných peněžních výsledků.

Přestože jsou odpovědi v úlohách anonymní, některé preference mohou být zobrazeny ostatním účastníkům.

Prosím, čtěte instrukce pečlivě, protože Vaše odměna závisí na Vašich rozhodnutích a ve všech úlohách také na rozhodnutích ostatních účastníků."""





trustResultTextA = """V úloze s dělením peněz Vám byla náhodně vybrána role hráče A. Rozhodl(a) jste se poslat {} Kč. Tato částka byla ztrojnásobena na {} Kč. Ze svých {} Kč Vám poslal hráč B {} Kč. V této úloze jste tedy získal(a) {} Kč a hráč B {} Kč."""

trustResultTextB = """V úloze s dělením peněz Vám byla náhodně vybrána role hráče B. Hráč A se rozhodl(a) poslat {} Kč. Tato částka byla ztrojnásobena na {} Kč. Ze svých {} Kč jste poslal(a) hráči A {} Kč. V této úloze jste tedy získal(a) {} Kč a hráč A {} Kč."""

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

    def _has_trust_data(self):
        return bool(self.root.status.get("trust_decisions"))

    @staticmethod
    def _normalize_coordination_role(role_raw):
        if role_raw == "A":
            return "1"
        if role_raw == "B":
            return "2"
        role = str(role_raw)
        if role in ("1", "2"):
            return role
        raise ValueError(f"Invalid role value: {role_raw}")

    def _coordination_role_for_block(self, block):
        roles = self.root.status["co_roles"]
        if block not in roles:
            raise KeyError(f"Role for block {block} not found in co_roles")
        return self._normalize_coordination_role(roles[block])

    def _append_market_result(self):
        if self.root.status.get("market_result_recorded"):
            return

        me_decisions = self.root.status.get("me_decisions", {})
        if not me_decisions:
            return

        # Compute pairings for all rounds if not already done
        if not self.root.status.get("me_results"):
            me_quiz_scores = self.root.status.get("me_quiz_scores", {})
            me_results = {}
            for block, my_decision in me_decisions.items():
                my_score = me_quiz_scores.get(block, 0)
                partner_decision = random.choice(["enter", "stayout"])
                partner_score = random.randint(0, 5)
                tie_winner = None

                if my_decision == "stayout" and partner_decision == "stayout":
                    payoff = MARKET_ENDOWMENT
                    entrants = 0
                elif my_decision == "enter" and partner_decision == "stayout":
                    payoff = MARKET_WIN
                    entrants = 1
                elif my_decision == "stayout" and partner_decision == "enter":
                    payoff = MARKET_ENDOWMENT
                    entrants = 1
                else:  # both enter
                    entrants = 2
                    if my_score > partner_score:
                        payoff = MARKET_WIN
                    elif my_score < partner_score:
                        payoff = MARKET_LOSS
                    else:
                        payoff = MARKET_WIN if random.random() >= 0.5 else MARKET_LOSS
                        tie_winner = "you" if payoff == MARKET_WIN else "partner"

                me_results[block] = {
                    "decision": my_decision,
                    "partner_decision": partner_decision,
                    "entrants": entrants,
                    "payoff": payoff,
                    "my_score": my_score,
                    "partner_score": partner_score,
                    "tie_winner": tie_winner,
                }
                self.file.write("MarketEntryWait\n")
                self.file.write("\t".join([
                    self.id, str(block), my_decision, partner_decision,
                    str(entrants), str(payoff),
                ]))
                self.file.write("\n\n")
            self.root.status["me_results"] = me_results

        me_results = self.root.status.get("me_results", {})
        chosen_round = random.choice(list(me_results.keys()))
        selected = me_results.get(chosen_round, {})

        my_decision = selected.get("decision", "stayout")
        partner_decision = selected.get("partner_decision", "stayout")
        entrants = int(selected.get("entrants", 0))
        payoff = int(selected.get("payoff", 0))

        my_decision_text = "vstoupit na trh" if my_decision == "enter" else "nevstoupit na trh"
        partner_decision_text = "vstoupil(a) na trh" if partner_decision == "enter" else "nevstoupil(a) na trh"
        result_text = marketResultText.format(chosen_round, my_decision_text, partner_decision_text, entrants, payoff)

        if my_decision == "enter" and partner_decision == "enter":
            my_score = selected.get("my_score")
            partner_score = selected.get("partner_score")
            if my_score is not None and partner_score is not None:
                result_text += " " + marketResultBothEnterText.format(my_score, partner_score)
                if my_score == partner_score:
                    tie_winner = selected.get("tie_winner")
                    if tie_winner == "you":
                        winner_text = "výhru jste získal(a) Vy"
                    elif tie_winner == "partner":
                        winner_text = "výhru získal druhý účastník"
                    else:
                        winner_text = "výsledek losu nebyl zaznamenán"
                    result_text += " " + marketResultTieText.format(winner_text)

        reward_so_far = self.root.status.get("reward", 0)
        if not isinstance(reward_so_far, (int, float)):
            reward_so_far = 0
        self.root.status["reward"] = reward_so_far + payoff

        results = self.root.status.get("results")
        if not isinstance(results, list):
            results = []
        results.append(result_text)
        self.root.status["results"] = results

        self.root.status["market_result"] = {
            "round": int(chosen_round),
            "decision": my_decision,
            "partner_decision": partner_decision,
            "entrants": entrants,
            "reward": payoff,
        }
        self.root.status["market_result_recorded"] = True

    def _ensure_coordination_results(self):
        self.root.status.setdefault("co_results", {})
        co_decisions = self.root.status.get("co_decisions", {})
        if not co_decisions:
            return

        for block, trials in co_decisions.items():
            for trial, d in trials.items():
                if trial in self.root.status["co_results"].get(block, {}):
                    continue
                my_decision = d.get("decision", "A")
                partner_decision = random.choice(["A", "B"])
                coordinated = my_decision == partner_decision
                payoff = COORDINATION_SUCCESS if coordinated else 0
                self.root.status["co_results"].setdefault(block, {})
                self.root.status["co_results"][block][trial] = {
                    "my_decision": my_decision,
                    "partner_decision": partner_decision,
                    "coordinated": coordinated,
                    "payoff": payoff,
                    "prediction": int(d.get("prediction", 50)),
                }

    def _append_coordination_result(self):
        if self.root.status.get("coordination_result_recorded"):
            return

        self._ensure_coordination_results()
        co_results = self.root.status.get("co_results", {})
        if not co_results:
            return

        flat = []
        for block, trials in co_results.items():
            for trial, result in trials.items():
                flat.append((int(block), int(trial), result))

        if not flat:
            return

        chosen_block, chosen_trial, selected = random.choice(flat)
        my_decision = selected.get("my_decision", "A")
        partner_decision = selected.get("partner_decision", "A")
        payoff = int(selected.get("payoff", 0))
        partner_payoff = int(selected.get("partner_payoff", 0))
        if "role" in selected and selected["role"]:
            role = self._normalize_coordination_role(selected["role"])
        else:
            role = self._coordination_role_for_block(chosen_block)
        role_label = f"Hráč {role}"
        partner_ordinals = {
            1: "prvním",
            2: "druhým",
            3: "třetím",
        }
        partner_label = partner_ordinals.get(chosen_block, f"{chosen_block}.")

        result_text = coordinationResultText.format(
            chosen_trial,
            partner_label,
            role_label,
            my_decision,
            partner_decision,
            payoff,
            partner_payoff,
        )

        reward_so_far = self.root.status.get("reward", 0)
        if not isinstance(reward_so_far, (int, float)):
            reward_so_far = 0
        self.root.status["reward"] = reward_so_far + payoff

        results = self.root.status.get("results")
        if not isinstance(results, list):
            results = []
        results.append(result_text)
        self.root.status["results"] = results

        self.root.status["coordination_result"] = {
            "round": chosen_block,
            "trial": chosen_trial,
            "role": role,
            "partner": partner_label,
            "my_decision": my_decision,
            "partner_decision": partner_decision,
            "reward": payoff,
            "partner_reward": partner_payoff,
        }
        self.root.status["coordination_result_recorded"] = True

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
            decision_other = random.choice(["in", "out"])
            quiz_other = random.randint(0, 5)
            me_part = f"market:{block},{decision_self},{quiz_self},{decision_other},{quiz_other}"
        else:
            me_part = "market:1,in,3,out,2"

        # Trust
        if self._has_trust_data():
            decisions = self.root.status.get("trust_decisions", {})
            if decisions:
                chosen_round = random.choice(list(decisions.keys()))
                d = decisions[chosen_round]
                sentA = d.get("sentA", TRUST_ENDOWMENT // 2)
                sentB = d.get("sentB", TRUST_ENDOWMENT // 2)
                trust_part = f"trust:{chosen_round},{sentA},{sentB}"
            else:
                trust_part = f"trust:1,{TRUST_ENDOWMENT//2},{TRUST_ENDOWMENT//2}"
        else:
            trust_part = f"trust:1,{TRUST_ENDOWMENT//2},{TRUST_ENDOWMENT//2}"

        return f"{co_part}|{me_part}|{trust_part}"

    def processResponse(self, response):
        if response == "ok":
            self._append_market_result()
            self._append_coordination_result()
            return

        # Parse format: coordination:<round>,<trial>,<self>,<other>|market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>|trust:<round>,<sentA>,<sentB>
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
                    payoff = COORDINATION_SUCCESS if co_self == co_other else 0
                    partner_label = f"{round_idx}."
                    role = self._coordination_role_for_block(round_idx)
                    role_label = f"Hráč {role}"
                    result_text = coordinationResultText.format(
                        trial_idx, partner_label, role_label, co_self, co_other, payoff, 0
                    )
                    results.append(result_text)
                    self.root.status["coordination_result"] = {
                        "round": round_idx,
                        "trial": trial_idx,
                        "role": role,
                        "my_decision": co_self,
                        "partner_decision": co_other,
                        "reward": payoff,
                    }
                    reward_so_far += payoff

            elif section.startswith("market:"):
                # market:<round>,<decision_self>,<quiz_self>,<decision_other>,<quiz_other>
                _, data = section.split(":", 1)
                parts = data.split(",")
                if len(parts) == 5:
                    round_idx = int(parts[0])
                    decision_self = parts[1].strip().lower()
                    quiz_self = int(parts[2])
                    decision_other = parts[3].strip().lower()
                    quiz_other = int(parts[4])

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
                            payoff = random.choice([MARKET_WIN, MARKET_LOSS])
                        result_text = marketResultText.format(round_idx, self_text, other_text, payoff)
                        result_text += " " + marketResultBothEnterText.format(quiz_self, quiz_other)
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
                        "reward": payoff,
                    }
                    reward_so_far += payoff

            elif section.startswith("trust:"):
                # trust:<round>,<sentA>,<sentB>
                _, data = section.split(":", 1)
                parts = data.split(",")
                if len(parts) == 3:
                    round_idx = int(parts[0])
                    sentA = int(parts[1])
                    sentB = int(parts[2])
                    # Assume role A for participant
                    reward = TRUST_ENDOWMENT - sentA + sentB
                    result_text = trustResultTextA.format(
                        sentA,
                        sentA * 3,
                        TRUST_ENDOWMENT + sentA * 3,
                        sentB,
                        TRUST_ENDOWMENT - sentA + sentB,
                        TRUST_ENDOWMENT + sentA * 3 - sentB,
                    )
                    results.append(result_text)
                    self.root.status["trust_result"] = {
                        "round": round_idx,
                        "sentA": sentA,
                        "sentB": sentB,
                        "reward": reward,
                    }
                    reward_so_far += reward

        self.root.status["results"] = results
        self.root.status["reward"] = reward_so_far

    def write(self, response):
        self.file.write("Final Results\n")
        if response == "ok":
            self.file.write(self.id + "\tok\n\n")
            return
        # Write each section on a new line for readability
        self.file.write(self.id + "\t" + response.replace("|", "\n\t") + "\n\n")




GamesIntro = (InstructionsFrame, {"text": games, "proceed": True, "height": "auto"})