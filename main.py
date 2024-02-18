from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from collections import defaultdict

from modules import Renderer
from modules import ObjectController

from modules.Piano import PianoVisualiser
from modules.Shapes import *
from modules.Notes import *

from modules.Midi import MidiParser

import time

def main():
    render_Manager = Renderer.Scene("Piano Testing")
    piano_Visualiser = PianoVisualiser()

    objManager = ObjectController.ObjectManager()
    objManager.populate(0, piano_Visualiser.draw_keys)

    print(f"Successfully populated the scene with {len(objManager.objects)}")

    render_Manager.fill_scene(objManager.objects)
    render_Manager.run([[piano_Visualiser.play_midi_thread, piano_Visualiser]])


if __name__ == "__main__":
    main()