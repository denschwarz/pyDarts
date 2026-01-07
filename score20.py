from Player import Player
from Game import Game
from Turn import Turn
import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def dart_score(inp: str) -> int:
    inp = inp.strip().lower()
    if inp not in ["s","d","t", "0"]:
        raise ValueError("Score must be s, d, or t")
    if inp == "s":
        return 1, "s"
    elif inp == "d":
        return 2, "d"
    elif inp == "t":
        return 3, "t"
    else:
        return 0, "0"

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
    start_score = 0
    names = input("Spielernamen (kommagetrennt): ").split(",")
    N_rounds_max = int(input("Anzahl der Runden: "))
    players = [Player(name.strip(), start_score=start_score) for name in names]

    game = Game(players, mode="score20")
    game.set_max_rounds(N_rounds_max)
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

                this_turn.add_throw_20s(score_value, score_string)
                if this_turn.done:
                    break
                i_throw += 1

            if correction_previous_turn:
                game.previous_player()
                continue

            player.add_turn(this_turn, subtract_from_score=False)
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
