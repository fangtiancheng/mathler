import os
print(os.path.dirname(os.path.realpath(__file__)))
ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
FONTS_PATH = 'resources/fonts'
IMAGES_PATH = 'resources/images/'
SAVE_TMP_PATH = 'data/tmp'