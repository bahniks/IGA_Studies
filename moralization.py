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

from intros import Initial, Intro, Ending
from demo import Demographics
from comments import Comments
from login import Login
from fires import (
    FiresIntro1, FiresIntro2, FiresRules,
    FiresTutorialBucket, FiresTutorialSprinkler, FiresTutorialLayout,
    FiresUnderstanding, FiresRoundIntro, FiresQuestionnaire, ResultGame,
)
from Tutorial_fire import FireTutorialGame
from Tutorial_sprinkler import SprinklerTutorialGame
from Tutorial_layout import LayoutTutorialGame
from experiment_game import ExperimentGame



frames = [        
        Login,
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
        Ending,
         ]

#frames = [Login, Videos2]

if __name__ == "__main__":
    try:
        print("Starting game...")
        gui = GUI(frames, load = os.path.exists("temp.json"))
        print("GUI session finished")
        print("Game completed")
    except Exception as e:
        print(f"Error during game execution: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
    finally:
        # Ensure log file is closed properly
        if log_file and not log_file.closed:
            sys.stdout.flush()
            sys.stderr.flush()
            log_file.close()
