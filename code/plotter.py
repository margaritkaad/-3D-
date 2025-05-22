import tkinter as tk
from tkinter import ttk
from vector import Vector3
from matrix import Matrix
from renderer import render_triangles
from geometry import sea_shell, generate_grid, generate_triangles, z_to_color
import math

class SeaShellPlotter:
    def update_alpha(self):
        self.alpha = self.alpha_var.get()
        self.update_polygons()

    def update_beta(self):
        self.b = self.b_var.get()
        self.update_polygons()

    def __init__(self, root, nu=30, nv=30):
        self.alpha = 0.3  # Начальное значение в диапазоне [0.1, 0.5]
        self.b = 0.1      # Начальное значение в диапазоне [0.05, 0.2]
        self.root = root
        self.nu, self.nv = nu, nv
        self.points = generate_grid(nu, nv, sea_shell, self.alpha, self.b)
        self.all_points = [self.points[i][j] for i in range(nu) for j in range(nv)]
        self.triangles = generate_triangles(nu, nv)
        self.rotation_x = math.pi / 6  # Наклон на 30 градусов
        self.rotation_y = math.pi / 4  # Поворот на 45 градусов по часовой стрелке
        self.rotation_z = 0.0
        self.scale = 80.0
        self.color_factor = 1.0
        self.last_x = None
        self.last_y = None
        self.shift_pressed = False
        self.camera_pos = Vector3(5, 5, 20)  # Позиция камеры
        self.look_at = Vector3(0, 0, 0)        # Точка взгляда
        self.up = Vector3(0, 0, 1)             # Вектор вверх

        # Основной фрейм
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)

        # Доп фрейм
        self.control_top_frame = tk.Frame(self.main_frame)
        self.control_top_frame.pack(side='top', fill='x')

        # Ползунок для nu 
        self.nu_var = tk.IntVar(value=nu)
        tk.Label(self.control_top_frame, text="U:").pack(side='right', padx=5, pady=5)
        ttk.Scale(self.control_top_frame, from_=5, to=50, orient='horizontal', variable=self.nu_var).pack(side='right', padx=5)
        self.nu_var.trace("w", lambda *args: self.update_polygons())

        # Ползунок для nv 
        self.nv_var = tk.IntVar(value=nv)
        tk.Label(self.control_top_frame, text="V:").pack(side='right', padx=5, pady=5)
        ttk.Scale(self.control_top_frame, from_=5, to=50, orient='horizontal', variable=self.nv_var).pack(side='right', padx=5)
        self.nv_var.trace("w", lambda *args: self.update_polygons())

        # Ползунок для alpha
        tk.Label(self.control_top_frame, text="Alpha:").pack(side='right', padx=5, pady=5)
        self.alpha_var = tk.DoubleVar(value=self.alpha)
        ttk.Scale(self.control_top_frame, from_=0.1, to=0.5, orient='horizontal', variable=self.alpha_var).pack(side='right', padx=5)
        self.alpha_var.trace("w", lambda *args: self.update_alpha())

        # Ползунок для beta
        tk.Label(self.control_top_frame, text="Beta:").pack(side='right', padx=5, pady=5)
        self.b_var = tk.DoubleVar(value=self.b)
        ttk.Scale(self.control_top_frame, from_=0.05, to=0.2, orient='horizontal', variable=self.b_var).pack(side='right', padx=5)
        self.b_var.trace("w", lambda *args: self.update_beta())

        # Подпись фигуры
        self.title_label = tk.Label(self.control_top_frame, text="Поверхность Морская раковина", font=("Helvetica", 14))
        self.title_label.pack(side='left', padx=5, pady=5)

        # Canvas для отрисовки
        self.canvas = tk.Canvas(self.main_frame, width=800, height=500, bg='white')
        self.canvas.pack(fill='both', expand=True)

        # Фрейм для элементов управления
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill='x', pady=5)

        # Ползунок для масштаба
        tk.Label(self.control_frame, text="Масштаб:").pack(side='left', padx=5)
        self.scale_slider = ttk.Scale(self.control_frame, from_=1, to=200, orient='horizontal', command=self.update_scale)
        self.scale_slider.set(self.scale)
        self.scale_slider.pack(side='left', padx=5, fill='x', expand=True)

        # Ползунки для цвета
        self.start_r = tk.DoubleVar(value=127)
        tk.Scale(self.control_frame, from_=0, to=255, orient='horizontal', variable=self.start_r, label="Start R").pack(side='left', padx=5)
        self.start_r.trace("w", lambda *args: self.draw())
        self.start_g = tk.DoubleVar(value=0)
        tk.Scale(self.control_frame, from_=0, to=255, orient='horizontal', variable=self.start_g, label="Start G").pack(side='left', padx=5)
        self.start_g.trace("w", lambda *args: self.draw())
        self.start_b = tk.DoubleVar(value=0)
        tk.Scale(self.control_frame, from_=0, to=255, orient='horizontal', variable=self.start_b, label="Start B").pack(side='left', padx=5)
        self.start_b.trace("w", lambda *args: self.draw())
        self.end_r = tk.DoubleVar(value=0)
        tk.Scale(self.control_frame, from_=0, to=255, orient='horizontal', variable=self.end_r, label="End R").pack(side='left', padx=5)
        self.end_r.trace("w", lambda *args: self.draw())
        self.end_g = tk.DoubleVar(value=0)
        tk.Scale(self.control_frame, from_=0, to=255, orient='horizontal', variable=self.end_g, label="End G").pack(side='left', padx=5)
        self.end_g.trace("w", lambda *args: self.draw())
        self.end_b = tk.DoubleVar(value=127)
        tk.Scale(self.control_frame, from_=0, to=255, orient='horizontal', variable=self.end_b, label="End B").pack(side='left', padx=5)
        self.end_b.trace("w", lambda *args: self.draw())

        # Фрейм для легенды
        self.legend_frame = tk.Frame(self.main_frame, bg='lightgray', bd=2, relief='solid')
        self.legend_frame.place(x=10, y=45, width=200, height=220)

        # Текст легенды
        self.legend_title = tk.Label(self.legend_frame, text="Описание:", font=("Helvetica", 12, "bold"), bg='lightgray')
        self.legend_title.pack(pady=5)
        self.legend_formula = tk.Label(
            self.legend_frame,
            text=f"Формула:\nx = αe^(βv)cos(v)(1+cos(u))\ny = αe^(βv)sin(v)(1+cos(u))\nz = αe^(βv)sin(u)",
            font=("Helvetica", 10),
            bg='lightgray',
            justify='center'
        )
        self.legend_formula.pack(pady=5)
        self.legend_params = tk.Label(
            self.legend_frame,
            text=f"U: {self.nu}, V: {self.nv}\nМасштаб: {self.scale:.1f}\nШаг сетки: 1.0\nAlpha: {self.alpha}\n Beta: {self.b}",
            font=("Helvetica", 10),
            bg='lightgray',
            justify='center'
        )
        self.legend_params.pack(pady=5)

        # Кнопка для скрытия/показа
        self.legend_button = tk.Button(self.control_top_frame, text="Скрыть", command=self.toggle_legend)
        self.legend_button.pack(side='right', padx=5)

        # Привязка событий
        self.canvas.bind('<MouseWheel>', self.zoom)  # Windows
        self.canvas.bind('<Button-4>', lambda e: self.zoom_manual(1.1))  # Linux/Mac (прокрутка вверх)
        self.canvas.bind('<Button-5>', lambda e: self.zoom_manual(0.9))  # Linux/Mac (прокрутка вниз)
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.root.bind('<KeyPress-Shift_L>', self.shift_press)
        self.root.bind('<KeyRelease-Shift_L>', self.shift_release)
        self.root.bind('<Key>', self.rotate)
        self.draw()

    def draw(self):
        self.canvas.delete('all')
        view_matrix = Matrix.look_at(self.camera_pos, self.look_at, self.up)
        rot_x = Matrix.rotation_x(self.rotation_x)
        rot_y = Matrix.rotation_y(self.rotation_y)
        rot_z = Matrix.rotation_z(self.rotation_z)
        rotation_matrix = rot_y * rot_x * rot_z
        transform = view_matrix * rotation_matrix
        # Трансформация всех точек графика
        transformed_points = [transform * p for p in self.all_points]

        # Вызов рендеринга треугольников
        render_triangles(
            self.canvas,
            transformed_points,
            self.triangles,
            self.scale,
            z_to_color,
            int(self.start_r.get()), int(self.start_g.get()), int(self.start_b.get()),
            int(self.end_r.get()), int(self.end_g.get()), int(self.end_b.get())
        )

        # Адаптация осей под данные
        max_coord = max(max(abs(p.x), abs(p.y), abs(p.z)) for p in transformed_points)
        axis_length = max(4.5, max_coord * 1.2)  # Минимум 4.5, но адаптируется под максимальную координату

        # Трансформация осей с адаптированным размером
        origin = transform * Vector3(0, 0, 0)
        x_axis_pos = transform * Vector3(axis_length, 0, 0)
        x_axis_neg = transform * Vector3(-axis_length, 0, 0)
        y_axis_pos = transform * Vector3(0, axis_length, 0)
        y_axis_neg = transform * Vector3(0, -axis_length, 0)
        z_axis_pos = transform * Vector3(0, 0, axis_length)
        z_axis_neg = transform * Vector3(0, 0, -axis_length)

        # Вычисление min и max Z для графика
        min_z = min(p.z for p in transformed_points)
        max_z = max(p.z for p in transformed_points)

        # Формирование треугольников с учётом Z-порядка
        triangles = []
        for tri in self.triangles:
            p0, p1, p2 = [transformed_points[idx] for idx in tri]
            avg_z = (p0.z + p1.z + p2.z) / 3
            triangles.append((avg_z, tri))
        triangles.sort(key=lambda x: x[0], reverse=True)

        # Единая функция проекции
        def project(point):
            if 1 - 0.02 * point.z == 0:  # Избежание деления на ноль
                return (400, 300)  # Центр канваса как запасной вариант
            x_2d = 400 + self.scale * point.x / (1 - 0.02 * point.z)
            y_2d = 300 - self.scale * point.y / (1 - 0.02 * point.z)
            return (x_2d, y_2d)

        # Проекция осей
        origin_2d = project(origin)
        x_pos_2d = project(x_axis_pos)
        x_neg_2d = project(x_axis_neg)
        y_pos_2d = project(y_axis_pos)
        y_neg_2d = project(y_axis_neg)
        z_pos_2d = project(z_axis_pos)
        z_neg_2d = project(z_axis_neg)

        # Отрисовка осей (без подписей)
        self.canvas.create_line(origin_2d[0], origin_2d[1], x_pos_2d[0], x_pos_2d[1], fill='red', width=2, arrow=tk.LAST)
        self.canvas.create_line(origin_2d[0], origin_2d[1], x_neg_2d[0], x_neg_2d[1], fill='red', width=2)
        self.canvas.create_line(origin_2d[0], origin_2d[1], y_pos_2d[0], y_pos_2d[1], fill='green', width=2, arrow=tk.LAST)
        self.canvas.create_line(origin_2d[0], origin_2d[1], y_neg_2d[0], y_neg_2d[1], fill='green', width=2)
        self.canvas.create_line(origin_2d[0], origin_2d[1], z_pos_2d[0], z_pos_2d[1], fill='blue', width=2, arrow=tk.LAST)
        self.canvas.create_line(origin_2d[0], origin_2d[1], z_neg_2d[0], z_neg_2d[1], fill='blue', width=2)

        # Единичные отрезки с подписями на концах
        unit_x_pos = transform * Vector3(1, 0, 0)
        unit_x_neg = transform * Vector3(-1, 0, 0)
        unit_y_pos = transform * Vector3(0, 1, 0)
        unit_y_neg = transform * Vector3(0, -1, 0)
        unit_z_pos = transform * Vector3(0, 0, 1)
        unit_z_neg = transform * Vector3(0, 0, -1)
        unit_x_pos_2d = project(unit_x_pos)
        unit_x_neg_2d = project(unit_x_neg)
        unit_y_pos_2d = project(unit_y_pos)
        unit_y_neg_2d = project(unit_y_neg)
        unit_z_pos_2d = project(unit_z_pos)
        unit_z_neg_2d = project(unit_z_neg)

        self.canvas.create_line(unit_x_pos_2d[0], unit_x_pos_2d[1] - 8, unit_x_pos_2d[0], unit_x_pos_2d[1] + 8, fill='red', width=3)
        self.canvas.create_line(unit_x_neg_2d[0], unit_x_neg_2d[1] - 8, unit_x_neg_2d[0], unit_x_neg_2d[1] + 8, fill='red', width=3)
        self.canvas.create_line(unit_y_pos_2d[0] - 8, unit_y_pos_2d[1], unit_y_pos_2d[0] + 8, unit_y_pos_2d[1], fill='green', width=3)
        self.canvas.create_line(unit_y_neg_2d[0] - 8, unit_y_neg_2d[1], unit_y_neg_2d[0] + 8, unit_y_neg_2d[1], fill='green', width=3)
        self.canvas.create_line(unit_z_pos_2d[0] - 8, unit_z_pos_2d[1], unit_z_pos_2d[0] + 8, unit_z_pos_2d[1], fill='blue', width=3)
        self.canvas.create_line(unit_z_neg_2d[0] - 8, unit_z_neg_2d[1], unit_z_neg_2d[0] + 8, unit_z_neg_2d[1], fill='blue', width=3)

        # Подписи единичных отрезков на концах с шагом 1.0
        self.canvas.create_text(unit_x_pos_2d[0], unit_x_pos_2d[1] - 15, text='1.0', fill='red', font=("Helvetica", 10))
        self.canvas.create_text(unit_x_neg_2d[0], unit_x_neg_2d[1] - 15, text='-1.0', fill='red', font=("Helvetica", 10))
        self.canvas.create_text(unit_y_pos_2d[0] + 15, unit_y_pos_2d[1], text='1.0', fill='green', font=("Helvetica", 10))
        self.canvas.create_text(unit_y_neg_2d[0] + 15, unit_y_neg_2d[1], text='-1.0', fill='green', font=("Helvetica", 10))
        self.canvas.create_text(unit_z_pos_2d[0] + 15, unit_z_pos_2d[1], text='1.0', fill='blue', font=("Helvetica", 10))
        self.canvas.create_text(unit_z_neg_2d[0] + 15, unit_z_neg_2d[1], text='-1.0', fill='blue', font=("Helvetica", 10))

        # Сетка с шагом 1.0
        grid_step = 1.0
        for i in range(int(-axis_length / grid_step), int(axis_length / grid_step) + 1):
            start = transform * Vector3(-axis_length, i * grid_step, 0)
            end = transform * Vector3(axis_length, i * grid_step, 0)
            start_2d = project(start)
            end_2d = project(end)
            self.canvas.create_line(start_2d[0], start_2d[1], end_2d[0], end_2d[1], fill='gray', dash=(4, 4))
            start = transform * Vector3(i * grid_step, -axis_length, 0)
            end = transform * Vector3(i * grid_step, axis_length, 0)
            start_2d = project(start)
            end_2d = project(end)
            self.canvas.create_line(start_2d[0], start_2d[1], end_2d[0], end_2d[1], fill='gray', dash=(4, 4))

        for i in range(int(-axis_length / grid_step), int(axis_length / grid_step) + 1):
            start = transform * Vector3(-axis_length, 0, i * grid_step)
            end = transform * Vector3(axis_length, 0, i * grid_step)
            start_2d = project(start)
            end_2d = project(end)
            self.canvas.create_line(start_2d[0], start_2d[1], end_2d[0], end_2d[1], fill='gray', dash=(4, 4))
            start = transform * Vector3(i * grid_step, 0, -axis_length)
            end = transform * Vector3(i * grid_step, 0, axis_length)
            start_2d = project(start)
            end_2d = project(end)
            self.canvas.create_line(start_2d[0], start_2d[1], end_2d[0], end_2d[1], fill='gray', dash=(4, 4))

        for i in range(int(-axis_length / grid_step), int(axis_length / grid_step) + 1):
            start = transform * Vector3(0, -axis_length, i * grid_step)
            end = transform * Vector3(0, axis_length, i * grid_step)
            start_2d = project(start)
            end_2d = project(end)
            self.canvas.create_line(start_2d[0], start_2d[1], end_2d[0], end_2d[1], fill='gray', dash=(4, 4))
            start = transform * Vector3(0, i * grid_step, -axis_length)
            end = transform * Vector3(0, i * grid_step, axis_length)
            start_2d = project(start)
            end_2d = project(end)
            self.canvas.create_line(start_2d[0], start_2d[1], end_2d[0], end_2d[1], fill='gray', dash=(4, 4))

        # Отрисовка графика
        for avg_z, tri in triangles:
            points_2d = [project(transformed_points[idx]) for idx in tri]
            color = z_to_color(avg_z, min_z, max_z, self.color_factor, int(self.start_r.get()), int(self.start_g.get()), int(self.start_b.get()), int(self.end_r.get()), int(self.end_g.get()), int(self.end_b.get()))
            self.canvas.create_polygon(points_2d, fill=color, outline='black')
            
    def zoom(self, event):
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale *= 0.9
        self.scale_slider.set(self.scale)
        self.update_legend()
        self.draw()

    def zoom_manual(self, factor):
        self.scale *= factor
        self.scale_slider.set(self.scale)
        self.update_legend()
        self.draw()

    def update_scale(self, value):
        self.scale = float(value)
        self.update_legend()
        self.draw()

    def start_drag(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        step = math.radians(0.5)
        if self.shift_pressed:
            self.rotation_z += dx * step  
        else:
            self.rotation_y += dx * step  
            self.rotation_x += dy * step  
        self.last_x = event.x
        self.last_y = event.y
        self.draw()

    def shift_press(self, event):
        self.shift_pressed = True

    def shift_release(self, event):
        self.shift_pressed = False

    def rotate(self, event):
        step = math.radians(5)
        if event.keysym == 'Left':
            self.rotation_y += step
        elif event.keysym == 'Right':
            self.rotation_y -= step
        elif event.keysym == 'Up':
            self.rotation_x -= step
        elif event.keysym == 'Down':
            self.rotation_x += step
        self.draw()

    def update_polygons(self):
        self.nu = self.nu_var.get()
        self.nv = self.nv_var.get()
        self.points = generate_grid(self.nu, self.nv, sea_shell, self.alpha, self.b)
        self.all_points = [self.points[i][j] for i in range(self.nu) for j in range(self.nv)]
        self.triangles = generate_triangles(self.nu, self.nv)
        self.update_legend()
        self.draw()

    def toggle_legend(self):
        if self.legend_frame.winfo_ismapped():
            self.legend_frame.place_forget()
            self.legend_button.config(text="Показать описание")
        else:
            self.legend_frame.place(x=10, y=45, width=250, height=180)
            self.legend_button.config(text="Скрыть описание")
            self.update_legend()

    def update_legend(self):
        if self.legend_frame.winfo_ismapped():
            self.legend_params.config(text=f"U: {self.nu}, V: {self.nv}\nМасштаб: {self.scale:.1f}\nШаг сетки: 1.0\nAlpha: {self.alpha}, Beta: {self.b}")

# Запуск приложения
root = tk.Tk()
root.title("Sea Shell Surface Plotter")
plotter = SeaShellPlotter(root)
root.mainloop()
