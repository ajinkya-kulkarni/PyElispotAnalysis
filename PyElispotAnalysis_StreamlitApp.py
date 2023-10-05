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

##########################################################################

import streamlit as st
from io import BytesIO

from cv2 import MORPH_OPEN, morphologyEx, resize
import numpy as np
from skimage.measure import label

import sys
# Don't generate the __pycache__ folder locally
sys.dont_write_bytecode = True 
# Print exception without the buit-in python warning
sys.tracebacklimit = 0 

##########################################################################

from modules import *

allowed_image_size = 1000 # Only images with sizes less than 1000x1000 allowed

##########################################################################

# Open the logo file in binary mode and read its contents into memory
with open("logo.jpg", "rb") as f:
	image_data = f.read()

# Create a BytesIO object from the image data
image_bytes = BytesIO(image_data)

# Configure the page settings using the "set_page_config" method of Streamlit
st.set_page_config(
	page_title='PyElispotAnalysis',
	page_icon=image_bytes,  # Use the logo image as the page icon
	layout="centered",
	initial_sidebar_state="expanded",
	menu_items={
		'Get help': 'mailto:ajinkya.kulkarni@mpinat.mpg.de',
		'Report a bug': 'mailto:ajinkya.kulkarni@mpinat.mpg.de',
		'About': 'This is an application for demonstrating the PyElispotAnalysis package. Developed, tested, and maintained by Ajinkya Kulkarni: https://github.com/ajinkya-kulkarni at the MPI-NAT, Goettingen.'
	}
)

##########################################################################

# Set the title of the web app
st.title(':blue[Spot detection for Elispot assay images. Works best for images smaller than 1000x1000 pixels]')

# st.caption('Application screenshots and source code available [here](https://github.com/ajinkya-kulkarni/PySpatialHistologyAnalysis). Sample image to test this application is available [here](https://github.com/ajinkya-kulkarni/PySpatialHistologyAnalysis/blob/main/TestImage.jpeg).', unsafe_allow_html = False)

# Add some vertical space between the title and the next section
st.markdown("")

##########################################################################

# Create a form using the "form" method of Streamlit
with st.form(key = 'form1', clear_on_submit = True):

	# Add some text explaining what the user should do next
	st.markdown(':blue[Upload a single Elispot assay image/slide to be analyzed.]')

	# Add a file uploader to allow the user to upload an image file
	uploaded_file = st.file_uploader("Upload a file", type = ["tif", "tiff", "png", "jpg", "jpeg"], accept_multiple_files = False, label_visibility = 'collapsed')

	######################################################################

	st.markdown("")

	left_column, middle_column1, middle_column2, right_column = st.columns(4)

	with left_column:

		st.slider('Local window size for analyzing image', min_value = 5, max_value = 101, value = 41, step = 2, format = '%d', label_visibility = "visible", key = '-BlockSizeKey-')

		BlockSize = int(st.session_state['-BlockSizeKey-'])

	with middle_column1:

		st.slider('Value to subtract from local window.', min_value = 2, max_value = 50, value = 10, step = 2, format = '%d', label_visibility = "visible", key = '-ConstantKey-')

		Constant = int(st.session_state['-ConstantKey-'])

	with middle_column2:

		st.slider('Minimum area of spots in the image.', min_value = 2, max_value = 50, value = 10, step = 2, format = '%d', label_visibility = "visible", key = '-MinimumAreaKey-')

		MinimumAreaKey = int(st.session_state['-MinimumAreaKey-'])

	with right_column:

		st.slider('Maximum area of spots in the image.', min_value = 500, max_value = 2000, value = 1000, step = 100, format = '%d', label_visibility = "visible", key = '-MaximumAreaKey-')

		MaximumAreaKey = int(st.session_state['-MaximumAreaKey-'])

	st.markdown("")

	######################################################################

	# Add a submit button to the form
	submitted = st.form_submit_button('Analyze')

	######################################################################

	# If no file was uploaded, stop processing and exit early
	if uploaded_file is None:
		st.stop()

	######################################################################

	if submitted:

		# Read and process the image: convert it to grayscale and scale it
		img_scaled = read_image(uploaded_file)

		if img_scaled.shape[0] > allowed_image_size or img_scaled.shape[1] > allowed_image_size:
			st.error('Uploaded image exceeds the allowed image size. Please reduce the image size.')
			st.stop()

		# Resize image to suit the UI for image comparision
		img_scaled = resize_image(img_scaled)

		# Segment the processed image to highlight regions of interest
		mask_image = make_segmented_image(img_scaled, BlockSize, Constant)

		# Define a kernel for morphological operations
		# Erosion helps in detaching closely packed regions
		kernel_size = (5, 5)
		kernel = np.ones(kernel_size, np.uint8)

		# Perform morphological opening on the segmented image
		# Opening is an operation that consists of erosion followed by dilation
		# It helps to remove noise and to separate regions that are close to each other
		opened = morphologyEx(mask_image, MORPH_OPEN, kernel)

		# Invert the opened image
		# This is done so the regions of interest are now considered as foreground (labelled as 1)
		inverted_opened = 1 - opened

		# Label the regions in the inverted image
		# Each connected component/region gets a unique label
		labeled_image = label(inverted_opened, connectivity=2)

		# Use the counts_spots function to draw circles around detected spots
		# Spots are determined based on the area and eccentricity criteria defined in the function
		circled_image, counter = counts_spots(labeled_image, img_scaled, MinimumAreaKey, MaximumAreaKey)

		# # Generate the results figure
		# result_figure = make_figure(img_scaled, circled_image, counter)

		##############################################################

		st.markdown("""---""")

		st.markdown("Results")

		##############################################################

		image_comparison(img1=img_scaled, img2=circled_image, label1="Uploaded image", label2="Detected spots")

		st.markdown(f'{counter} spots detected.')

		st.stop()
		
##########################################################################
