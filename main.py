from os import environ
from multiprocessing import Queue, Process

from themeParkClass import ParkWindow
from rideClass import RideWindow

from bhavsCode import combinedDict

def start_theme_park(caption, size, pos, queue_in, queue_out, images):
    park_window = ParkWindow(caption, size, pos, queue_in, queue_out, images)
    park_window.run()

def start_ride_window(caption, size, pos, queue_in, queue_out, logs):
    ride_window = RideWindow(caption, size, pos, queue_in, queue_out, logs)
    ride_window.run()
    


if __name__ == "__main__":

    # Image class
    images = {

        "Map" : ("Map", (0, 0)),

        "Lazy River" : ("Lazy River", (454, 647)),

        "Nebula Spinner" : ("Nebula Spinner", (459, 8)),

        "Pixel Arcade" : ("Pixel Arcade", (25, 532)),

        "Rocket Slingshot" : ("Rocket Slingshot", (189, 8)),

        "Splashing Mountain" : ("Splashing Mountain", (478, 180)),

        "Titan Coaster" : ("Titan Coaster", (17, 275)),

        "Hydration Station" : ("Hydration Station", (450, 524)),

        "Pixel Popcorn" : ("Pixel Popcorn", (253, 180)),

        "Quantum Cafe" : ("Quantum Cafe", (176, 673)),

        "The Sugar Shack" : ("The Sugar Shack", (244, 523))

    }

    # Create IN/OUT queues for Theme Park
    main_to_park = Queue()
    park_to_main = Queue()

    # Create IN/OUT queues for Station
    main_to_station = Queue()
    station_to_main = Queue()

    # Create Main Window with communcation_queue
    theme_park = Process(
        target=start_theme_park,
        args=("Theme Park", (800, 900), (10 + 250, 45), main_to_park, park_to_main, images)
    )

    # Create Second Information Window with communcation_queue
    ride_park = Process(
        target=start_ride_window,
        args=("Station", (400, 900), (820 + 250, 45), main_to_station, station_to_main, combinedDict)
    )

    ride_park.start()
    theme_park.start()

    try:
        while theme_park.is_alive(): # Check if the main window is currently open
            
            # Route messages FROM Park TO Station
            try:
                msg = park_to_main.get_nowait() # Grabs the most recent message in queue
                main_to_station.put(msg)
            except:
                pass
    
            # Route messages FROM Station TO Park
            try:
                msg = station_to_main.get_nowait() # Grabs the most recent message in queue
                main_to_park.put(msg)
            except:
                pass

        theme_park.join()

    except KeyboardInterrupt:
        pass

    finally:
        print("\nEnding Program...")
        
        print("\nClosing Station Window Process...")
        ride_park.terminate()
        print("\nStation Window is closed.")

        print("\nClosing Main Window Process...")
        theme_park.terminate()
        print("\nMain Window is closed.")