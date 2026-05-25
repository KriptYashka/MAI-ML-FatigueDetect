import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import random

DATASET_PATH = r"C:\Users\kript\.cache\kagglehub\datasets\rihabkaci99\fatigue-dataset\versions\1\Data"

FATIGUE_DIR = os.path.join(DATASET_PATH, "Fatigue")
NONFATIGUE_DIR = os.path.join(DATASET_PATH, "NonFatigue")

def load_images(folder, num_images=5):
    """Загрузить случайные изображения из папки."""
    images = []
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    selected = random.sample(files, min(num_images, len(files)))
    
    for filename in selected:
        filepath = os.path.join(folder, filename)
        try:
            img = Image.open(filepath)
            images.append((filename, img))
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
    
    return images

def show_dataset_samples(num_per_class=6):
    """Показать примеры изображений из датасета."""
    
    print("=" * 60)
    print("  Датасет Face Fatigue - Примеры изображений")
    print("=" * 60)
    
    fatigue_images = load_images(FATIGUE_DIR, num_per_class)
    nonfatigue_images = load_images(NONFATIGUE_DIR, num_per_class)
    
    total = len(fatigue_images) + len(nonfatigue_images)
    cols = 3
    rows = 2
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 8))
    fig.suptitle('Датасет Face Fatigue - Усталость vs Бодрость', fontsize=16, fontweight='bold')
    
    for idx, (name, img) in enumerate(fatigue_images):
        row = idx // cols
        col = idx % cols
        ax = axes[row, col]
        ax.imshow(img)
        ax.set_title(f'УСТАЛЫЙ: {name}', color='red', fontweight='bold')
        ax.axis('off')
    
    for idx, (name, img) in enumerate(nonfatigue_images):
        row = idx // cols + 1
        col = idx % cols
        if row < rows:
            ax = axes[row, col]
            ax.imshow(img)
            ax.set_title(f'БОДРЫЙ: {name}', color='green', fontweight='bold')
            ax.axis('off')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.show()

def show_single_image(category="Fatigue", index=0):
    """Показать одно изображение по индексу."""
    
    folder = FATIGUE_DIR if category == "Fatigue" else NONFATIGUE_DIR
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    if index >= len(files):
        print(f"Индекс {index} превышает количество изображений ({len(files)})")
        return
    
    filename = files[index]
    filepath = os.path.join(folder, filename)
    
    img = Image.open(filepath)
    
    print("=" * 60)
    print(f"  Изображение: {filename}")
    print(f"  Категория: {'Усталый' if category == 'Fatigue' else 'Бодрый'}")
    print(f"  Размер: {img.size}")
    print(f"  Формат: {img.format}")
    print(f"  Режим: {img.mode}")
    print("=" * 60)
    
    plt.figure(figsize=(8, 6))
    plt.imshow(img)
    color = 'red' if category == "Fatigue" else 'green'
    plt.title(f'{filename}\n{"УСТАЛЫЙ" if category == "Fatigue" else "БОДРЫЙ"}', 
              color=color, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.show()

def dataset_statistics():
    """По��азать статистику датасета."""
    
    fatigue_files = [f for f in os.listdir(FATIGUE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    nonfatigue_files = [f for f in os.listdir(NONFATIGUE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print("=" * 60)
    print("  Статистика датасета Face Fatigue")
    print("=" * 60)
    print(f"Усталые (Fatigue):     {len(fatigue_files)} изображений")
    print(f"Бодрые (NonFatigue):  {len(nonfatigue_files)} изображений")
    print(f"Всего:                {len(fatigue_files) + len(nonfatigue_files)} изображений")
    print("=" * 60)
    
    sizes_fatigue = []
    sizes_nonfatigue = []
    
    for f in random.sample(fatigue_files, min(10, len(fatigue_files))):
        img = Image.open(os.path.join(FATIGUE_DIR, f))
        sizes_fatigue.append(img.size)
    
    for f in random.sample(nonfatigue_files, min(10, len(nonfatigue_files))):
        img = Image.open(os.path.join(NONFATIGUE_DIR, f))
        sizes_nonfatigue.append(img.size)
    
    print("\nРазмеры изображений (случайная выборка):")
    print(f"Усталые:   мин {min(s[0] for s in sizes_fatigue)}x{max(s[1] for s in sizes_fatigue)}, макс {max(s[0] for s in sizes_fatigue)}x{max(s[1] for s in sizes_fatigue)}")
    print(f"Бодрые:    мин {min(s[0] for s in sizes_nonfatigue)}x{max(s[1] for s in sizes_nonfatigue)}, макс {max(s[0] for s in sizes_nonfatigue)}x{max(s[1] for s in sizes_nonfatigue)}")

def interactive_browser():
    """Интерактивный браузер изображений."""
    
    fatigue_files = sorted([f for f in os.listdir(FATIGUE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    nonfatigue_files = sorted([f for f in os.listdir(NONFATIGUE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    print("\n" + "=" * 60)
    print("  Интерактивный браузер изображений")
    print("=" * 60)
    print("Команды:")
    print("  f <N>  - показать N-е изображение усталого (0=первое)")
    print("  n <N>  - показать N-е изображение бодрого")
    print("  s      - показать случайные примеры")
    print("  stats  - статистика датасета")
    print("  q      - выход")
    print("=" * 60)
    
    while True:
        cmd = input("\nВведите команду: ").strip()
        
        if cmd.lower() == 'q':
            print("До свидания!")
            break
        
        elif cmd.lower() == 'stats':
            dataset_statistics()
        
        elif cmd.lower() == 's':
            show_dataset_samples(6)
        
        elif cmd.startswith('f '):
            try:
                idx = int(cmd.split()[1])
                show_single_image("Fatigue", idx)
            except (IndexError, ValueError):
                print("Неверный формат. Используйте: f <номер>")
        
        elif cmd.startswith('n '):
            try:
                idx = int(cmd.split()[1])
                show_single_image("NonFatigue", idx)
            except (IndexError, ValueError):
                print("Неверный формат. Используйте: n <номер>")
        
        else:
            print("Неизвестная команда. Введите 'stats', 's', 'f <N>', 'n <N>' или 'q'")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'stats':
            dataset_statistics()
        elif sys.argv[1] == 'browser':
            interactive_browser()
        elif sys.argv[1] == 'sample':
            show_dataset_samples(6)
    else:
        print("Использование:")
        print("  python show_images.py stats    - показать статистику")
        print("  python show_images.py sample - показать примеры")
        print("  python show_images.py browser - интерактивный браузер")
        print("\nЗапускаю браузер по умолчанию...")
        interactive_browser()