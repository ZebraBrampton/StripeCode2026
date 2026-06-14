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
        # Main Map
        "Map" : ("Map", "International/Images/Map.png", (0, 0), (800, 900), False, (0, 0, 0)),
        
        # 6 Rides Affected from Weather
        "Lazy River" : ("Lazy River", "International/Images/Lazy River.png", (454, 647), (308, 217), True, (159, 197, 232)),
        "Nebula Spinner" : ("Nebula Spinner", "International/Images/Nebula Spinner.png", (459, 8), (152, 152), True, (249, 203, 156)),
        "Pixel Arcade" : ("Pixel Arcade", "International/Images/Pixel Arcade.png", (25, 532), (146, 160), True, (0, 255, 255)),
        "Rocket Slingshot" : ("Rocket Slingshot", "International/Images/Rocket Slingshot.png", (189, 8), (150, 163), True, (255, 229, 153)),
        "Splashing Mountain" : ("Splashing Mountain", "International/Images/Splashing Mountain.png", (478, 180), (308, 250), True, (147, 196, 125)),
        "Titan Coaster" : ("Titan Coaster", "International/Images/Titan Coaster.png", (17, 275), (312, 159), True, (139, 198, 252)),

        # Unaffected places
        "Hydration Station" : ("Hydration Station", "International/Images/Hydration Station.png", (450, 524), (116, 117), False, (164, 194, 244)),
        "Pixel Popcorn" : ("Pixel Popcorn", "International/Images/Pixel Popcorn.png", (253, 180), (88, 89), False, (230, 145, 56)),
        "Quantum Cafe" : ("Quantum Cafe", "International/Images/Quantum Cafe.png", (176, 673), (163, 163), False, (142, 124, 195)),
        "The Sugar Shack" : ("The Sugar Shack", "International/Images/The Sugar Shack.png", (244, 523), (107, 103), False, (233, 120, 93)),

        # Icons for statistics
        "Low Temp" : ("Low Temp", "International/Images/Low Temp.png", (11, 80), (57, 73), False, None),
        "Moderate Temp" : ("Moderate Temp", "International/Images/Moderate Temp.png", (0, 82), (69, 69), False, None),
        "High Temp" : ("High Temp", "International/Images/Heavy Temp.png", (15, 82), (69, 69), False, None),

        "Low Wind" : ("Low Wind", "International/Images/Low Wind.png", (13, 157), (58, 58), False, None),
        "Moderate Wind" : ("Moderate Wind", "International/Images/Moderate Wind.png", (17, 157), (54, 54), False, None),
        "Heavy Wind" : ("Heavy Wind", "International/Images/Heavy Wind.png", (16, 160), (50, 50), False, None),

        "Low Rain" : ("Low Rain", "International/Images/Low Rain.png", (16, 216), (50, 50), False, None),
        "Moderate Rain" : ("Moderate Rain", "International/Images/Moderate Rain.png", (16, 216), (50, 50), False, None),
        "Heavy Rain" : ("Heavy Rain", "International/Images/Heavy Rain.png", (12, 211), (57, 57), False, None),

        "Morning" : ("Morning", "International/Images/Morning.png", (15, 17), (54, 54), False, None),
        "Afternoon" : ("Afternoon", "International/Images/Afternoon.png", (13, 15), (58, 60), False, None),
        "Evening" : ("Evening", "International/Images/Evening.png", (5, 8), (69, 67), False, None)
        },

    'simulation' : {
        'realTimeInterval' : 3, # One simulation hour is 10 seconds
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