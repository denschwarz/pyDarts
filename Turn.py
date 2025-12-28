class Turn:
    def __init__(self, current_score):
        self.throws = []
        self.throws_strings = []
        self.current_score = current_score
        self.done = False

    def remove_throw(self):
        self.throws.pop()

    def add_throw(self, value: int, score_string: str):
        if len(self.throws) < 3:
            self.throws.append(value)
            self.throws_strings.append(score_string)
        # Overthrown, count as 3 darts with no score
        if sum(self.throws) > self.current_score:
            self.throws = [0, 0, 0]
            self.throws_strings = ["0", "0", "0"]
            self.done = True
        # Turn over after 3 throws
        if len(self.throws) == 3:
            self.done = True
        # Turn over if reached 0
        if sum(self.throws) == self.current_score:
            self.done = True
            # FIXME: We could check for doubles here
