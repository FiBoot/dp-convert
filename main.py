import sys      
import math
import numpy
from PIL import Image, ImageDraw, ImagePalette
from dmc_colors import DMC_RGB_COLORS

# DMC_RGB_COLORS=[
#   199,43,59,    #321	Red
#   90,143,184,   #322	Baby Blue Dark
#   179,59,75,    #326	Rose Very Dark
#   99,54,102,    #327	Violet Dark
# ]

DEFAULT_SAMPLING_SCALE = 4
DEFAULT_RENDER_PIXEL_SIZE = 8
DEFAULT_GAP = 1
DEFAULT_GAP_COLOR = (66,66,66)  #3799	Pewter Gray Very Dark
DEFAULT_COLOR_COUNT = 256

class Main():
  def __init__(self):
    if (len(sys.argv) < 2):
      return print('Error [init]: need an image file in argument')
    # get params
    base_image = self.get_params(sys.argv[1])
    # gap & board size
    self.gap = DEFAULT_GAP if len(sys.argv) < 3 else int(sys.argv[2])
    self.board_size = base_image.size[0] // self.sampling_size, base_image.size[1] // self.sampling_size
    # process image
    print(f'[1/5] creating colors palette..')
    palette_image = self.create_color_palette(self.color_count)
    print(f'[2/5] resize & color reduce image..')
    image = self.reduce_colors(base_image, palette_image)
    print('[3/5] generating pixels..')
    pixels = self.process_pixels(image)
    print('[4/5] creating image..')
    new_image = self.draw_image(pixels)
    print('[5/5] rendering..')
    # show image
    new_image.show()
    
  def get_params(self, image):
    image = Image.open(sys.argv[1], "r")
    width, height = image.size
    min_size = width if width < height else height
    # auto sampling
    auto_sampling = round(math.sqrt(min_size) / DEFAULT_SAMPLING_SCALE)
    print(f'Echantillonnage de l\'image: (defaut: {auto_sampling})')
    self.sampling_size = int(input() or auto_sampling)
    # def board size
    self.board_size = image.size[0] // self.sampling_size, image.size[1] // self.sampling_size
    # propose new pixel size
    proposed_pixel_size = self.sampling_size if self.sampling_size < DEFAULT_RENDER_PIXEL_SIZE else DEFAULT_RENDER_PIXEL_SIZE
    print(f'Taille du pixel de rendu: (defaut: {proposed_pixel_size})')
    self.render_pixel_size = int(input() or proposed_pixel_size)
    print(f'Nombre limite de couleurs: (defaut: {DEFAULT_COLOR_COUNT})')
    self.color_count = int(input() or DEFAULT_COLOR_COUNT)
    return image

  def create_color_palette(self, color_count):
    palette_image = Image.new('P', (1,1))
    rgb_color_count = color_count * 3
    max_rgb_color_count = rgb_color_count if rgb_color_count < len(DMC_RGB_COLORS) else len(DMC_RGB_COLORS)
    rgb_colors = DMC_RGB_COLORS[:max_rgb_color_count]
    self.color_count = len(rgb_colors) // 3
    print(f'\t↪ color count: {self.color_count}')
    palette_image.putpalette(rgb_colors)
    return palette_image
  
  def reduce_colors(self, image, palette_image):
    processed_image = image.resize(self.board_size)
    px = processed_image.load()
    for x in range(processed_image.width):
      for y in range(processed_image.height):
        pixel = processed_image.getpixel((x, y))
        print(pixel)
    #.convert("RGB").quantize(palette=palette_image)
    # resize_image = image.resize(self.board_size).convert("RGB")
    # processed_image = resize_image.quantize(palette=palette_image, dither=Image.Dither.NONE)
    return processed_image.convert("RGB")
    
  def process_pixels(self, image):
    pixels = list(image.getdata())
    colors = set()
    for pixel in pixels:
      colors.add(pixel)
    print(f'\t↪ {len(pixels)} pixels generated')
    print(f'\t↪ {len(colors)} different colors')
    return pixels
  
  def draw_pixel(self, image, coords, color):
    for y in range(self.render_pixel_size):
      for x in range(self.render_pixel_size):
        pos_x = self.gap * (coords[0] + 1) + coords[0] * self.render_pixel_size + x
        pos_y = self.gap * (coords[1] + 1) + coords[1] * self.render_pixel_size + y
        image.putpixel((pos_x, pos_y), color)
 
  def draw_image(self, pixels):
    image_size_x = self.board_size[0] * (self.render_pixel_size + self.gap) + self.gap
    image_size_y = self.board_size[1] * (self.render_pixel_size + self.gap) + self.gap
    image_size = image_size_x, image_size_y
    print(f'\t↪ image size: {image_size}')
    print(f'\t↪ board size: {self.board_size}')
    image = Image.new("RGB", image_size, DEFAULT_GAP_COLOR)
    for y in range(self.board_size[1]):
      for x in range(self.board_size[0]):
        index = x + y * self.board_size[0]
        color = pixels[index]
        self.draw_pixel(image, (x,y), color)
    return image
    
Main()