import os
import tempfile
import base64
from typing import Optional, Dict, Any, List, Tuple
from io import BytesIO

class ImageProcessor:
    """Image processing module for image analysis and generation."""

    def __init__(self):
        self.pillow_available = False
        self.diffusers_available = False
        self.temp_dir = tempfile.gettempdir()

        # Try to import optional dependencies
        try:
            from PIL import Image, ImageDraw, ImageFont
            self.pillow_available = True
            self.Image = Image
            self.ImageDraw = ImageDraw
            self.ImageFont = ImageFont
            print("PIL/Pillow (image processing) is available")
        except ImportError:
            print("Pillow not available. Install with: pip install pillow")

        try:
            from diffusers import StableDiffusionPipeline
            import torch
            self.diffusers_available = True
            self.StableDiffusionPipeline = StableDiffusionPipeline
            self.torch = torch
            self.sd_pipeline = None  # Lazy loading
            print("Diffusers (image generation) is available")
        except ImportError:
            print("Diffusers not available. Install with: pip install diffusers torch")

    def analyze_image(self, image_path: str, prompt: str = "") -> str:
        """Analyze an image and provide description."""
        if not self.pillow_available:
            return "Image analysis not available. Please install pillow."

        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"

        try:
            from PIL import Image

            # Open and get basic image info
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode

                # Basic analysis
                analysis = f"Image Analysis:\n"
                analysis += f"- Dimensions: {width}x{height} pixels\n"
                analysis += f"- Format: {format_name}\n"
                analysis += f"- Color mode: {mode}\n"

                # Calculate dominant colors (simplified)
                try:
                    colors = self._get_dominant_colors(img, 5)
                    analysis += f"- Dominant colors: {', '.join(colors)}\n"
                except:
                    analysis += "- Color analysis: Not available\n"

                # Add prompt-based analysis if provided
                if prompt:
                    analysis += f"\nRegarding your question about '{prompt}':\n"
                    analysis += "This is a basic image analysis. For advanced AI-powered image understanding, "
                    analysis += "please configure a vision model or use a specialized image analysis service."

                return analysis

        except Exception as e:
            return f"Image analysis error: {str(e)}"

    def generate_image(self, prompt: str, output_path: Optional[str] = None,
                      width: int = 512, height: int = 512, num_inference_steps: int = 20) -> str:
        """Generate an image from text prompt using Stable Diffusion."""
        if not self.diffusers_available:
            # Fallback: create a simple text-based image
            return self._create_text_image(prompt, output_path, width, height)

        try:
            # Lazy load the pipeline
            if not self.sd_pipeline:
                print("Loading Stable Diffusion pipeline...")
                self.sd_pipeline = self.StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=self.torch.float16 if self.torch.cuda.is_available() else self.torch.float32
                )
                if self.torch.cuda.is_available():
                    self.sd_pipeline = self.sd_pipeline.to("cuda")

            # Generate image
            if not output_path:
                import uuid
                filename = f"generated_image_{uuid.uuid4().hex[:8]}.png"
                output_path = os.path.join(self.temp_dir, filename)

            image = self.sd_pipeline(
                prompt,
                num_inference_steps=num_inference_steps,
                height=height,
                width=width
            ).images[0]

            image.save(output_path)
            return output_path

        except Exception as e:
            print(f"Diffusers generation failed: {e}")
            # Fallback to text image
            return self._create_text_image(prompt, output_path, width, height)

    def _create_text_image(self, text: str, output_path: Optional[str] = None,
                          width: int = 512, height: int = 512) -> str:
        """Create a simple text-based image as fallback."""
        if not self.pillow_available:
            raise Exception("Image generation not available")

        try:
            if not output_path:
                import uuid
                filename = f"text_image_{uuid.uuid4().hex[:8]}.png"
                output_path = os.path.join(self.temp_dir, filename)

            # Create image with text
            img = self.Image.new('RGB', (width, height), color='black')
            draw = self.ImageDraw.Draw(img)

            # Wrap text to fit image
            try:
                font = self.ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = self.ImageFont.load_default()

            # Simple text wrapping
            lines = []
            words = text.split()
            current_line = ""

            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] < width - 40:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw text
            y_position = 50
            for line in lines[:15]:  # Limit to 15 lines
                draw.text((20, y_position), line, fill='white', font=font)
                y_position += 30

            img.save(output_path)
            return output_path

        except Exception as e:
            raise Exception(f"Text image creation failed: {str(e)}")

    def _get_dominant_colors(self, image, num_colors: int = 5) -> List[str]:
        """Get dominant colors from an image."""
        # Simplified color analysis
        image = image.convert('RGB')
        image = image.resize((100, 100))  # Resize for faster processing

        colors = []
        pixels = list(image.getdata())

        # Simple color clustering (simplified)
        color_counts = {}
        for pixel in pixels:
            # Round colors to nearest 32 for grouping
            rounded = tuple((c // 32) * 32 for c in pixel)
            color_counts[rounded] = color_counts.get(rounded, 0) + 1

        # Get top colors
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        for color, _ in sorted_colors[:num_colors]:
            hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            colors.append(hex_color)

        return colors

    def resize_image(self, input_path: str, output_path: Optional[str] = None,
                    width: Optional[int] = None, height: Optional[int] = None,
                    maintain_aspect: bool = True) -> str:
        """Resize an image."""
        if not self.pillow_available:
            raise Exception("Image processing not available")

        if not os.path.exists(input_path):
            raise Exception(f"Input image not found: {input_path}")

        try:
            if not output_path:
                import uuid
                filename = f"resized_image_{uuid.uuid4().hex[:8]}.jpg"
                output_path = os.path.join(self.temp_dir, filename)

            with self.Image.open(input_path) as img:
                original_width, original_height = img.size

                if width and height and maintain_aspect:
                    # Calculate aspect ratio
                    aspect_ratio = original_width / original_height
                    if width / height > aspect_ratio:
                        width = int(height * aspect_ratio)
                    else:
                        height = int(width / aspect_ratio)
                elif width and not height:
                    aspect_ratio = original_width / original_height
                    height = int(width / aspect_ratio)
                elif height and not width:
                    aspect_ratio = original_width / original_height
                    width = int(height * aspect_ratio)
                else:
                    width = original_width
                    height = original_height

                resized_img = img.resize((width, height), self.Image.Resampling.LANCZOS)
                resized_img.save(output_path, 'JPEG', quality=90)

                return output_path

        except Exception as e:
            raise Exception(f"Image resize failed: {str(e)}")

    def create_thumbnail(self, input_path: str, output_path: Optional[str] = None,
                        size: Tuple[int, int] = (150, 150)) -> str:
        """Create a thumbnail of an image."""
        if not self.pillow_available:
            raise Exception("Image processing not available")

        try:
            if not output_path:
                import uuid
                filename = f"thumbnail_{uuid.uuid4().hex[:8]}.jpg"
                output_path = os.path.join(self.temp_dir, filename)

            with self.Image.open(input_path) as img:
                img.thumbnail(size, self.Image.Resampling.LANCZOS)
                img.save(output_path, 'JPEG', quality=85)

                return output_path

        except Exception as e:
            raise Exception(f"Thumbnail creation failed: {str(e)}")

    def convert_format(self, input_path: str, output_path: Optional[str] = None,
                      target_format: str = "PNG") -> str:
        """Convert image to different format."""
        if not self.pillow_available:
            raise Exception("Image processing not available")

        try:
            if not output_path:
                import uuid
                filename = f"converted_{uuid.uuid4().hex[:8]}.{target_format.lower()}"
                output_path = os.path.join(self.temp_dir, filename)

            with self.Image.open(input_path) as img:
                img.save(output_path, target_format)
                return output_path

        except Exception as e:
            raise Exception(f"Format conversion failed: {str(e)}")

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get detailed information about an image."""
        if not self.pillow_available:
            return {"error": "Image processing not available"}

        try:
            with self.Image.open(image_path) as img:
                return {
                    "filename": os.path.basename(image_path),
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.size[0],
                    "height": img.size[1],
                    "file_size": os.path.getsize(image_path),
                    "has_transparency": img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            return {"error": str(e)}

    def is_available(self) -> Dict[str, bool]:
        """Check availability of image processing features."""
        return {
            "image_analysis": self.pillow_available,
            "image_generation": self.diffusers_available,
            "image_manipulation": self.pillow_available,
            "format_conversion": self.pillow_available
        }