from constants import *

def import_image(*path, alpha = True):
    full_path = os.path.join(abs_path, *path)
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path):
    frames = []
    for folder_path, _, image_names in os.walk(os.path.join(abs_path, *path)):
        image_names = [name for name in image_names if name.endswith( ".png")]
        for image_name in sorted(image_names, key = lambda x: int(x.split('.')[0])):
            path = os.path.join(folder_path, image_name)
            frames.append(pygame.image.load(path).convert_alpha())
    return frames

def import_subfolders(*path):
    frame_dict = {}
    for _, subfolders, _ in os.walk(os.path.join(abs_path, *path)):
        for subfolder in subfolders:
            frame_dict[subfolder] = import_folder(*path, subfolder)
    return frame_dict