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


from gui import GUI

from intros import Ending
from login import Login
from questionnaire import Narcissism
from games import GamesIntro, WaitResults
from groups import Groups, InstructionsGroups
from trustgame import IntroTrust, InstructionsTrust, Trust, WaitGroups
from coordination import IntroCoordination, InstructionsCoordination, CoordinationGame, WaitCoordination, CoordinationRoundResult, NextRoundInfo
from marketentry import IntroMarketEntry, InstructionsMarketEntry, MarketEntryQuiz, MarketEntryGame
from constants import TRUST_ROUNDS, COORDINATION_ROUNDS, MARKET_ROUNDS



frames = [Login,          
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
          Narcissism,
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