import math
from vector import Vector3

def sea_shell(u, v, alpha=0.3, b=0.1):
    x = alpha * math.exp(b * v) * math.cos(v) * (1 + math.cos(u))
    y = alpha * math.exp(b * v) * math.sin(v) * (1 + math.cos(u))
    z = alpha * math.exp(b * v) * math.sin(u)
    return Vector3(x, y, z)

def generate_grid(nu, nv, func, alpha=0.3, b=0.1):
    points = []
    for i in range(nu):
        row = []
        u = i * 2 * math.pi / (nu - 1) if nu > 1 else 0
        for j in range(nv):
            v = j * 6 * math.pi / (nv - 1) if nv > 1 else 0
            row.append(func(u, v, alpha, b))
        points.append(row)
    return points

def generate_triangles(nu, nv):
    triangles = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            idx0 = i * nv + j
            idx1 = (i + 1) * nv + j
            idx2 = (i + 1) * nv + j + 1
            idx3 = i * nv + j + 1
            triangles.append((idx0, idx1, idx2))
            triangles.append((idx0, idx2, idx3))
    return triangles

def z_to_color(z, min_z, max_z, color_factor=1.0, start_r=0, start_g=0, start_b=255, end_r=255, end_g=0, end_b=0):
    if max_z == min_z: return f'#{start_r:02x}{start_g:02x}{start_b:02x}'
    t = (z - min_z) / (max_z - min_z)
    r = int((start_r + t * (end_r - start_r)) * color_factor)
    g = int((start_g + t * (end_g - start_g)) * color_factor)
    b = int((start_b + t * (end_b - start_b)) * color_factor)
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    return f'#{r:02x}{g:02x}{b:02x}'