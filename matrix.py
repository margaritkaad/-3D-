from vector import Vector3
import math

class Matrix:
    def __init__(self, rows):
        self.rows = [[float(x) for x in row] for row in rows]

    def __mul__(self, other):
        if isinstance(other, Matrix):
            result = [[0.0 for _ in range(4)] for _ in range(4)]
            for i in range(4):
                for j in range(4):
                    for k in range(4):
                        result[i][j] += self.rows[i][k] * other.rows[k][j]
            return Matrix(result)
        elif isinstance(other, Vector3):
            vec = [other.x, other.y, other.z, 1.0]
            result = [0.0, 0.0, 0.0, 0.0]
            for i in range(4):
                for k in range(4):
                    result[i] += self.rows[i][k] * vec[k]
            return Vector3(result[0], result[1], result[2])

    @staticmethod
    def rotation_x(angle):
        c, s = math.cos(angle), math.sin(angle)
        return Matrix([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, c, -s, 0.0],
            [0.0, s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def rotation_y(angle):
        c, s = math.cos(angle), math.sin(angle)
        return Matrix([
            [c, 0.0, s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-s, 0.0, c, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def rotation_z(angle):
        c, s = math.cos(angle), math.sin(angle)
        return Matrix([
            [c, -s, 0.0, 0.0],
            [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ])

    @staticmethod
    def look_at(eye, center, up):
        forward = (center - eye).normalize()
        right = forward.cross(up.normalize()).normalize()
        up = right.cross(forward).normalize()
        matrix = [
            [right.x, right.y, right.z, 0.0],
            [up.x, up.y, up.z, 0.0],
            [-forward.x, -forward.y, -forward.z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]
        # Транспонирование для корректной ориентации
        matrix = [[matrix[j][i] for j in range(4)] for i in range(4)]
        # Смещение
        matrix[0][3] = -eye.dot(Vector3(right.x, right.y, right.z))
        matrix[1][3] = -eye.dot(Vector3(up.x, up.y, up.z))
        matrix[2][3] = eye.dot(forward)
        return Matrix(matrix)
