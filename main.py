import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np
import threading

class DitherEditor(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("B&W Dithering Editor")
		self.geometry("800x600")

		self.original_image = None
		self.grayscale_image = None
		self.dithered_image = None
		self.thread = threading.Thread(None)

		# Create GUI elements
		self.create_widgets()
		self.columnconfigure((0, 1), weight = 1)
		self.rowconfigure((0, 2), weight = 1)
		self.rowconfigure((1), weight = 2)
		self.rowconfigure((3), weight = 10)

	def create_widgets(self):
		# Image path entry and browse button
		path_frame = tk.Frame(self)
		path_frame.grid(row=0, column=0, columnspan=2)
		self.path_entry_label = tk.Label(path_frame, text="file: ")
		self.path_entry = tk.Entry(path_frame, width=50)
		self.browse_button = tk.Button(path_frame, text="Browse", command=self.browse_file)
		
		self.path_entry_label.grid(row=0, column=0)
		self.path_entry.grid(row=0, column=1, columnspan=2)
		self.browse_button.grid(row=0, column=3)

		def deactivate_threshold():
			self.threshold_entry.grid_remove()
			self.threshold_entry_label.grid_remove()
		def activate_threshold():
			self.threshold_entry.grid()
			self.threshold_entry_label.grid()

			
		# Grayscale options
		options_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)
		options_frame.grid(row=1, column=0)
		self.grayscale_var = tk.StringVar()
		self.grayscale_var.set("average")
		self.lightness_grayscale_radio = tk.Radiobutton(options_frame, text="Lightness Grayscale Method", variable=self.grayscale_var, value="lightness")
		self.average_grayscale_radio = tk.Radiobutton(options_frame, text="Average Grayscale Method", variable=self.grayscale_var, value="average")
		self.luminosity_grayscale_radio = tk.Radiobutton(options_frame, text="Luminosity Grayscale Method", variable=self.grayscale_var, value="luminosity")
		
		self.lightness_grayscale_radio.grid(row=0, column=0, padx=5, pady=5)
		self.average_grayscale_radio.grid(row=1, column=0, padx=5, pady=5)
		self.luminosity_grayscale_radio.grid(row=2, column=0, padx=5, pady=5)

		# Dithering options
		options_frame = tk.Frame(self, highlightbackground="black", highlightthickness=1)
		options_frame.grid(row=1, column=1)
		self.conversion_var = tk.StringVar()
		self.conversion_var.set("threshold")
		self.threshold_radio = tk.Radiobutton(options_frame, text="Threshold Dithering", variable=self.conversion_var, value="threshold", command=activate_threshold)
		self.random_radio = tk.Radiobutton(options_frame, text="Random Dithering", variable=self.conversion_var, value="random", command=deactivate_threshold)
		self.threshold_entry_label = tk.Label(options_frame, text="Threshold: ")
		self.threshold_entry = tk.Entry(options_frame, width=5)
		self.threshold_entry.insert(0, "128")
		
		self.threshold_radio.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
		self.random_radio.grid(row=0, column=2, columnspan=2, padx=5, pady=5)
		self.threshold_entry_label.grid(row=1, column=0, pady=5)
		self.threshold_entry.grid(row=1, column=1, pady=5)

		# Generate and Save buttons
		button_frame = tk.Frame(self)
		button_frame.grid(row=2, column=0, columnspan=2)
		self.generate_button = tk.Button(button_frame, text="Generate", command=self.generate_dithered_image)
		self.save_button = tk.Button(button_frame, text="Save", command=self.save_dithered_image)
		
		self.generate_button.grid(row=0, column=1, padx=5)
		self.save_button.grid(row=0, column=2, padx=5)

		# Image display
		image_frame = tk.Frame(self)
		image_frame.grid(row=3, column=0, columnspan=2)
		self.original_label = tk.Label(image_frame, text="Original", compound=tk.BOTTOM)
		self.dithered_label = tk.Label(image_frame, text="Dithered", compound=tk.BOTTOM)
		
		self.original_label.grid(row=0, column=0, columnspan=2, padx=10)
		self.dithered_label.grid(row=0, column=2, columnspan=2, padx=10)

	def browse_file(self):
		file_path = filedialog.askopenfilename()
		self.path_entry.delete(0, tk.END)
		self.path_entry.insert(0, file_path)
		self.load_original_image(file_path)

	def load_original_image(self, file_path):
		try:
			self.original_image = Image.open(file_path)
			self.display_image(self.original_image, self.original_label)
		except Exception as e:
			print(f"Error loading image: {e}")

	def display_image(self, image, label):
		max_width, max_height = 350, 350  # Maximum allowed size for display
		original_width, original_height = image.size

		# Calculate the new dimensions while maintaining the aspect ratio
		aspect_ratio = original_width / original_height
		new_width = min(max_width, original_width)
		new_height = int(new_width / aspect_ratio)

		if new_height > max_height:
			new_height = max_height
			new_width = int(new_height * aspect_ratio)

		image = image.resize((new_width, new_height))
		photo = ImageTk.PhotoImage(image)
		label.configure(image=photo)
		label.image = photo

	def generate_dithered_image(self):
		
		if self.original_image is None:
			return
		elif self.thread.is_alive():
			return

		grayscale_method = self.grayscale_var.get()
		conversion_method = self.conversion_var.get()
		threshold = int(self.threshold_entry.get())

		self.grayscale(grayscale_method)
		self.thread = threading.Thread(target=self.dither_image, args=(conversion_method, threshold))
		self.thread.start()
		self.thread.join()
		self.display_image(self.dithered_image, self.dithered_label)
		
	def grayscale(self, method):
		original_image = self.original_image.convert("RGB")
		pixels = np.array(original_image)
		red, green, blue = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
		if method == "average":
			grayscaled = pixels.mean(axis=2)
		elif method == "luminosity":
			grayscaled = (0.2126 * red + 0.7152 * green + 0.0722 * blue)
		else:
			grayscaled = ((np.maximum(red, green, blue) + np.minimum(red, green, blue)) / 2)
		self.grayscale_image = grayscaled

	def dither_image(self, conversion_method, threshold):
		if conversion_method == "threshold":
			self.dithered_image = self.threshold_dithering(self.grayscale_image, threshold)
		else:
			self.dithered_image = self.random_dithering(self.grayscale_image)

	def threshold_dithering(self, image, threshold):
		dithered = np.zeros_like(self.grayscale_image)
		for i in range(self.grayscale_image.shape[0]):
			for j in range(self.grayscale_image.shape[1]):
				if self.grayscale_image[i, j] < threshold:
					dithered[i, j] = 0
				else:
					dithered[i, j] = 255
		dithered_image = Image.fromarray(dithered)
		return dithered_image

	def random_dithering(self, image):
		dithered = np.zeros_like(self.grayscale_image)
		for i in range(self.grayscale_image.shape[0]):
			for j in range(self.grayscale_image.shape[1]):
				if np.random.rand() <= self.grayscale_image[i, j] / 255:
					dithered[i, j] = 255
				else:
					dithered[i, j] = 0
		dithered_image = Image.fromarray(dithered)
		return dithered_image

	def save_dithered_image(self):
		if self.dithered_image is None:
			return

		file_path = filedialog.asksaveasfilename(defaultextension=".tif")
		if file_path:
			self.dithered_image.save(file_path)

if __name__ == "__main__":
	app = DitherEditor()
	app.mainloop()
