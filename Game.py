import re

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def visible_len(text):
    return len(ANSI_RE.sub("", text))

def pad_cell(text, width, align=">"):
    vis = visible_len(text)
    pad = max(0, width - vis)

    if align == "<":
        return text + " " * pad
    else:
        return " " * pad + text


class Game:
    def __init__(self, players, mode="normal"):
        self.players = players
        self.current_player_index = 0
        self.finished = False
        self.start_player_index = 0
        self.last_player_score_string = ""
        self.mode = mode
        self.max_rounds = 1000

        # ANSI styles
        self.RESET = "\033[0m"
        self.BOLD = "\033[1m"
        self.GREEN = "\033[32m"
        self.CYAN = "\033[36m"
        self.RED = "\033[31m"

        # Markers
        self.START_MARK = "•"
        self.CURRENT_MARK = "◀"
        self.LEGSWON_MARK = "✖"

    def current_round(self):
        # Current round is defined by the least progressed player (and offset by 1 because rounds should start at 1)
        completed_rounds_per_player = [ len(p.throws) // 3 for p in self.players ]
        return min(completed_rounds_per_player) + 1 

    def set_max_rounds(self, N):
        self.max_rounds = N

    def current_player(self):
        return self.players[self.current_player_index]

    def next_player(self):
        last_player = self.players[self.current_player_index]
        self.last_player_score_string = f"[Last score: {last_player.name}, {sum(last_player.last_turn)}]"
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def previous_player(self):
        self.current_player_index = (self.current_player_index - 1) % len(self.players)

    def is_finished(self):
        return self.finished
    
    def end_game(self):
        self.finished = True

    def end_leg(self):
        for p in self.players:
            p.end_leg()

    def start_new_leg(self):
        self.start_player_index = (self.start_player_index + 1) % len(self.players)
        self.current_player_index = self.start_player_index
        for p in self.players:
            p.start_new_leg()

    def leg_is_finished(self):
        if self.mode == "normal":
            return any(p.current_score <= 0 for p in self.players)
        elif self.mode == "score20":
            return self.current_round() > self.max_rounds
    

    def declare_winner(self):
        if self.mode == "normal":
            for p in self.players:
                if p.current_score == 0:
                    print(f"\n🎯 Gewinner: {p.name}")
                    p.make_winner()
                else:
                    p.make_looser()
        elif self.mode == "score20":
            max_score = max(p.current_score for p in self.players)
            for p in self.players:
                if p.current_score == max_score:
                    print(f"\n🎯 Gewinner: {p.name}")
                    p.make_winner()
                else:
                    p.make_looser()

    def print_turn_header(self, correction_mode, first_turn):
        current_player = self.players[self.current_player_index]
        print(f"Bedienung")
        print(f"  c                    : Korrektur")
        if self.mode == "normal":
            print(f"  dX                   : Double X")
            print(f"  tX                   : Triple X")
            print(f"  sb/bull/25           : Bull")
            print(f"  db/dbull/bullseye/50 : Bullseye")
        elif self.mode == "score20":
            print(f"  s                    : Single hit")
            print(f"  d                    : Double hit")
            print(f"  t                    : Triple hit")
            print(f"  0                    : No hit")
        if first_turn:
            print("\n\n")
        else:
            print(f"                                       {self.last_player_score_string}")
            print("\n")
        if correction_mode:
            print(f" {self.BOLD}{self.RED}{current_player.name} (Korrektur){self.RESET}")
        else:
            print(f" {self.BOLD}{self.CYAN}{current_player.name}{self.RESET}")


    def print_score_table(self):
        if self.mode == "score20":
            print(f"Round {self.current_round()} of {self.max_rounds}")

        # column widths
        NAME_W = 15
        LEGS_W = 8
        SCORE_W = 14
        AVG_W = 15
        LEG_AVG_W = 15

        # box drawing characters
        TL, TR, BL, BR = "┌", "┐", "└", "┘"
        H, V = "─", "│"
        TM, MM, BM = "┬", "┼", "┴"

        def hline(left, mid, right):
            return (
                left
                + H * NAME_W + mid
                + H * LEGS_W + mid
                + H * SCORE_W + mid
                + H * AVG_W + mid
                + H * LEG_AVG_W
                + right
            )

        def cell(text, width, align="<"):
            return f"{text:{align}{width}}"

        # top border
        print(self.CYAN + hline(TL, TM, TR) + self.RESET)

        # header row
        print(
            self.CYAN + V + self.RESET
            + cell("", NAME_W) + self.CYAN + V + self.RESET
            + cell("Legs", LEGS_W, ">") + self.CYAN + V + self.RESET
            + cell("Score", SCORE_W, ">") + self.CYAN + V + self.RESET
            + cell("Total Avg", AVG_W, ">") + self.CYAN + V + self.RESET
            + cell("Leg Avg", LEG_AVG_W, ">") + self.CYAN + V + self.RESET
        )

        # header separator
        print(self.CYAN + hline("├", MM, "┤") + self.RESET)

        # player rows
        for idx, p in enumerate(self.players):
            start_mark = self.CYAN+" "+self.START_MARK+self.RESET if idx == self.start_player_index else "  "
            current_turn_mark = self.RED+" "+self.CURRENT_MARK+self.RESET if idx == self.current_player_index else "  "
            print(
                self.CYAN + V + self.RESET
                + pad_cell(p.name+start_mark, NAME_W, "<") + self.CYAN + V + self.RESET
                + cell(p.legs_won, LEGS_W, ">") + self.CYAN + V + self.RESET
                + self.BOLD + self.GREEN
                + cell(p.current_score, SCORE_W, ">")
                + self.RESET + self.CYAN + V + self.RESET
                + cell(f"{p.get_3dart_average_total():.2f}", AVG_W, ">") + self.CYAN + V + self.RESET
                + cell(f"{p.get_3dart_average_this_leg():.2f}", LEG_AVG_W, ">") + self.CYAN + V + self.RESET
                + current_turn_mark
            )

        # bottom border
        print(self.CYAN + hline(BL, BM, BR) + self.RESET)

    def print_statistics_table(self):
        ROW_W = 18
        COL_W = 12

        num_players = len(self.players)
        num_legs = max(len(p.leg_results) for p in self.players)

        # box drawing
        TL, TR, BL, BR = "┌", "┐", "└", "┘"
        H, V = "─", "│"
        TM, MM, BM = "┬", "┼", "┴"

        def hline(left, mid, right):
            return (
                left
                + H * ROW_W
                + mid
                + mid.join(H * COL_W for _ in range(num_players))
                + right
            )

        def is_win(result):
            return result.lower().startswith("w")

        # top
        print(self.CYAN + hline(TL, TM, TR) + self.RESET)

        # header
        print(
            self.CYAN + V + self.RESET
            + pad_cell("", ROW_W, "<")
            + "".join(
                self.CYAN + V + self.RESET
                + pad_cell(p.name, COL_W, ">")
                for p in self.players
            )
            + self.CYAN + V + self.RESET
        )

        # separator
        print(self.CYAN + hline("├", MM, "┤") + self.RESET)

        # legs won
        print(
            self.CYAN + V + self.RESET
            + pad_cell("Legs won", ROW_W, "<")
            + "".join(
                self.CYAN + V + self.RESET
                + pad_cell(str(sum(is_win(r) for r in p.leg_results)), COL_W, ">")
                for p in self.players
            )
            + self.CYAN + V + self.RESET
        )

        # total average
        print(
            self.CYAN + V + self.RESET
            + pad_cell("Total average", ROW_W, "<")
            + "".join(
                self.CYAN + V + self.RESET
                + pad_cell(f"{p.get_3dart_average_total():.2f}", COL_W, ">")
                for p in self.players
            )
            + self.CYAN + V + self.RESET
        )

        # per-leg rows
        for leg in range(num_legs):
            print(
                self.CYAN + V + self.RESET
                + pad_cell(f"Leg {leg + 1} avg", ROW_W, "<")
                + "".join(
                    self.CYAN + V + self.RESET
                    + pad_cell(
                        (
                            self.BOLD + self.RED + self.LEGSWON_MARK +" " + self.RESET
                            if leg < len(p.leg_results) and is_win(p.leg_results[leg])
                            else "  "
                        )
                        + (
                            f"{p.get_3dart_average_leg(leg):.2f}"
                            if leg < len(p.leg_results)
                            else ""
                        ),
                        COL_W,
                        ">"
                    )
                    for p in self.players
                )
                + self.CYAN + V + self.RESET
            )

        # bottom
        print(self.CYAN + hline(BL, BM, BR) + self.RESET)
