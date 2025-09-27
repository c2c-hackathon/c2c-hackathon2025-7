import logging
import queue
import threading
import time
import typing
from dataclasses import dataclass
import random

import library
from matrix_button_led_controller import MatrixButtonLEDController

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
USE_LED_HAT = True

@dataclass
class ButtonInfo:
    color: str
    sound: str
    matched: bool


class Game:
    def __init__(self, button_pad: MatrixButtonLEDController):
        self.button_pad = button_pad
        self.button_pad.assign_button_events(self.when_pressed, self.when_held, self.when_released)

        self.chosen_pair = []
        self.chosen_button = None
        self.waiting_for_pair = False
        self.matched = [False for i in range(16)]
        self.total = 0
        print(self.matched)

        self.buttons: typing.List[ButtonInfo] = []
        self.sounds: typing.List[str] = []
        self.colors: typing.List[str] = []
        self.speaker = library.speaker.Speaker()
        self.initialize_button_pad()
        self.started = False
        self.play_game = True
        self.queue = queue.Queue()

        self.button_pairs = [[None for i in range(2)] for i in range(8)]
        self.button_numbers = [i for i in range(0, 16)]
        for i in range(len(self.button_pairs)):
            for j in range(len(self.button_pairs[i])):
                self.button_pairs[i][j] = random.choice(self.button_numbers) + 1
                self.button_numbers.remove(self.button_pairs[i][j] - 1)
        self.randomize()
        print(self.button_pairs)

    @property
    def correct_sound(self):
        """The sound that is played when player gets a pair"""
        # OPTIONAL: change this to a different sound if you want
        return "correct_answer"

    @property
    def incorrect_sound(self):
        """The sound that is played when player makes an incorrect guess"""
        # OPTIONAL: change this to a different sound if you want
        return "incorrect"

    @property
    def end_of_game_sound(self):
        """The sound that is played when the game ends."""
        # OPTIONAL: change this to a different sound if you want
        return "end_of_game"

    def _background_logic_checker(self):
        while self.play_game:
            time.sleep(0.005)  # Prevents busy-waiting
            if self.queue.empty():
                continue
            button_number = self.queue.get()
            print(f"Handling button {button_number}")

            # Example logic: light up the button that was pressed with a constant color
            button = self.button_pad.get_button(button_number)

            for button_num_x in self.button_pairs:
                print(button_num_x)
                if button_number in button_num_x:
                    print(self.button_pairs.index(button_num_x))
                    print(self.colors)
                    self.button_pad.set_button_led_color(button, self.colors[self.button_pairs.index(button_num_x)])
                    self.speaker.play_preloaded_wav(self.sounds[self.button_pairs.index(button_num_x)], wait_until_done=True)

                    
                    break

            if self.matched[button_number - 1] or button == self.chosen_button:
                continue

            if self.waiting_for_pair:
                if button.pin.info.number in pair:
                    print("Matched!")
                    self.matched[button_number - 1] = True
                    self.matched[chosen_button_number - 1] = True
                    self.speaker.play_preloaded_wav("correct_answer", wait_until_done=True)
                    self.total += 1
                else:
                    print("No Match!")
                    self.button_pad.set_button_led_color(self.chosen_button, "black")
                    self.button_pad.set_button_led_color(button, "black")
                    self.speaker.play_preloaded_wav("incorrect", wait_until_done=True)
                self.waiting_for_pair = False

            else:
                
                self.chosen_button = button
                chosen_button_number = button.pin.info.number
                for pair in self.button_pairs:
                    if chosen_button_number in pair:
                        chosen_pair = pair
                        self.waiting_for_pair = True
                        break
            

            if self.total >= 8:
                print("You won.")
                self.speaker.play_preloaded_wav("end_of_game", wait_until_done=True)
                self.button_pad.clear_button_pad()
                break

            

    def when_pressed(self, button):
        # TODO: this is called when a button is pressed. Add what you need to here
        _logger.info(f"Button {button.pin.info.number} pressed")

        self.queue.put(button.pin.info.number)

    def when_held(self, button):
        # TODO: this is called when a button is held. Add what you need to here

        pass

    def when_released(self, button):
        # TODO: this is called when a button is released. Add what you need to here
        pass

    def initialize_button_pad(self):
        self.button_pad.clear_button_pad()
        # TODO: Set all buttons to a color, List of colors to choose from: https://github.com/waveform80/colorzero/blob/master/colorzero/tables.py#L315
        # sounds are available in the sounds directory
        self.sounds = [
            "thunder2",
            "fart_z",
            "baby_x",
            "slide_whistle_x",
            "arrow2",
            "phone_pay",
            "bloop_x",
            "car_horn_x",
        ]
        self.colors = [
            "blue",
            "green",
            "red",
            "orangered",
            "purple",
            "grey",
            "white",
            "yellow",
        ]
        # TODO: assign to buttons

    def randomize(self):



    def _start_game(self):
        self.thread = threading.Thread(target=self._background_logic_checker)
        self.thread.start()
        # TODO: play a sound to start the game
        self.started = True

    def play(self):
        self._start_game()
        try:
            input("Press Enter to exit the game...")
        except KeyboardInterrupt:
            print("Exiting game...")
        finally:
            self.play_game = False
            self.thread.join()
            self.button_pad.cleanup()


def _main():
    button_pad = MatrixButtonLEDController(
        scan_delay=0.020, pwm_freq=10000, display_pause=0.001, use_led_hat=USE_LED_HAT
    )
    game = Game(button_pad)
    game.play()


if __name__ == "__main__":
    _main()
