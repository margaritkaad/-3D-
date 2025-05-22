from vector import Vector3
from geometry import z_to_color

def project(point, scale):
    """Проецирует 3D-точку на 2D-плоскость с учетом перспективы."""
    if 1 - 0.02 * point.z == 0:
        return (400, 300)  # Центр канваса как запасной вариант
    x_2d = 400 + scale * point.x / (1 - 0.02 * point.z)
    y_2d = 300 - scale * point.y / (1 - 0.02 * point.z)
    return (x_2d, y_2d)

def render_triangles(canvas, transformed_points, triangles, scale, color_func, start_r, start_g, start_b, end_r, end_g, end_b):
    """Отрисовывает треугольники на канвасе с учетом глубины и цвета."""
    min_z = min(p.z for p in transformed_points)
    max_z = max(p.z for p in transformed_points)
    
    # Сортировка треугольников по средней Z-координате
    triangles_to_render = [(sum(transformed_points[idx].z for idx in tri) / 3, tri) for tri in triangles]
    triangles_to_render.sort(key=lambda x: x[0], reverse=True)
    
    for avg_z, tri in triangles_to_render:
        points_2d = [project(transformed_points[idx], scale) for idx in tri]
        color = color_func(avg_z, min_z, max_z, 1.0, start_r, start_g, start_b, end_r, end_g, end_b)
        canvas.create_polygon(points_2d, fill=color, outline='black')