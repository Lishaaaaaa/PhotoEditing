import cv2
from tkinter import Tk, filedialog, Scale, HORIZONTAL, Radiobutton, IntVar
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from rembg import remove  # Ensure you have the rembg package installed
  # 1920*1080
class FrontEnd:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Editing Application")

        # Apply theme and create styles
        style = ttk.Style()
        style.theme_use('clam')  # You can choose 'clam', 'alt', 'default', 'classic'
        
        style.configure('TFrame', background='#3c3f41') # for frame gray color
        style.configure('TButton', font=('Helvetica', 12), background='#2b2b2b', foreground='#ffffff', padding=10)
        style.map('TButton', background=[('active', '#4b4b4b')])
        style.configure('TLabel', font=('Helvetica', 12), background='#3c3f41', foreground='#ffffff')
        style.configure('TScale', background='#3c3f41')
        style.configure('TRadiobutton', font=('Helvetica', 12), background='#3c3f41', foreground='#ffffff')
        
        self.root.configure(background='#3c3f41')

        # Initialize main UI components
        self.frame_main = ttk.Frame(root, padding="20")
        self.frame_main.grid(row=0, column=0, sticky="nsew")

        self.frame_menu = ttk.Frame(self.frame_main)
        self.frame_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        self.canvas = tk.Canvas(self.frame_main, bg='#ffffff', highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.side_frame = None
        self.original_image = None
        self.edited_image = None
        self.filtered_image = None

        self.blur_type = IntVar(value=1)  # Default to Gaussian blur

        # Setup UI buttons
        self.setup_buttons()

        # Configure grid weight
        self.frame_main.grid_rowconfigure(0, weight=1)
        self.frame_main.grid_columnconfigure(0, weight=1)
        self.frame_menu.grid_rowconfigure(0, weight=1)
        self.frame_menu.grid_columnconfigure(0, weight=1)
        self.frame_menu.grid_columnconfigure(1, weight=1)

    def setup_buttons(self):
        button_frame = ttk.Frame(self.frame_menu)
        button_frame.grid(row=0, column=0, columnspan=6, sticky='nsew')

        # Configure grid to expand properly
        self.frame_menu.grid_rowconfigure(0, weight=1)
        self.frame_menu.grid_columnconfigure(0, weight=1)
        self.frame_menu.grid_columnconfigure(1, weight=1)
        self.frame_menu.grid_columnconfigure(2, weight=1)
        self.frame_menu.grid_columnconfigure(3, weight=1)
        self.frame_menu.grid_columnconfigure(4, weight=1)
        self.frame_menu.grid_columnconfigure(5, weight=1)
        self.frame_menu.grid_columnconfigure(6, weight=1)

        button_frame.pack(fill='both', expand=True)

        ttk.Button(button_frame, text="Load Image", command=self.load_image_action).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="Filters", command=self.filter_action).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="Rotate", command=self.rotate_action).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="Flip", command=self.flip_action).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="Adjust", command=self.adjust_action).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="Blur", command=self.blur_adjust_action).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="Save", command=self.save_action).pack(pady=5, fill='x')
        ttk.Button(button_frame, text="Revert Changes", command=self.revert_changes).pack(pady=5, fill='x')

    def load_image_action(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", ".jpg;.jpeg;.png;.bmp")])
        if filepath:
            self.original_image = cv2.imread(filepath)
            self.edited_image = self.original_image.copy()
            self.display_image(self.edited_image)
            self.filename = filepath.split('/')[-1]

    def refresh_side_frame(self):
        if self.side_frame is not None:
            self.side_frame.grid_forget()

        self.side_frame = ttk.Frame(self.frame_main)
        self.side_frame.grid(row=0, column=2, padx=20, pady=20, sticky="ns")

    def save_action(self):
        if self.filtered_image is not None:
            filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", ".png"), ("JPEG files", ".jpg;.jpeg"), ("All files", ".*")])
            if filepath:
                cv2.imwrite(filepath, self.filtered_image)
        else:
            print("No image to save.")
    
    def filter_action(self):
        self.refresh_side_frame()

        filters = [
            ("Histogram Equalization", self.histogram_equalization_action),
            ("Sharpen", self.sharpen_action),
            ("Edge Detection", self.edge_detection_action),
            ("Color Enhancement", self.color_enhancement_action),
            ("Background Removal", self.background_removal_action)
        ]

        for idx, (text, command) in enumerate(filters):
            ttk.Button(self.side_frame, text=text, command=command).grid(row=idx, column=0, padx=5, pady=5, sticky="ew")

    def revert_changes(self):
        if self.original_image is not None:
            self.edited_image = self.original_image.copy()
            self.filtered_image = None
            self.display_image(self.edited_image)
 
    def histogram_equalization_action(self):
        img_gray = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2GRAY)
        equ = cv2.equalizeHist(img_gray)
        self.filtered_image = cv2.cvtColor(equ, cv2.COLOR_GRAY2BGR)
        self.display_image(self.filtered_image)

    def rotate_image(self, image, angle):
        center = (image.shape[1] // 2, image.shape[0] // 2)  # Center of rotation  
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)  # Rotation matrix
        rotated = cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]))
        return rotated

    def flip_image(self, image, direction):
        if direction == 'horizontal':
            return cv2.flip(image, 1)
        elif direction == 'vertical':
            return cv2.flip(image, 0)
        else:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")

    def sharpen_action(self):
        kernel = np.array([[0, -1, 0], 
                           [-1, 5, -1], 
                           [0, -1, 0]])
        self.filtered_image =  cv2.filter2D(self.edited_image, -1, kernel)
        self.display_image(self.filtered_image)

    def gaussian_blur_image(self, image, kernel_size):
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    def average_blur_image(self, image, kernel_size):
        return cv2.blur(image, (kernel_size, kernel_size))

    def median_blur_image(self, image, kernel_size):
        return cv2.medianBlur(image, kernel_size)

    def edge_detection_action(self):
        edges = cv2.Canny(self.edited_image, 100, 200)
        self.filtered_image =  cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.display_image(self.filtered_image)

    def adjust_brightness_contrast(self, image, brightness=0, contrast=0):
        beta = brightness
        alpha = (contrast + 100) / 100.0
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    def color_enhancement_action(self):
        hsv = cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2HSV)
        hsv[:, :, 2] = cv2.equalizeHist(hsv[:, :, 2])
        self.filtered_image =  cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        self.display_image(self.filtered_image)

    def background_removal_action(self):
        if self.edited_image.size == 0:
            raise ValueError("The input image is empty.")
        input_image = Image.fromarray(cv2.cvtColor(self.edited_image, cv2.COLOR_BGR2RGB))
        output_image = remove(input_image)
        output_image_np = np.array(output_image)
        self.filtered_image = cv2.cvtColor(output_image_np, cv2.COLOR_RGBA2BGR)
        self.display_image(self.filtered_image)

    def blur_action(self):
        self.filtered_image = self.blur_image(self.edited_image, 5)
        self.display_image(self.filtered_image)

    def rotate_action(self):
        self.refresh_side_frame()
  
        ttk.Label(self.side_frame, text="Angle").grid(row=0, column=0, padx=5, pady=5)
        self.angle_slider = Scale(self.side_frame, from_=-180, to=180, orient=HORIZONTAL, command=self.rotate_image_action)
        self.angle_slider.grid(row=1, column=0, padx=5, pady=5)
        self.angle_slider.set(0)

    def rotate_image_action(self, angle):
        angle = float(angle)
        self.filtered_image = self.rotate_image(self.edited_image, angle)
        self.display_image(self.filtered_image)

    def flip_action(self):
        self.refresh_side_frame()
        
        ttk.Button(self.side_frame, text="Flip Horizontal", command=self.flip_horizontal_action).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.side_frame, text="Flip Vertical", command=self.flip_vertical_action).grid(row=1, column=0, padx=5, pady=5)

    def flip_horizontal_action(self):
        self.filtered_image = self.flip_image(self.edited_image, 'horizontal')
        self.display_image(self.filtered_image)

    def flip_vertical_action(self):
        self.filtered_image = self.flip_image(self.edited_image, 'vertical')
        self.display_image(self.filtered_image)

    def adjust_action(self):
        self.refresh_side_frame()

        ttk.Label(self.side_frame, text="Brightness").grid(row=0, column=0, padx=5, pady=5)
        self.brightness_slider = Scale(self.side_frame, from_=-100, to=100, orient=HORIZONTAL, command=self.brightness_action)
        self.brightness_slider.grid(row=1, column=0, padx=5, pady=5)
        self.brightness_slider.set(0)

        ttk.Label(self.side_frame, text="Contrast").grid(row=2, column=0, padx=5, pady=5)
        self.contrast_slider = Scale(self.side_frame, from_=-100, to=100, orient=HORIZONTAL, command=self.contrast_action)
        self.contrast_slider.grid(row=3, column=0, padx=5, pady=5)
        self.contrast_slider.set(0)

    def brightness_action(self, value):
        brightness = int(value)
        contrast = int(self.contrast_slider.get())
        self.filtered_image = self.adjust_brightness_contrast(self.edited_image, brightness, contrast)
        self.display_image(self.filtered_image)

    def contrast_action(self, value):
        contrast = int(value)
        brightness = int(self.brightness_slider.get())
        self.filtered_image = self.adjust_brightness_contrast(self.edited_image, brightness, contrast)
        self.display_image(self.filtered_image)

    def blur_adjust_action(self):
        self.refresh_side_frame()

        ttk.Radiobutton(self.side_frame, text="Gaussian Blur", variable=self.blur_type, value=1).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.side_frame, text="Average Blur", variable=self.blur_type, value=2).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.side_frame, text="Median Blur", variable=self.blur_type, value=3).grid(row=2, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(self.side_frame, text="Kernel Size").grid(row=3, column=0, padx=5, pady=5)
        self.kernel_size_slider = Scale(self.side_frame, from_=1, to=21, orient=HORIZONTAL, command=self.blur_adjust_action_execute)
        self.kernel_size_slider.grid(row=4, column=0, padx=5, pady=5)
        self.kernel_size_slider.set(5)

    def blur_adjust_action_execute(self, value):
        kernel_size = int(value)
        if kernel_size % 2 == 0:  # Ensure kernel size is odd
            kernel_size += 1
        
        if self.blur_type.get() == 1:
            self.filtered_image = self.gaussian_blur_image(self.edited_image, kernel_size)
        elif self.blur_type.get() == 2:
            self.filtered_image = self.average_blur_image(self.edited_image, kernel_size)
        elif self.blur_type.get() == 3:
            self.filtered_image = self.median_blur_image(self.edited_image, kernel_size)
        
        self.display_image(self.filtered_image)

    def display_image(self, image=None):
        self.canvas.delete("all")
        if image is None:
            image = self.edited_image

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, _ = image.shape
        ratio = height / width

        # Set the maximum dimensions for the display image
        max_width = 800
        max_height = 900

        if width > max_width or height > max_height:
            if ratio < 1:
                new_width = max_width
                new_height = int(new_width * ratio)
            else:
                new_height = max_height
                new_width = int(new_height / ratio)
        else:
            new_width = width
            new_height = height

        self.new_image = cv2.resize(image, (new_width, new_height))
        self.new_image = ImageTk.PhotoImage(Image.fromarray(self.new_image))

        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(new_width / 2, new_height / 2, image=self.new_image)

if __name__ == "__main__":
    mainWindow = Tk()
    app = FrontEnd(mainWindow)
    mainWindow.mainloop()