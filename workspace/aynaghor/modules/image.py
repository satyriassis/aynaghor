class ImageProcessor:
    def __init__(self):
        self.pillow_available = False
        self.diffusers_available = False

    def is_available(self):
        return {
            "image_analysis": self.pillow_available,
            "image_generation": self.diffusers_available,
            "image_manipulation": self.pillow_available,
            "format_conversion": self.pillow_available
        }