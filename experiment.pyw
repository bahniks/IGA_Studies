#! python3

import sys
import os

# Ensure we're in the correct directory regardless of how the script is executed
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the Stuff directory to Python path for imports
stuff_path = os.path.join(script_dir, "Stuff")
if stuff_path not in sys.path:
    sys.path.insert(0, stuff_path)

# Redirect stdout and stderr to log file for debugging when run from double-click
log_file_path = os.path.join(script_dir, "log.txt")
log_file = None
try:
    log_file = open(log_file_path, 'w', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file
    print(f"Script directory: {script_dir}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
except Exception as e:
    # If logging fails, continue without it
    log_file = None

from Stuff.gui import GUI

from Stuff.intros import Initial, Intro, Ending
from Stuff.demo import Demographics
from Stuff.comments import Comments
from Stuff.login import Login
from Stuff.questionnaire import (
    QuestInstructions,
    QuestInstructions2,
    Numeracy,
    Narcissism,
    SalesProneness,
    TransactionValue,
)
from Stuff.groups import InstructionsGroups, Groups
from Stuff.games import GamesIntro, WaitResults
from Stuff.coordination import IntroCoordination, InstructionsCoordination, CoordinationGame, WaitCoordination, CoordinationRoundResult, NextRoundInfo
from Stuff.marketentry import IntroMarketEntry, InstructionsMarketEntry, MarketEntryQuiz, MarketEntryGame
from Stuff.trustgame import WaitGroups, IntroTrust, InstructionsTrust, Trust
from Stuff.fires import (
    FiresIntro1,
    FiresIntro2,
    FiresRules,
    FiresTutorialBucket,
    FiresTutorialSprinkler,
    FiresTutorialLayout,
    FiresUnderstanding,
    FiresRoundIntro,
    ResultGame,
    FiresQuestionnaire,
)
from Stuff.Tutorial_fire import FireTutorialGame
from Stuff.Tutorial_sprinkler import SprinklerTutorialGame
from Stuff.Tutorial_layout import LayoutTutorialGame
from Stuff.experiment_game import ExperimentGame
from Stuff.products import ProductsIntro1, ProductsIntro2, ProductsIntroUnderstanding, ProductsIntro4, Choices, ProductsIntro5, ProductsEnd1
from Stuff.constants import COORDINATION_ROUNDS, MARKET_ROUNDS, TRUST_ROUNDS



frames = [Initial,
          Login,                    
          Intro,
          GamesIntro,
          InstructionsGroups,
          Groups,
          IntroCoordination,
          InstructionsCoordination,
	      *([CoordinationGame, WaitCoordination, CoordinationRoundResult, CoordinationGame, NextRoundInfo] * (COORDINATION_ROUNDS - 1)),
          CoordinationGame, WaitCoordination, CoordinationRoundResult, CoordinationGame,
		  IntroMarketEntry,
		  InstructionsMarketEntry,
		  *([MarketEntryQuiz, MarketEntryGame] * MARKET_ROUNDS),	  
          WaitGroups,
          IntroTrust,
          InstructionsTrust,
          *([Trust] * TRUST_ROUNDS),
        FiresIntro1,
        FiresIntro2,
        FiresRules,
        FiresTutorialBucket,
        FireTutorialGame,
        FiresTutorialSprinkler,
        SprinklerTutorialGame,
        FiresTutorialLayout,
        LayoutTutorialGame,
        FiresUnderstanding,
        FiresRoundIntro,
        ExperimentGame,
        ResultGame,
        FiresQuestionnaire,
        FiresRoundIntro,
        ExperimentGame,
        ResultGame,
        FiresQuestionnaire,
        ProductsIntro1,
        ProductsIntro2,
        ProductsIntroUnderstanding,
        ProductsIntro4,        
        Choices,       
        ProductsEnd1,
        QuestInstructions,
        Numeracy,
        Narcissism,
        ProductsIntro5,
        Choices,
        QuestInstructions2,
        SalesProneness, 
        TransactionValue, 
        Demographics,
        Comments,
          WaitResults,
          Ending
         ]



if __name__ == "__main__":
    try:
        print("Starting experiment...")
        gui = GUI(frames, load = os.path.exists("temp.json"))
        print("GUI session finished")
        print("Experiment completed")
    except Exception as e:
        print(f"Error during experiment execution: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
    finally:
        # Ensure log file is closed properly
        if log_file and not log_file.closed:
            sys.stdout.flush()
            sys.stderr.flush()
            log_file.close()