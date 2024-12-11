import tkinter as tk
from tkinter import ttk, colorchooser
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D

class EmotionVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Emotion Visualizer")
        
        # Visualization para
        self.elev = 30
        self.azim = 45
        self.auto_rotate = False
        self.color_theme = 'plasma'
        self.background_color = 'black'
        self.rotation_time = 0
        
        # Optimization P
        self.is_rotating = False
        self.mesh_density_normal = 100
        self.mesh_density_interactive = 50
        
        #  Emotions
        self.emotions = {
            "Happy": {"count": 0, "position": (0, np.pi/3), "color": "#FFD700"},          
            "Sad": {"count": 0, "position": (0, 2*np.pi/3), "color": "#4169E1"},          
            "Angry": {"count": 0, "position": (np.pi/2, np.pi/4), "color": "#FF4500"},    
            "Calm": {"count": 0, "position": (3*np.pi/2, np.pi/4), "color": "#98FB98"},   
            "Anxious": {"count": 0, "position": (np.pi/2, 3*np.pi/4), "color": "#DDA0DD"},
            "Peaceful": {"count": 0, "position": (3*np.pi/2, 3*np.pi/4), "color": "#87CEEB"},
            "Excited": {"count": 0, "position": (np.pi/4, np.pi/6), "color": "#FFA500"},   
            "Bored": {"count": 0, "position": (7*np.pi/4, 5*np.pi/6), "color": "#808080"},
            "Jealous": {"count": 0, "position": (2*np.pi/3, np.pi/2), "color": "#32CD32"},
            "In Love": {"count": 0, "position": (4*np.pi/3, np.pi/2), "color": "#FF69B4"},
            "Tired": {"count": 0, "position": (np.pi, np.pi/2), "color": "#8B4513"},       
            "Confident": {"count": 0, "position": (0, np.pi/6), "color": "#FFD700"},       
            "Insecure": {"count": 0, "position": (0, 5*np.pi/6), "color": "#483D8B"},      
            "Grateful": {"count": 0, "position": (np.pi/3, np.pi/3), "color": "#9370DB"},  
            "Stressed": {"count": 0, "position": (5*np.pi/3, 2*np.pi/3), "color": "#CD5C5C"}
        }

        # main
        self.main_frame = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # left control P
        self.create_control_panel()
        
        # visualization P
        self.create_visualization_panel()

    def create_control_panel(self):
        control_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(control_frame)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Emotion.TButton", padding=5)
        
        # Controls section
        controls_label = ttk.Label(control_frame, text="Controls", font=('Helvetica', 12, 'bold'))
        controls_label.pack(pady=5)
        
        # R controls
        rotation_frame = ttk.LabelFrame(control_frame, text="Rotation Controls")
        rotation_frame.pack(pady=5, padx=5, fill="x")
        
        # Auto R
        self.auto_rotate_var = tk.BooleanVar(value=False)
        auto_rotate_cb = ttk.Checkbutton(rotation_frame, text="Auto Rotate", 
                                       variable=self.auto_rotate_var,
                                       command=self.toggle_auto_rotate)
        auto_rotate_cb.pack(pady=2)
        
        # Manual R sliders
        ttk.Label(rotation_frame, text="Elevation:").pack()
        self.elev_slider = ttk.Scale(rotation_frame, from_=0, to=180, 
                                   orient="horizontal", command=self.update_view)
        self.elev_slider.set(30)
        self.elev_slider.pack(fill="x", padx=5)
        
        ttk.Label(rotation_frame, text="Azimuth:").pack()
        self.azim_slider = ttk.Scale(rotation_frame, from_=0, to=360, 
                                   orient="horizontal", command=self.update_view)
        self.azim_slider.set(45)
        self.azim_slider.pack(fill="x", padx=5)
        
        # Reset B
        ttk.Button(control_frame, text="Reset All Emotions", 
                  command=self.reset_emotions).pack(pady=5)
        
        # Theme selection
        theme_frame = ttk.LabelFrame(control_frame, text="Visual Theme")
        theme_frame.pack(pady=5, padx=5, fill="x")
        
        themes = ['plasma', 'viridis', 'magma', 'inferno', 'cividis']
        self.theme_var = tk.StringVar(value='plasma')
        for theme in themes:
            ttk.Radiobutton(theme_frame, text=theme.capitalize(), 
                           variable=self.theme_var, value=theme,
                           command=lambda: self.update_visualization(False)).pack(anchor="w")
        
        # BG color B
        ttk.Button(theme_frame, text="Change Background Color",
                  command=self.change_background_color).pack(pady=5)
        
        # Emotions section
        emotions_label = ttk.Label(control_frame, text="Emotions", font=('Helvetica', 12, 'bold'))
        emotions_label.pack(pady=5)
        
        # scrollable frame for emotion B
        canvas = tk.Canvas(control_frame)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Emotion B section pack
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.create_buttons()

    def create_buttons(self):
        # Clear existing  B
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Add emotion B
        for emotion in self.emotions.keys():
            btn = ttk.Button(
                self.scrollable_frame,
                text=f"{emotion} ({self.emotions[emotion]['count']})",
                command=lambda e=emotion: self.increment_emotion(e)
            )
            btn.pack(pady=2, padx=10, fill=tk.X)

    def create_visualization_panel(self):
        self.viz_frame = ttk.Frame(self.main_frame)
        self.main_frame.add(self.viz_frame)
        
        self.fig = plt.Figure(figsize=(8, 8), facecolor=self.background_color)
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
        self.canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # mouse R
        self.canvas_plot.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas_plot.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas_plot.mpl_connect('button_release_event', self.on_mouse_release)
        
        self.mouse_pressed = False
        self.last_x = 0
        self.last_y = 0
        
        self.update_visualization(False)

    def increment_emotion(self, emotion):
        self.emotions[emotion]['count'] += 1
        self.create_buttons()
        self.update_visualization(False)

    def reset_emotions(self):
        for emotion in self.emotions:
            self.emotions[emotion]['count'] = 0
        self.create_buttons()
        self.update_visualization(False)

    def toggle_auto_rotate(self):
        self.auto_rotate = self.auto_rotate_var.get()
        if self.auto_rotate:
            self.rotation_time = 0  # Reset rotation time when starting
            self.update_rotation()

    def update_rotation(self):
        if self.auto_rotate:
            # Increment t para
            self.rotation_time += 0.05
            
            # Calculate both angles
            self.azim = (self.rotation_time * 50) % 360  # Horizontal R
            self.elev = 30 + 45 * np.sin(self.rotation_time)  # Vertical R
            
            self.azim_slider.set(self.azim)
            self.elev_slider.set(self.elev)
            
            self.update_visualization(True)
            self.root.after(50, self.update_rotation)

    def update_view(self, _=None):
        self.elev = self.elev_slider.get()
        self.azim = self.azim_slider.get()
        self.update_visualization(True)

    def change_background_color(self):
        color = colorchooser.askcolor(title="Choose background color")[1]
        if color:
            self.background_color = color
            self.fig.set_facecolor(self.background_color)
            self.update_visualization(False)

    def on_mouse_press(self, event):
        self.mouse_pressed = True
        self.last_x = event.x
        self.last_y = event.y

    def on_mouse_move(self, event):
        if self.mouse_pressed and hasattr(event, 'inaxes') and event.inaxes:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            
            self.azim = (self.azim + dx) % 360
            self.elev = np.clip(self.elev + dy, 0, 180)
            
            self.azim_slider.set(self.azim)
            self.elev_slider.set(self.elev)
            
            self.last_x = event.x
            self.last_y = event.y
            
            self.update_visualization(True)

    def on_mouse_release(self, event):
        self.mouse_pressed = False
        self.update_visualization(False)

    def gaussian_deformation(self, theta, phi, center_theta, center_phi, amplitude, sigma=0.5):
        dist = np.arccos(np.clip(np.sin(center_phi) * np.sin(phi) + 
                        np.cos(center_phi) * np.cos(phi) * np.cos(theta - center_theta), -1, 1))
        return amplitude * np.exp(-(dist**2) / (2 * sigma**2))

    def update_visualization(self, interactive=False):
        self.fig.clear()
        ax = self.fig.add_subplot(111, projection='3d')
        
        # Background color
        ax.set_facecolor(self.background_color)
        
        # lower mesh density
        mesh_density = self.mesh_density_interactive if interactive else self.mesh_density_normal
        
        # Sphere mesh
        phi = np.linspace(0, np.pi, mesh_density)
        theta = np.linspace(0, 2 * np.pi, mesh_density)
        phi, theta = np.meshgrid(phi, theta)
        
        # Base sphere radius
        r = np.ones_like(phi)
        
        # Optimize deformation calculation
        if not interactive or sum(data['count'] for data in self.emotions.values()) > 0:
            for emotion, data in self.emotions.items():
                if data['count'] > 0:
                    center_theta, center_phi = data['position']
                    r += self.gaussian_deformation(
                        theta, phi, center_theta, center_phi,
                        amplitude=0.2 * data['count'],
                        sigma=0.4
                    )
        
        # Convert to cartesian coordinates
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # Create surface plot with optimized settings
        surf = ax.plot_surface(x, y, z,
                             cmap=self.theme_var.get(),
                             antialiased=not interactive,
                             alpha=0.9,
                             shade=not interactive)
        
        # Optimize view settings
        ax.set_box_aspect([1,1,1])
        ax.set_axis_off()
        ax.view_init(elev=self.elev, azim=self.azim)
        
        # Title when not interactive
        if not interactive:
            ax.set_title("Emotional Landscape", 
                        color='white' if self.background_color == 'black' else 'black',
                        pad=20, fontsize=14, fontweight='bold')
            
        
        self.canvas_plot.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionVisualizer(root)
    root.geometry("1200x800")
    root.mainloop()