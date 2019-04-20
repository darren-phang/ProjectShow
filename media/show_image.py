import matplotlib.pyplot as plt
from PIL import Image
from io import StringIO, BytesIO
x = open('./image/default_image_for_inception.jpeg', 'rb').read()
print(x)
img = Image.open('./image/default_image_for_inception.jpeg')
s = BytesIO()
img.save(s, format='JPEG')
print(s.getvalue())
print(type(s.getvalue()))
print(type(x))