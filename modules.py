#!/usr/bin/env python3
# encoding: utf-8
#
# Copyright (C) 2022 Max Planck Institute for Multidisclplinary Sciences
# Copyright (C) 2022 University Medical Center Goettingen
# Copyright (C) 2022 Ajinkya Kulkarni <ajinkya.kulkarni@mpinat.mpg.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

######################################################################################

# This file contains all the modules/functions necessary for running the streamlit application or the example notebooks.

######################################################################################

import matplotlib.pyplot as plt
from cv2 import adaptiveThreshold, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, cvtColor, COLOR_GRAY2RGB, circle, MORPH_OPEN, morphologyEx, INTER_AREA, resize
from PIL import Image
import numpy as np
from skimage.measure import regionprops

######################################################################################

def resize_image(image, new_width=674):

    # Calculate the aspect ratio
    aspect_ratio = float(new_width) / image.shape[1]
    
    # Compute new height using aspect_ratio
    new_height = int(image.shape[0] * aspect_ratio)
    
    # Resize the image
    resized_image = resize(image, (new_width, new_height), interpolation=INTER_AREA)
    
    return resized_image

######################################################################################

def read_image(image_path):
	"""
	Reads and processes an image from the given path.
	
	Args:
	- image_path (str): Path to the image file.
	
	Returns:
	- img_scaled (numpy.ndarray): Processed image in grayscale and scaled to [0, 255].
	"""
	
	img = np.array(Image.open(image_path).convert('L'))
	min_val, max_val = img.min(), img.max()
	
	img_normalized = (img - min_val) / (max_val - min_val)
	img_scaled = (img_normalized * 255).astype(np.uint8)
	
	return img_scaled

######################################################################################

def make_segmented_image(grayscaleimage, BlockSize, Constant):
	"""
	Segments the provided grayscale image using adaptive thresholding.
	
	Args:
	- grayscaleimage (numpy.ndarray): Input grayscale image.
	- BlockSize (int): Size of the neighborhood to calculate the threshold.
	- Constant (int): A constant subtracted from mean or weighted mean. 
					It is a user-defined constant which is subtracted from the calculated adaptive mean.
	
	Returns:
	- segmented_image (numpy.ndarray): Binary segmented image.
	"""
	
	segmented_image = adaptiveThreshold(grayscaleimage, 255, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, BlockSize, Constant)
	segmented_image = (segmented_image - segmented_image.min()) / (segmented_image.max() - segmented_image.min())
	
	return segmented_image

######################################################################################

def counts_spots(labeled_image, grayscale_parent_image, min_area, max_area):
	"""
	Counts spots on the labeled image by filtering based on area.
	
	Args:
	- labeled_image: Labeled image where each region has a unique ID.
	- grayscale_parent_image: Original grayscale image on which the spots will be visualized.
	- min_area, max_area: Filtering parameters for the spots.
	
	Returns:
	- An image with the detected spots circled.
	- Count of the detected spots.
	"""
	
	# Get the RGB values for tab:red from tab10 colormap
	rgb_color = plt.cm.tab10(1)
	# Excluding the alpha value and scaling to [0, 255]
	scaled_rgb = tuple([int(val * 255) for val in rgb_color[:-1]])

	# Convert to a 3-channel image for drawing colored circles
	circled_image = cvtColor(grayscale_parent_image, COLOR_GRAY2RGB)

	counter = 0
	label_counter = 1

	# Iterate over the regions in labeled_image
	for region in regionprops(labeled_image):
		# Check conditions
		if (min_area <= region.area <= max_area):
			# Draw a circle around the spot using the equivalent diameter
			y0, x0 = map(int, region.centroid)
			radius = int(0.5 * region.equivalent_diameter)
			circle(circled_image, (x0, y0), radius, scaled_rgb, 1)

			# Assign the current label to the filtered labels image
			coords = region.coords
			label_counter = label_counter + 1
			
			counter = counter + 1
	
	return circled_image, counter

######################################################################################

# def make_figure(img_scaled, circled_image, counter):

# 	fig = plt.figure(figsize=(8, 4))

# 	plt.subplot(1, 2, 1)
# 	plt.imshow(img_scaled, cmap='gray')
# 	plt.title('Image')
# 	plt.axis('off')

# 	plt.subplot(1, 2, 2)
# 	plt.imshow(circled_image)
# 	plt.title(f'{counter} IFN-Y cells')
# 	plt.axis('off')

# 	return fig

######################################################################################

import streamlit.components.v1 as components
import base64
import io
from typing import Union, Tuple
import requests
from PIL import Image
import numpy as np

def read_image_and_convert_to_base64(image: Union[Image.Image, str, np.ndarray]) -> Tuple[str, int, int]:
	"""
	Reads an image in PIL Image, file path, or numpy array format and returns a base64-encoded string of the image
	in JPEG format, along with its width and height.

	Args:
		image: An image in PIL Image, file path, or numpy array format.

	Returns:
		A tuple containing:
		- base64_src (str): A base64-encoded string of the image in JPEG format.
		- width (int): The width of the image in pixels.
		- height (int): The height of the image in pixels.

	Raises:
		TypeError: If the input image is not of a recognized type.

	Assumes:
		This function assumes that the input image is a valid image in PIL Image, file path, or numpy array format.
		It also assumes that the necessary libraries such as Pillow and scikit-image are installed.

	"""
	# Set the maximum image size to None to allow reading of large images
	Image.MAX_IMAGE_PIXELS = None

	# If input image is PIL Image, convert it to RGB format
	if isinstance(image, Image.Image):
		image_pil = image.convert('RGB')

	# If input image is a file path, open it using requests library if it's a URL, otherwise use PIL Image's open function
	elif isinstance(image, str):
		try:
			image_pil = Image.open(
				requests.get(image, stream=True).raw if str(image).startswith("http") else image
			).convert("RGB")
		except:
			# If opening image using requests library fails, try to use scikit-image library to read the image
			try:
				import skimage.io
			except ImportError:
				raise ImportError("Please run 'pip install -U scikit-image imagecodecs' for large image handling.")

			# Read the image using scikit-image and convert it to a PIL Image
			image_sk = skimage.io.imread(image).astype(np.uint8)
			if len(image_sk.shape) == 2:
				image_pil = Image.fromarray(image_sk, mode="1").convert("RGB")
			elif image_sk.shape[2] == 4:
				image_pil = Image.fromarray(image_sk, mode="RGBA").convert("RGB")
			elif image_sk.shape[2] == 3:
				image_pil = Image.fromarray(image_sk, mode="RGB")
			else:
				raise TypeError(f"image with shape: {image_sk.shape[3]} is not supported.")

	# If input image is a numpy array, create a PIL Image from it
	elif isinstance(image, np.ndarray):
		if image.shape[0] < 5:
			image = image[:, :, ::-1]
		image_pil = Image.fromarray(image).convert("RGB")

	# If input image is not of a recognized type, raise a TypeError
	else:
		raise TypeError("read image with 'pillow' using 'Image.open()'")

	# Get the width and height of the image
	width, height = image_pil.size

	# Save the PIL Image as a JPEG image with maximum quality (100) and no subsampling
	in_mem_file = io.BytesIO()
	image_pil.save(in_mem_file, format="JPEG", subsampling=0, quality=100)

	# Encode the bytes of the JPEG image in base64 format
	img_bytes = in_mem_file.getvalue()
	image_str = base64.b64encode(img_bytes).decode("utf-8")

	# Create a base64-encoded string of the image in JPEG format
	base64_src = f"data:image/jpg;base64,{image_str}"

	# Return the base64-encoded string along with the width and height of the image
	return base64_src, width, height

######################################################

def image_comparison(
	img1: str,
	img2: str,
	label1: str,
	label2: str,
	width_value = 674,
	show_labels: bool=True,
	starting_position: int=50,
) -> components.html:
	"""
	Creates an HTML block containing an image comparison slider of two images.

	Args:
		img1 (str): A string representing the path or URL of the first image to be compared.
		img2 (str): A string representing the path or URL of the second image to be compared.
		label1 (str): A label to be displayed above the first image in the slider.
		label2 (str): A label to be displayed above the second image in the slider.
		width_value (int, optional): The maximum width of the slider in pixels. Defaults to 500.
		show_labels (bool, optional): Whether to show the labels above the images in the slider. Defaults to True.
		starting_position (int, optional): The starting position of the slider. Defaults to 50.

	Returns:
		A Dash HTML component that displays an image comparison slider.

	"""
		# Convert the input images to base64 format
	img1_base64, img1_width, img1_height = read_image_and_convert_to_base64(img1)
	img2_base64, img2_width, img2_height = read_image_and_convert_to_base64(img2)

	# Get the maximum width and height of the input images
	img_width = int(max(img1_width, img2_width))
	img_height = int(max(img1_height, img2_height))

	# Calculate the aspect ratio of the images
	h_to_w = img_height / img_width

	# Determine the height of the slider based on the width and aspect ratio
	if img_width < width_value:
		width = img_width
	else:
		width = width_value
	height = int(width * h_to_w)

	# Load CSS and JS for the slider
	cdn_path = "https://cdn.knightlab.com/libs/juxtapose/latest"
	css_block = f'<link rel="stylesheet" href="{cdn_path}/css/juxtapose.css">'
	js_block = f'<script src="{cdn_path}/js/juxtapose.min.js"></script>'

	# Create the HTML code for the slider
	htmlcode = f"""
		<style>body {{ margin: unset; }}</style>
		{css_block}
		{js_block}
		<div id="foo" style="height: {height}; width: {width};"></div>
		<script>
		slider = new juxtapose.JXSlider('#foo',
			[
				{{
					src: '{img1_base64}',
					label: '{label1}',
				}},
				{{
					src: '{img2_base64}',
					label: '{label2}',
				}}
			],
			{{
				animate: true,
				showLabels: {str(show_labels).lower()},
				showCredits: true,
				startingPosition: "{starting_position}%",
				makeResponsive: true,
			}});
		</script>
		"""

	# Create a Dash HTML component from the HTML code
	static_component = components.html(htmlcode, height=height, width=width)

	return static_component

##########################################################################