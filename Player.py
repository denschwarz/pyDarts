class Player:
    def __init__(self, name: str, start_score: int = 501):
        self.name = name
        self.start_score = start_score
        self.current_score = start_score
        self.legs_won = 0
        self.leg_results = []

        self.throws = []
        self.throws_finished_legs = []
        self.last_turn = []

        self.throws_strings = []
        self.throws_finished_legs_strings = []
        self.last_turn_strings = []

    def add_throw(self, value: int, value_string: str, subtract_from_score = True):
        self.throws.append(value)
        self.throws_strings.append(value_string)
        if subtract_from_score:
            self.current_score -= value
        else:
            self.current_score += value


    def add_turn(self, turn, subtract_from_score = True):
        for value, value_string in zip(turn.throws, turn.throws_strings):
            self.add_throw(value, value_string, subtract_from_score)
        self.last_turn = turn.throws
        self.last_turn_strings = turn.throws_strings


    def get_3dart_average_this_leg(self) -> float:
        if not self.throws:
            return 0.0
        return (sum(self.throws) / len(self.throws)) * 3

    def get_3dart_average_leg(self, leg) -> float:
        if leg > len(self.throws_finished_legs)-1:
            return 0.0
        if not self.throws_finished_legs[leg]:
            return 0.0
        return (sum(self.throws_finished_legs[leg]) / len(self.throws_finished_legs[leg])) * 3
    
    def get_3dart_average_total(self) -> float:
        throws_total = len(self.throws)
        sum_total = sum(self.throws)
        for throws_old_leg in self.throws_finished_legs:            
            throws_total += len(throws_old_leg)
            sum_total += sum(throws_old_leg)
        if throws_total <= 0:
            return 0.0
        return (sum_total / throws_total) * 3

    def end_leg(self):
        self.throws_finished_legs.append(self.throws)
        self.throws_finished_legs_strings.append(self.throws_strings)
        self.throws = []
        self.throws_strings = []
        self.current_score = self.start_score

    def start_new_leg(self):
        self.current_score = self.start_score

    def delete_last_turn(self):
        N_throws = len(self.last_turn)
        self.current_score += sum(self.throws[-N_throws:])
        del self.throws[-N_throws:]
        del self.throws_strings[-N_throws:]

    def make_winner(self):
        self.legs_won += 1
        self.leg_results.append("win")

    def make_looser(self):
        self.leg_results.append("loss")


    def __str__(self):
        return f"{self.name}: {self.current_score} Punkte"