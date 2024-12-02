class Case:
    def __init__(self, x, y, case_type):
        self.x = x
        self.y = y
        self.case_type = case_type

    def is_traversable(self):
        return self.case_type != "obstacle"

    def get_color(self):
        if self.case_type == "normal":
            return (200, 200, 200)  # Gris clair
        elif self.case_type == "obstacle":
            return (50, 50, 50)  # Gris foncé
        elif self.case_type == "heal":
            return (0, 255, 0)  # Vert
        elif self.case_type == "trap":
            return (255, 0, 0)  # Rouge
        return (255, 255, 255)  # Blanc par défaut
