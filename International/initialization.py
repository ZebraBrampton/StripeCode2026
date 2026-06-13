# This program will have the main variables for our windows and logics

config = {
    'parkWindow' : {
        'caption' : 'Park',
        'size' : (800, 900),
        'pos' : (260, 25),
    },

    'rideWindow' : {
        'caption' : 'Ride',
        'size' : (400, 900),
        'pos' : (1070, 25)
    },
    
    'images' : {
        # Name: (Name, File, (x, y), (x, y) ,(r,g,b)) <- (Name, Position, Size, Colour)
        "Map" : ("Map", "International/Images/test_map.png", (0, 0), (800, 900), (0, 0, 0)),
        "Ride" : ("Map", "International/Images/test_ride.png", (454, 647), (150, 163), (159, 197, 232)),
    },

    'simulation' : {
        'realTimeInterval' : 10, # One simulation hour is 10 seconds
        'startHour' : 10, # Start clock at 10:00 AM
        'endHour' : 21 # End clock at 9:00 PM
    },

    'audio' : {
        'bgm' : 'International/Audio/BGM.mp3',
        'click' : 'International/Audio/ClickSFX.mp3',
        'pause' : 'International/Audio/PauseSFX.mp3',
        'restart' : 'International/Audio/RestartSFX.mp3',
        'exit' : 'International/Audio/ExitSFX.mp3'
    }
}