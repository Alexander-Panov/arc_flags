import json
import random

COLORS = {
    'Красный': (255, 0, 0),
    'Зеленый': (0, 255, 0),
    'Синий': (0, 0, 255),
    'Голубой': (0, 255, 255),
}

def generate_random_graph(K, filename="random_graph.json"):
    # Определяем границы для координат вершин
    x_range = (0, 20)
    y_range = (0, 20)

    # Генерация вершин и их позиций
    pos = [[random.uniform(*x_range), random.uniform(*y_range)] for _ in range(K)]

    # Генерация связей между вершинами (ребер)
    adj = []
    for i in range(K):
        # Добавляем случайное количество связей для каждой вершины
        connections = random.sample(range(K), random.randint(1, 3))
        for j in connections:
            if i != j and [i, j] not in adj:
                adj.append([i, j])

    # Генерация цветов вершин
    points_colors = [random.choice(list(COLORS.values())) for _ in range(K)]

    # Генерация названий вершин
    texts = [f"Point {i}" for i in range(K)]

    # Собираем все в один словарь
    graph_data = {
        "pos": pos,
        "adj": adj,
        "points_colors": points_colors,
        "texts": texts
    }

    # Запись в файл .json
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False, indent=4)

    print(f"Граф с {K} вершинами успешно сгенерирован и сохранен в файл '{filename}'.")


if __name__ == '__main__':
    # Пример использования
    generate_random_graph(50)
