import json

class PresentationState:
    def __init__(self):
        self.slides = list()
        self.title_font = "Liberation Sans"
        self.title_size = "44pt"
        self.title_weight = "bold"
        self.body_font = "Liberation Sans"
        self.body_size = "22pt"
        self.body_weight = "normal"

    def add_blank(self):
        s = dict()
        s["title"] = "New Slide"
        s["subtitle"] = ""
        s["layout_type"] = "single_column"
        s["bullets"] = list()
        s["speaker_notes"] = list()
        self.slides.append(s)
        return len(self.slides) - 1

    def remove_at(self, idx):
        if len(self.slides) > 1 and 0 <= idx < len(self.slides):
            del self.slides[idx]
            return True
        return False

    def get_json_data(self):
        p = dict()
        p["$schema"] = "https://json-schema.org"
        p["title"] = "Presentation Data Schema"
        p["global_title_style"] = {"font_name": self.title_font, "font_size": self.title_size, "font_weight": self.title_weight}
        p["global_body_style"] = {"font_name": self.body_font, "font_size": self.body_size, "font_weight": self.body_weight}
        p["slides"] = self.slides
        return p
