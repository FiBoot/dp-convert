import sys      
import math
import numpy
from PIL import Image, ImageDraw

DEFAULT_RENDER_PIXEL_SIZE = 8
DEFAULT_GAP = 1
DEFAULT_COLOR_COUNT = 54

class Main():
  def __init__(self):
    if (len(sys.argv) < 2):
      return print('Error [init]: need an image file in argument')
    # open image
    base_image = self.open_image(sys.argv[1])
    if (base_image == False):
      return
    # get params
    self.get_params(base_image)
    # process image
    print(f'[1/4] resize & color reduce image..')
    image = self.reduce_colors(base_image, self.color_count)
    print('[2/4] generating pixels..')
    pixels = self.process_pixels(image)
    print('[3/4] creating image..')
    new_image = self.draw_image(pixels)
    print('[4/4] rendering..')
    # show image
    new_image.show()
    
  def open_image(self, file_path):
    try:
      return Image.open(file_path, "r")
    except:
      print(f'Error [init]: File \'{file_path}\' not found')
      return False
  
  def get_params(self, image):
    width, height = image.size
    min_size = width if width < height else height
    auto_sampling = round(math.sqrt(min_size) / 3)
    print(f'Echantillonnage de l\'image: (defaut: {auto_sampling})')
    self.sampling_size = int(input() or auto_sampling)
    # def board size
    self.board_size = image.size[0] // self.sampling_size, image.size[1] // self.sampling_size
    print(f'Taille du pixel de rendu: (defaut: {DEFAULT_RENDER_PIXEL_SIZE})')
    self.render_pixel_size = int(input() or DEFAULT_RENDER_PIXEL_SIZE)
    print(f'Nombre limite de couleurs: (defaut: {DEFAULT_COLOR_COUNT})')
    self.color_count = int(input() or DEFAULT_COLOR_COUNT)
  
  def reduce_colors(self, image, color_count):
    processed_image = image.resize(self.board_size).convert("P", palette=Image.ADAPTIVE, colors=color_count)
    print(f'\t↪ new image size: {self.board_size}')
    print(f'\t↪ colors limited to {color_count}')
    return processed_image.convert("RGB")
    
  def process_pixels(self, image):
    pixels = list(image.getdata())
    colors = []
    for pixel in pixels:
      if pixel not in colors:
        colors.append(pixel)
    print(f'\t↪ {len(pixels)} pixels generated')
    print(f'\t↪ {len(colors)} different colors')
    return pixels
  
  def draw_pixel(self, image, coords, color):
    for y in range(self.render_pixel_size):
      for x in range(self.render_pixel_size):
        try:
          pos_x = DEFAULT_GAP * (coords[0] + 1) + coords[0] * self.render_pixel_size + x
          pos_y = DEFAULT_GAP * (coords[1] + 1) + coords[1] * self.render_pixel_size + y
          image.putpixel((pos_x, pos_y), color)
        except:
          print(f'nope {pos_x, pos_y}')
 
    
  def draw_image(self, pixels):
    image_size_x = self.board_size[0] * (self.render_pixel_size + DEFAULT_GAP) + DEFAULT_GAP
    image_size_y = self.board_size[1] * (self.render_pixel_size + DEFAULT_GAP) + DEFAULT_GAP
    image_size = image_size_x, image_size_y
    print(f'\t↪ image size: {image_size}')
    print(f'\t↪ board size: {self.board_size}')
    image = Image.new(mode="RGB", size=image_size)
    for y in range(self.board_size[1]):
      for x in range(self.board_size[0]):
        index = x + y * self.board_size[0]
        color = pixels[index]
        self.draw_pixel(image, (x,y), color)
    return image
    
Main()