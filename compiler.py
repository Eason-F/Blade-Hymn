import PyInstaller.__main__
import os

param = ['code/main.py', '--windowed', '--clean', '--name=Blade Hymn']
for folder_path, _, names in os.walk(os.path.join('code')):
    for file in [name for name in names if name.endswith('.py') and name != 'main.py']:
        param.append(f'--add-data=code/{file}:.')

for _, subfolders, _ in os.walk(os.path.join('data')):
    for subfolder in subfolders:
        for folder_path, _, names in os.walk(os.path.join('data', subfolder,)):
            for file in [name for name in names if name.endswith(subfolder)]:
                param.append(f'--add-data=data/{subfolder}/{file}:data/{subfolder}')

for _, subfolders, _ in os.walk(os.path.join('assets', 'audio')):
    for subfolder in subfolders:
            for folder_path, _, names in os.walk(os.path.join('assets', 'audio', subfolder)):
                for file in [name for name in names if name.endswith('.mp3') or name.endswith('.wav')]:
                    param.append(f'--add-data=assets/audio/{subfolder}/{file}:assets/audio/{subfolder}')

for _, subfolders, _ in os.walk(os.path.join('assets', 'graphics')):
    for subfolder in [folder for folder in subfolders if folder != 'enemies' and folder != 'ui']:
        for _, folders, _ in os.walk(os.path.join('assets', 'graphics', subfolder)):
            for folder in folders:
                for folder_path, _, names in os.walk(os.path.join('assets', 'graphics', subfolder, folder)):
                    for file in [name for name in names if name.endswith('.png')]:
                        param.append(f'--add-data=assets/graphics/{subfolder}/{folder}/{file}:assets/graphics/{subfolder}/{folder}')

param.append('--add-data=assets/graphics/player/player.png:assets/graphics/player')

for _, subfolders, _ in os.walk(os.path.join('assets', 'graphics', 'enemies')):
    for subfolder in subfolders:
        for _, folders, _ in os.walk(os.path.join('assets', 'graphics', 'enemies', subfolder)):
            for folder in folders:
                for folder_path, _, names in os.walk(os.path.join('assets', 'graphics', 'enemies', subfolder, folder)):
                    for file in [name for name in names if name.endswith('.png')]:
                        param.append(f'--add-data=assets/graphics/enemies/{subfolder}/{folder}/{file}:assets/graphics/enemies/{subfolder}/{folder}')

for _, subfolders, _ in os.walk(os.path.join('assets', 'graphics', 'ui')):
    for subfolder in subfolders:
        for _, folders, _ in os.walk(os.path.join('assets', 'graphics', 'ui', subfolder)):
            for folder in folders:
                for folder_path, _, names in os.walk(os.path.join('assets', 'graphics', 'ui', subfolder, folder)):
                    for file in [name for name in names if name.endswith('.png')]:
                        param.append(f'--add-data=assets/graphics/ui/{subfolder}/{folder}/{file}:assets/graphics/ui/{subfolder}/{folder}')

# for line in param:
#     print(line)
# print(param)

PyInstaller.__main__.run(param)