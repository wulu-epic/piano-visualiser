import random, pygame, time
import threading, numpy

from threading import Thread
from queue import Queue
from collections import defaultdict

from modules.Shapes import *
from modules.PianoObjects import *
from modules.Output import *
from modules.ObjectController import ObjectManager

from modules.Midi import MidiParser
from modules.Midi import MidiSynthesiser

class PianoVisualiser:
    def __init__(self, objManager : ObjectManager, renderManager ):
        """
        Initialize the PianoRoll class with the given parameters.
        @param objManager: ObjectManager - The object manager for the piano roll.
        @param renderManager - The render manager for the piano roll.
        @return None
        """
        
        self.screen_width = 1280
        self.screen_height = 720

        self.TOTAL_WHITE_KEYS = 56
        self.WIDTH_WHITE_KEY_SPACE = 22

        self.WHITE_KEY_COLOUR = (255, 255, 255)
        self.BLACK_KEY_COLOUR = (0, 0, 0)
        self.KEY_DOWN_COLOUR = (0, 255, 0)

        self.NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.NOTES_IN_OCTAVE = len(self.NOTES)
        self.NOTE_SCALE = 100

        self.TIME_SCALE = .999
        self.TIME_STEP = 0.001 # -> This requires tweaking (SOMETIMES) unfortunately

        self.time = 0.0

        self.white_key_width = self.screen_width / self.TOTAL_WHITE_KEYS
        self.white_key_height = (self.screen_height / 7) + 500

        self.keys = []
        self.notes_and_shapes = {}

        self.midi_synthesier = MidiSynthesiser()
        self.object_manager : ObjectManager = objManager
        self.render_manager  = renderManager

        self.visualisation_running = False
        self.note_fall = True
        self.playing_piece = False

        pygame.init()
        self.clock = pygame.time.Clock()
          
    def draw_keys(self):
        """
        Draw the keys for the piano interface, including white and black keys.
        @param self - the instance of the class
        @return The list of keys that have been drawn
        """
        key_space = 0

        for i in range(self.TOTAL_WHITE_KEYS):
            white_key = Square(pygame.Vector2(key_space, self.white_key_height), (self.WIDTH_WHITE_KEY_SPACE, 120), self.WHITE_KEY_COLOUR)
            self.keys.append(white_key)

            if i % 7 != 2 and i % 7 != 6:
                black_key = Square(pygame.Vector2(key_space + (self.white_key_width - self.WIDTH_WHITE_KEY_SPACE / 2), self.white_key_height), (self.WIDTH_WHITE_KEY_SPACE / 2, 80), self.BLACK_KEY_COLOUR)
                self.keys.append(black_key)

            key_space += self.white_key_width

        self.assign_key_names()
        return self.keys

    def assign_key_names(self):
        """
        Assign key names to the keys based on their position in the list of keys.
        @param self - the object instance
        @return None
        """
        for i, key in enumerate(self.keys):
            octave = (i // self.NOTES_IN_OCTAVE) 
            note_index = i % self.NOTES_IN_OCTAVE

            note = self.NOTES[note_index]
            if note in ['C#', 'D#', 'F#', 'G#', 'A#']:
                key_name = f"{note}{octave}"
            else:
                key_name = f"{note}{octave}"

            self.notes_and_shapes[key_name] = key

    def get_shape_by_key(self, key):
        """
        Retrieve a shape from the notes and shapes dictionary based on the provided key.
        @param self - the object instance
        @param key - the key to look up in the notes and shapes dictionary
        @return The shape corresponding to the key, or None if the key is not found.
        """
        return self.notes_and_shapes.get(key, None)
    
    def press_note(self, note_object : N_Note, midParser : MidiParser):
        """
        Press a note on the synthesizer and update the corresponding shape on the interface.
        @param note_object: N_Note - The note object to be played.
        @param midParser: MidiParser - The MIDI parser object.
        @return None.
        """
        self.midi_synthesier.play_note(note_object.pitch, note_object.velocity)

        key_note = midParser.midi_note_number_to_name(note_object.pitch)
        shape : Shape = self.get_shape_by_key(key_note)
        if not shape:
            error(f'Failed to get the shape for the pitch: {note_object.pitch} ({key_note})')
            return
        
        shape.colour = self.KEY_DOWN_COLOUR 

    def lift_note(self, note_object : N_Note, midParser : MidiParser) -> None:
        """
        Lift a note by stopping the note on the MIDI synthesizer, retrieving the key note, and resetting the shape's color.
        @param note_object - The note object to be lifted
        @param midParser - The MIDI parser object
        @return None
        """
        self.midi_synthesier.stop_note(note_object.pitch, note_object.velocity)

        key_note = midParser.midi_note_number_to_name(note_object.pitch)    
        shape : Shape = self.get_shape_by_key(key_note)
        if not shape:
            error(f'Failed to get the shape for {note_object.pitch}')
            return
    
        shape.colour = shape.original_colour

    def split_note_array_by_instruments(self, note_array: list[N_Note]) -> dict:
        """
        Split a list of notes into separate lists based on the instrument index of each note.
        @param note_array - a list of N_Note objects
        @return a dictionary where keys are instrument indices and values are lists of notes
        """
        result = {}
        for note in note_array:
            if note.instrument_index not in result:
                result[note.instrument_index] = []
            
            result[note.instrument_index].append(note)

        return result
    
    def get_pedal_note_amount(self, note_array):
        """
        Calculate the number of notes in an array that have the pedal attribute set to True.
        @param self - the object instance
        @param note_array - an array of notes
        @return the number of notes with the pedal attribute set to True
        """
        n = 0
        for note in note_array:
            if note.pedal:
                n += 1
        return n
    
    def get_pedal_note(self, note_array):
        """
        Retrieve the index and note of the first pedal note in a given array of notes.
        @param self - the object instance
        @param note_array - an array of notes
        @return a tuple containing the index and the note of the first pedal note
        """
        for index, note in enumerate(note_array):
            if note.pedal:
                return index, note
    
    def press_note_array(self, note_array : list, end_duration : float, start_duration : float, midParser : MidiParser) -> None:
        """
        Press notes in the note array with a specified duration and using a MidiParser.
        @param note_array - list of notes to be pressed
        @param end_duration - the end duration of the note
        @param start_duration - the start duration of the note
        @param midParser - the MidiParser object
        @return None
        """
        for note in note_array:
            self.press_note(note, midParser)
        
        scaled_length = ((end_duration - start_duration) * self.TIME_SCALE / len(note_array))
        time.sleep(scaled_length) 

        for note in note_array:
            self.lift_note(note, midParser) 
    
    def do_note_array(self, note_array : list, end_duration : float, start_duration : float, midParser : MidiParser) -> None:
        """
        Define a method to process a note array with specified durations and a MIDI parser.
        @param note_array: list - The array of notes to process.
        @param end_duration: float - The end duration of the notes.
        @param start_duration: float - The start duration of the notes.
        @param midParser: MidiParser - The MIDI parser object.
        @return None
        """
        if end_duration == 0:
            return
        
        if len(note_array) != 1:
            note_array_by_instruments : dict = self.split_note_array_by_instruments(note_array)
            for instrument_index, note_arrays in note_array_by_instruments.items():
                Thread(target=self.press_note_array, args=(note_arrays, end_duration, start_duration, midParser, ), daemon=True).start()
                
                if self.note_fall:
                    Thread(target=self.fall_note_array, args=(note_arrays, midParser, ), daemon=True).start()
        else:
            Thread(target=self.press_note_array, args=(note_array, end_duration, start_duration, midParser, ), daemon=True).start()
            
            if self.note_fall:
                Thread(target=self.fall_note_array, args=(note_array, midParser, ), daemon=True).start()
    
    # object animations, will make into a own class later on (🙏🙏)
    def object_up_animate(self, object: Shape, duration: float):
        """
        Animate an object moving upwards on the screen.
        @param object - The object to animate
        @param duration - The duration of the animation
        @return None
        """

        initial_y_position = 600
        CONST_SPEED = 200

        object = Square(object.position + Vector2(0, initial_y_position), object.size, (255,0,255))
        speed = -(CONST_SPEED)

        elapsed_time = 0
        time_step = 0.01
        object.size = (object.size[0], duration * self.NOTE_SCALE)
        
        object = self.render_manager.insert_object(object)
        duration_scaler = duration < 1.5 and 20 or 2
        while elapsed_time <= (duration * duration_scaler):
            elapsed_time += time_step
            time.sleep(time_step)

            delta_y = speed * elapsed_time  
            new_y = initial_y_position + delta_y

            new_position = Vector2(object.position.x, new_y)
            object.position = new_position

        self.render_manager.remove_object(object)

    def fall_note_array(self, note_array, midParser):
        """
        Animate falling objects based on the notes in the note array.
        @param note_array - Array of notes to animate
        @param midParser - MIDI parser object
        @return None
        """
        
        for note in note_array:
            note_duration = note.end - note.start

            note_keyname = midParser.midi_note_number_to_name(note.pitch)
            if note_keyname:
                note_shape = self.get_shape_by_key(note_keyname)
                if note_shape:
                    Thread(target = self.object_up_animate, args=(note_shape, note_duration, ), daemon=True).start()

    def stop_midi(self) -> None:
        """
        Stop the MIDI playback if a piece is currently being played.
        @return None
        """
        if self.playing_piece:
            self.playing_piece = False

    def play_midi(self, midParser: MidiParser, mid_parser_result: dict) -> None:
        """
        Play a MIDI file using a MIDI parser and the parsed MIDI data.
        @param midParser - An instance of the MidiParser class
        @param mid_parser_result - A dictionary containing the parsed MIDI data
        @return None
        """
        if not self.midi_synthesier.open_port():
            error('Failed to open a port! Audio will not work!')
            return
        else:
            output('Opened a midi output port successfully!')

        midi_length = midParser.get_midi_length(mid_parser_result)
        warn(f'This piece is: ~{midi_length // 60} minutes long.')

        result_clone = mid_parser_result.copy()
        notes_by_timestamp = self.group_notes_by_timestamp(result_clone)

        start_time = time.time()
        self.playing_piece = True

        self.play_notes_in_time(notes_by_timestamp, midi_length, midParser, start_time)
        self.playing_piece = False

    def group_notes_by_timestamp(self, result_clone):
        """
        Group notes by timestamp from a cloned result.
        @param self - the object instance
        @param result_clone - the cloned result to group notes from
        @return notes_by_timestamp - a dictionary where notes are grouped by timestamp
        """
        notes_by_timestamp = defaultdict(list)
        for timestamp, note_array in result_clone.items():
            for note in note_array:
                notes_by_timestamp[timestamp].append(note)
        return notes_by_timestamp

    def play_notes_in_time(self, notes_by_timestamp, midi_length, midParser, start_time):
        """
        Play notes in time based on the given notes by timestamp, MIDI length, MIDI parser, and start time.
        @param notes_by_timestamp - A dictionary mapping timestamps to notes
        @param midi_length - The length of the MIDI file
        @param midParser - The MIDI parser object
        @param start_time - The starting time for playing notes
        @return None
        """
        for i in numpy.arange(0, midi_length, self.TIME_STEP):
            self.time = i
            notes_to_play = self.get_notes_to_play(notes_by_timestamp, i)

            longest_note, smallest_note = midParser.get_note_range(notes_to_play)
            self.do_note_array(notes_to_play, longest_note, smallest_note, midParser)

            self.wait_for_next_beat(i, start_time)

            if not self.playing_piece:
                break

            self.clock.tick()

    def get_notes_to_play(self, notes_by_timestamp, current_time):
        """
        Given a dictionary of notes by timestamp and the current time, determine which notes should be played based on a time step.
        @param notes_by_timestamp - Dictionary of notes with timestamps
        @param current_time - The current time
        @return List of notes to play
        """
        notes_to_play = []
        for timestamp in list(notes_by_timestamp.keys()):
            if (timestamp - current_time) < self.TIME_STEP:
                notes_to_play = (notes_by_timestamp[timestamp])
                del notes_by_timestamp[timestamp]
        return notes_to_play

    def wait_for_next_beat(self, current_time, start_time):
        """
        Wait for the next beat based on the current time and start time.
        @param current_time - the current time
        @param start_time - the start time
        @return None
        """
        elapsed_time = time.time() - start_time
        beat_time = (current_time * self.TIME_SCALE)
        time_to_wait = beat_time - elapsed_time
        if time_to_wait > 0:
            pygame.time.wait(int(time_to_wait * 1000))

    def play_midi_thread(self, pianoVisualiser):
        """
        Play a MIDI file in a separate thread and update the piano visualizer accordingly.
        @param self - the instance of the class
        @param pianoVisualiser - the piano visualizer object
        @return None
        """
        pianoVisualiser.visualisation_running = True
        piece = 'C:/Users/Martin/Documents/MIDI Files/Hungarian_Rhapsody_No.2_Friska_-_Franz_Liszt.mid'
        #self.render_manager.scene_objects.append(ImageRect(((1280/2) - 500, 720/2), "C:/Users/Martin/Pictures/Screenshots/Screenshot 2024-03-06 161319.png"))      

        midParser = MidiParser()
        result = midParser.deserialize_midi(piece)
        output(f'Now playing the selected file: {piece}')

        self.play_midi(midParser, result)
        output('Finished playing the midi file!')
