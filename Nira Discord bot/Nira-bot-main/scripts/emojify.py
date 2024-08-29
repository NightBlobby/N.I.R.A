from PIL import Image

# Discord emoji mapping for pixel colors
COLORS = {
  (0, 0, 0):
  "⬛",
  (0, 0, 255):
  "🔵",
  (255, 0, 0):
  "🔴",
  (255, 255, 0):
  "🟡",
  (190, 100, 80):
  "🟫",
  (255, 165, 0):
  "🟠",
  (160, 140, 210):
  "🟣",
  (255, 255, 255):
  "⬜",
  (0, 255, 0): 
  "🟢",
  # Add more color entries here for better precision
  # Example: (r, g, b): "emoji"
  (150, 75, 0):
  "🟤",
  (0, 128, 128):
  "🔷",
  (128, 0, 128):
  "🟪",
  (128, 128, 128):
  "⚪",
  (255, 192, 203):
  "🌸",
  (0, 255, 255):
  "🦋",
  (255, 0, 255):
  "💜",
  (128, 0, 0):
  "🍎",
  (255, 255, 128):
  "🌼",
  (0, 255, 128):
  "🍏",
  (128, 0, 255):
  "🟣",
  (255, 128, 0):
  "🎃",
  (128, 128, 0):
  "🌿",
  (0, 128, 0):
  "🍃",
  (0, 128, 255):
  "🌊",
  (255, 0, 128):
  "💖",
  (255, 128, 128):
  "🌹",
  (128, 255, 128):
  "🌿",
  (128, 128, 255):
  "🔷",
  (255, 128, 255):
  "🌸",
  (128, 255, 255):
  "🌼",
  # Additional color entries for better precision
  (0, 0, 128):
  "🟦",
  (0, 128, 128):
  "🔷",
  (128, 0, 128):
  "🟪",
  (128, 128, 128):
  "⚪",
}


def calculate_luminance(color):
  r, g, b = color
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def find_closest_emoji(color):
  emoji_colors = sorted(COLORS.keys(),
                        key=lambda c: euclidean_distance(color, c))
  return COLORS[emoji_colors[0]]


def euclidean_distance(c1, c2):
  r1, g1, b1 = c1
  r2, g2, b2 = c2
  d = ((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2)**0.5

  return d


def emojify_image(img, size=22):
  WIDTH, HEIGHT = size, size
  small_img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)

  emoji = ""
  small_img = small_img.load()
  for y in range(HEIGHT):
    for x in range(WIDTH):
      emoji += find_closest_emoji(small_img[x, y])
    emoji += "\n"
  return emoji
