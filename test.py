from PIL import Image
import numpy as np
import imageio

img_path = "img.png"
test_img = Image.open(img_path)
img_np = np.array(test_img)
red_content = img_np[:, :, 0]
red_content_back = red_content[:]
green_content = img_np[:, :, 1]

imageio.imwrite('test_red_content.png', red_content)
imageio.imwrite('test_green_content.png', green_content)
imageio.imwrite('test_green-red.png', green_content - red_content_back)
imageio.imwrite('test_red-green.png', red_content_back - green_content)

subtraction_green = green_content - red_content_back
b = np.where(subtraction_green > 200)
print(b)