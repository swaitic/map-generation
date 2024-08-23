import numpy as np
import matplotlib.pyplot as plt
import noise
import random
from scipy.ndimage import gaussian_filter
#генерация мира
def generate_world_map(width, height, scale=50, octaves=4, persistence=0.5, lacunarity=2.0, seed=None):
    world_map = np.zeros((height, width)) #задаем мапу
    
    if seed:
        np.random.seed(seed)
    
    for y in range(height): #перлин шум для задания высот
        for x in range(width):
            nx = x / width - 0.5
            ny = y / height - 0.5
            elevation = noise.pnoise2(nx * scale,
                                      ny * scale,
                                      octaves=octaves,
                                      persistence=persistence,
                                      lacunarity=lacunarity,
                                      repeatx=width,
                                      repeaty=height,
                                      base=seed)
            world_map[y][x] = elevation
    #нормализация
    world_map = (world_map - world_map.min()) / (world_map.max() - world_map.min())
    
    return world_map
#АДЫН остров
def create_island_mask(width, height, center_x, center_y, radius, falloff):
    mask = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance < radius:
                mask[y, x] = 1.0 - (distance / radius) ** falloff
    return mask
#МНОГА остров
def generate_islands_mask(width, height, num_islands, min_radius, max_radius, falloff):
    mask = np.zeros((height, width))
    
    np.random.seed(random.randint(0,60))
    
    for _ in range(num_islands):
        center_x = np.random.randint(0, width)
        center_y = np.random.randint(0, height)
        radius = np.random.uniform(min_radius, max_radius)
        island_mask = create_island_mask(width, height, center_x, center_y, radius, falloff)
        mask = np.maximum(mask, island_mask)
    
    return mask
#распределяет карту высот так чтобы каждый диапазон стал биомом
def classify_biomes(world_map):
    biomes = np.zeros(world_map.shape)
    
    for y in range(world_map.shape[0]):
        for x in range(world_map.shape[1]):
            elevation = world_map[y, x]
            
            if elevation < 0.3:
                biomes[y, x] = 0  # Океан
            elif elevation < 0.4:
                biomes[y, x] = 1  # Пляж
            elif elevation < 0.55:
                biomes[y, x] = 2  # Лес
            elif elevation < 0.8:
                biomes[y, x] = 3  # Холмы
            else:
                biomes[y, x] = 4  # Горы
    
    return biomes
#делает так чтобы все что не под маской острова стало водой
def apply_island_mask(world_map, mask):
    return world_map * mask
#дает биомам цвета
def plot_world_map(biomes):
    biome_colors = {
        0: (0, 0, 0.5),    # Океан - темно-синий
        1: (0.9, 0.9, 0.5), # Пляж - светло-желтый
        2: (0.1, 0.7, 0.1), # Лес - зеленый
        3: (0.5, 0.5, 0.2), # Холмы - коричневый
        4: (0.5, 0.5, 0.5)  # Горы - серый
    }
    
    color_map = np.zeros((*biomes.shape, 3))
    
    for biome, color in biome_colors.items():
        color_map[biomes == biome] = color
    
    plt.figure(figsize=(12, 8))
    plt.imshow(color_map, origin='upper')
    plt.title("Generated World Map with Multiple Islands")
    plt.show()
#Делает так чтобы переход из одного биома в другой был мягче
def smooth_map(world_map, sigma=2.0):
    return gaussian_filter(world_map, sigma=sigma)
# Параметры карты
width = 512
height = 512
scale = 50 #масштаб шума
octaves = 8 #детализация - количество октав
persistence = 0.5 #снижение амплитуды октав
lacunarity = 2.0 #частота октав
seed = random.randint(0,100) #нач значение шума

# Генерация карты
world_map = generate_world_map(width, height, scale, octaves, persistence, lacunarity, seed)

# Создание маски для нескольких островов
num_islands = 8
min_radius = 46
max_radius = 150
falloff = 3 #плавность перехода от центра острова к краю
island_mask = generate_islands_mask(width, height, num_islands, min_radius, max_radius, falloff)

world_map_with_islands = apply_island_mask(world_map, island_mask)

sigma = 3.0  #параметр сглаживания
#смягчение
smoothed_map = smooth_map(world_map_with_islands, sigma=sigma)
#биомы
biomes = classify_biomes(smoothed_map)
#рисуем
plot_world_map(biomes)
