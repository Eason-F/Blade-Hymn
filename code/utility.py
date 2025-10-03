from constants import *

def import_image(*path, alpha = True):
    full_path = os.path.join(abs_path, *path)
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path, file_ext = 'gif'):
    frame_dict = {}
    for folder_path, _, image_names in os.walk(os.path.join(abs_path, *path)):
        for image_name in image_names:
            if image_name.endswith(file_ext):
                path = os.path.join(folder_path, image_name)
                frame_dict[image_name.split('.')[0]] = [pygame.image.load(path).convert_alpha()]
    return frame_dict