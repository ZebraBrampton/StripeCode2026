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
        # Name: (Name, File, (x, y), (x, y), True/False, (r,g,b)) <- (Name, Filename, Position, Size, Outside, Colour)
        "Map" : ("Map", "International/Images/Map.png", (0, 0), (800, 900), False, (0, 0, 0)),
        "Lazy River" : ("Lazy River", "International/Images/Lazy River.png", (454, 647), (308, 217), True, (159, 197, 232)),
        "Nebula Spinner" : ("Nebula Spinner", "International/Images/Nebula Spinner.png", (459, 8), (152, 152), True, (249, 203, 156)),
        "Rocket Slingshot" : ("Rocket Slingshot", "International/Images/Rocket Slingshot.png", (189, 8), (150, 163), True, (255, 229, 153)),
        "Pixel Arcade" : ("Pixel Arcade", "International/Images/Pixel Arcade.png", (25, 532), (146, 160), False, (0, 255, 255)),
        "Splashing Mountain" : ("Splashing Mountain", "International/Images/Splashing Mountain.png", (478, 180), (308, 250), True, (147, 196, 125)),
        "Titan Coaster" : ("Titan Coaster", "International/Images/Titan Coaster.png", (17, 275), (312, 159), True, (139, 198, 252)),
        "Hydration Station" : ("Hydration Station", "International/Images/Hydration Station.png", (450, 524), (116, 117), False, (164, 194, 244)),
        "Pixel Popcorn" : ("Pixel Popcorn", "International/Images/Pixel Popcorn.png", (253, 180), (88, 89), False, (230, 145, 56)),
        "Quantum Cafe" : ("Quantum Cafe", "International/Images/Quantum Cafe.png", (176, 673), (163, 163), False, (142, 124, 195)),
        "The Sugar Shack" : ("The Sugar Shack", "International/Images/The Sugar Shack.png", (244, 523), (107, 103), False, (233, 120, 93)),
        
        "Low Temp" : ("Low Temp", "International/Images/Low Temp.png", (11, 80), (57, 73), False, None),
        "Moderate Temp" : ("Moderate Temp", "International/Images/Moderate Temp.png", (0, 82), (69, 69), False, None),

        "Morning" : ("Morning", "International/Images/Morning.png", (15, 17), (54, 54), False, None),
        "Afternoon" : ("Afternoon", "International/Images/Afternoon.png", (13, 15), (58, 60), False, None),
        "Evening" : ("Evening", "International/Images/Evening.png", (5, 8), (69, 67), False, None),
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