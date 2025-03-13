import sys      
import math
import numpy
from PIL import Image
from dmc_colors import DMC_RGB_COLORS

DEFAULT_SAMPLING_SCALE = 8
DEFAULT_RENDER_PIXEL_SIZE = 8
DEFAULT_GAP = 1
DEFAULT_GAP_COLOR = (0,0,0) 
DEFAULT_COLOR_COUNT = 256

def fixed(number, decimal = 2):
  decimal = 10 ** decimal
  return round(number * decimal) / decimal
  
class Main():
  def __init__(self):
    if (len(sys.argv) < 2):
      return print('Error [init]: need an image file in argument')
    # get params
    base_image = self.get_params(sys.argv[1])
    if (not base_image):
      return print('err')
    # gap & board size
    self.gap = DEFAULT_GAP if len(sys.argv) < 3 else int(sys.argv[2])
    self.board_size = base_image.size[0] // self.sampling_size, base_image.size[1] // self.sampling_size
    # process image
    print('[1/5] Création de la palette..')
    palette_image = self.create_color_palette(self.color_count)
    print('[2/5] Correspondance de couleurs..')
    image = self.reduce_colors(base_image, palette_image)
    print('[3/5] Lecture des données pixels..')
    pixels = self.get_pixels(image)
    print('[4/5] Création de l\'image..')
    new_image = self.draw_image(pixels)
    print('[5/5] Ouverture du fichier..')
    # show image
    new_image.show()
    
  def get_params(self, image):
    image = Image.open(sys.argv[1], "r")
    width, height = image.size
    min_size = width if width < height else height
    # auto sampling
    auto_sampling = round(math.sqrt(min_size) / DEFAULT_SAMPLING_SCALE)
    print(f'Echantillonnage de l\'image: (défaut: {auto_sampling})')
    self.sampling_size = int(input() or auto_sampling)
    # def board size
    self.board_size = image.size[0] // self.sampling_size, image.size[1] // self.sampling_size
    print(f'Taille du pixel de rendu: (défaut: {DEFAULT_RENDER_PIXEL_SIZE})')
    self.render_pixel_size = int(input() or DEFAULT_RENDER_PIXEL_SIZE)
    print(f'Nombre limite de couleurs: (défaut: {DEFAULT_COLOR_COUNT})')
    self.color_count = int(input() or DEFAULT_COLOR_COUNT)
    return image

  def create_color_palette(self, color_count):
    palette_image = Image.new('P', (1,1))
    rgb_color_count = color_count * 3
    max_rgb_color_count = rgb_color_count if rgb_color_count < len(DMC_RGB_COLORS) else len(DMC_RGB_COLORS)
    rgb_colors = DMC_RGB_COLORS[:max_rgb_color_count]
    self.color_count = len(rgb_colors) // 3
    print(f'\t↪ nombre de couleurs: {self.color_count}')
    palette_image.putpalette(rgb_colors)
    return palette_image
  
  def process_pixel(self, pixel):
    closest_differ = 255 * 3
    closest_index = -1
    for index in range(self.color_count):
      i = index * 3
      r = abs(DMC_RGB_COLORS[i] - pixel[0])
      g = abs(DMC_RGB_COLORS[i + 1] -pixel[1])
      b = abs(DMC_RGB_COLORS[i + 2] - pixel[2])
      current_differ = r + g + b
      if current_differ < closest_differ:
        closest_index = i
        closest_differ = current_differ
        if current_differ == 0:
          self.bingo_count += 1
          break
    self.differs.append(closest_differ)
    return (DMC_RGB_COLORS[closest_index], DMC_RGB_COLORS[closest_index + 1], DMC_RGB_COLORS[closest_index + 2])
  
  def reduce_colors(self, image, palette_image):
    resize_image = image.resize(self.board_size).convert("RGB")
    self.differs = []
    self.bingo_count = 0
    for x in range(resize_image.width):
      for y in range(resize_image.height):
        pixel = resize_image.getpixel((x, y))
        color = self.process_pixel(pixel)
        resize_image.putpixel((x,y), color)
    average_differ = fixed(sum(self.differs) / len(self.differs))
    differ_percentage = fixed(average_differ / 255 * 100)
    print(f'\t↪ Moyenne de difference: {differ_percentage}% ({average_differ}/{255})')
    pixel_count = resize_image.width * resize_image.height
    bingo_percentage = fixed(self.bingo_count / pixel_count * 100)
    print(f'\t↪ Nombre de parfait: {bingo_percentage}% ({self.bingo_count}/{pixel_count})')
    return resize_image

  def get_pixels(self, image):
    pixels = list(image.getdata())
    colors = set()
    for pixel in pixels:
      colors.add(pixel)
    print(f'\t↪ {len(pixels)} pixels générés')
    print(f'\t↪ {len(colors)} couleurs')
    return pixels
  
  def draw_pixel(self, image, coords, color):
    pos_x = self.gap * (coords[0] + 1) + coords[0] * self.render_pixel_size
    pos_y = self.gap * (coords[1] + 1) + coords[1] * self.render_pixel_size
    for y in range(self.render_pixel_size):
      for x in range(self.render_pixel_size):
        image.putpixel((pos_x + x, pos_y + y), color)
 
  def draw_image(self, pixels):
    image_size_x = self.board_size[0] * (self.render_pixel_size + self.gap) + self.gap
    image_size_y = self.board_size[1] * (self.render_pixel_size + self.gap) + self.gap
    image_size = image_size_x, image_size_y
    print(f'\t↪ taille de l\'image: {image_size}')
    print(f'\t↪ taille en diamands: {self.board_size}')
    image = Image.new("RGB", image_size, DEFAULT_GAP_COLOR)
    for y in range(self.board_size[1]):
      for x in range(self.board_size[0]):
        index = x + y * self.board_size[0]
        color = pixels[index]
        self.draw_pixel(image, (x,y), color)
    return image
    
Main()