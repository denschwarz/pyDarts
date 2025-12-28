from Player import Player
from Game import Game
from Turn import Turn
import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def dart_score(inp: str) -> int:
    inp = inp.strip().lower()
    # bullseye handling (optional)
    if inp in ("sb", "bull", "25"):
        return 25, "sb"
    if inp in ("db", "dbull", "bullseye", "50"):
        return 50, "db"
    multiplier = 1
    multiplier_string = ""
    if inp.startswith("d"):
        multiplier_string = "d"
        multiplier = 2
        inp = inp[1:]
    elif inp.startswith("t"):
        multiplier_string = "t"
        multiplier = 3
        inp = inp[1:]
    value = int(inp)
    if not 0 <= value <= 20:
        raise ValueError("Dart number must be between 0 and 20 or sb, bull, 25, db, dbull, bullseye, 50")
    return multiplier*value, f"{multiplier_string}{value}"

def get_valid_score(message_string):
    while True:
        user_input = input(message_string)
        if user_input == "c":
            return -10, "correct"
        try:
            result, result_string = dart_score(user_input)
        except ValueError as e:
            print(f"Invalid input: {e}. Try again.")
        else:
            return result, result_string

def get_yes_no(message_string):
    while True:
        user_input = input(message_string)
        if user_input in ["y", "n"]:
            return user_input
        print("Must answer y or n")   

def main():
    start_score = int(input("Start Score: "))
    names = input("Spielernamen (kommagetrennt): ").split(",")
    players = [Player(name.strip(), start_score=start_score) for name in names]

    game = Game(players)
    correction_previous_turn = False
    while not game.is_finished():
        is_first_turn = True
        while not game.leg_is_finished():
            clear_screen()
            game.print_score_table()

            player = game.current_player()

            if correction_previous_turn:
                player.delete_last_turn()
            
            game.print_turn_header(correction_previous_turn, is_first_turn)
            this_turn = Turn(current_score=player.current_score)
            i_throw = 0
            while i_throw < 3:
                score_value, score_string  = get_valid_score(f"Pfeil {i_throw+1}: ")
                # check for correction mode
                if score_value == -10 and i_throw == 0: # if c is typed on first throw, correct previous turn
                    correction_previous_turn = True
                    break
                elif score_value == -10 and i_throw > 0: # if c is typed on 2nd or 3rd throw, go back one throw
                    this_turn.remove_throw()
                    i_throw -= 1
                    continue
                else:
                    correction_previous_turn = False

                this_turn.add_throw(score_value, score_string)
                if this_turn.done:
                    break
                i_throw += 1

            if correction_previous_turn:
                game.previous_player()
                continue

            player.add_turn(this_turn)
            game.next_player()
            is_first_turn = False

        game.declare_winner()
        game.end_leg()

        yes_no = get_yes_no("Noch ein leg (y,n)? ")
        if yes_no == "y":
            game.start_new_leg()
        else:
            clear_screen()
            game.print_statistics_table()
            game.end_game()

if __name__ == "__main__":
    main()


"""
TODOS
- Statistiken abspeichern.
"""
