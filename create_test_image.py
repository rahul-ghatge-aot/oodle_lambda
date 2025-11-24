
from PIL import Image

# Create a dummy image for testing
img = Image.new('RGB', (64, 64), color = 'red')
img.save('test_image.png')

print("Created test_image.png")
