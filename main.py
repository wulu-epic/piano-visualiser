from os import environ
import time
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from modules import Renderer
from modules import ObjectController

from modules.Piano import PianoVisualiser
from modules.Shapes import *

from modules.Midi import MidiParser

def piano_thread(piano_Visualiser):
    midParser = MidiParser()
    midParser.deserialize_midi("C:/Users/Martin/Documents/MIDI Files/Ballade_No._1_Opus_23_in_G_Minor.mid")

    for i in range(1, 6):
        shape : Square = piano_Visualiser.get_shape_by_key(f"C{i}")
        shape.colour = (0,255,0)
        time.sleep(.25)

def main():
    render_Manager = Renderer.Scene("Piano Testing")
    piano_Visualiser = PianoVisualiser()

    objManager = ObjectController.ObjectManager()
    objManager.populate(0, piano_Visualiser.draw_keys)
    
    print(f"Successfully populated the scene with {len(objManager.objects)}")

    render_Manager.fill_scene(objManager.objects)
    render_Manager.run([[piano_thread, piano_Visualiser]])


if __name__ == "__main__":
    main()