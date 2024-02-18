class Note:
    def __init__(self, time, velocity, note):
        self.time = time
        self.velocity = velocity
        self.note = note
        self.state = True

class Chord:
    def __init__(self, notes, time):
        self.notes = notes  # List of `Note` objects
        self.time = time
        self.state = True  

class Pedal:
    def __init__(self, value, time ):
        if not value == 64:
            print('This is not a valid pedal note')

        self.value = 64
        self.time = time
        self.state = True

