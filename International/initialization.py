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
        # Name: (Name, File, (x, y), True/False,(r,g,b)) <- (Name, Position, Colour)
        "Map" : ("Map", "Images/test_map.png", (0, 0), (0, 0, 0)),
        "Ride" : ("Map", "Images/test_ride.png", (454, 647), (159, 197, 232)),
    },

    'simulation' : {
        'interval' : 10, # One simulation hour is 10 seconds
        'startHour' : 10, # Start clock at 10:00 AM
        'endHour' : 21 # End clock at 9:00 PM
    },

    'audio' : {
        'bgm' : 'Audio/BGM.mp3',
        'click' : 'Audio/ClickSFX.mp3',
        'pause' : 'Audio/PauseSFX.mp3',
        'restart' : 'Audio/RestartSFX.mp3',
        'exit' : 'Audio/ExitSFX.mp3'
    }
}