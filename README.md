# PyElispotAnalysis
Detecting spots (IFN-Gamma positive cells) from an Elispot assay image

### App Overview

A web application developed using Streamlit is available at [https://elispotanalysis.streamlit.app/](https://elispotanalysis.streamlit.app/)

![alt text](https://github.com/ajinkya-kulkarni/PyElispotAnalysis/blob/main/AppImage1.png)
![alt text](https://github.com/ajinkya-kulkarni/PyElispotAnalysis/blob/main/AppImage2.png)
![alt text](https://github.com/ajinkya-kulkarni/PyElispotAnalysis/blob/main/AppImage3.png)

### Overview
PyElispotAnalysis is a Streamlit web application that provides a user-friendly interface for the automated analysis of Elispot assay images. Developed with a focus on ease of use and accuracy, it allows for the rapid quantification of spots within an assay image, facilitating the assessment of immune responses.

### Features
Image Upload: Users can upload Elispot assay images in various formats, including .tif, .tiff, .png, .jpg, and .jpeg.
Interactive Sliders: The app features interactive sliders for fine-tuning analysis parameters such as local window size, sensitivity for spot detection, and minimum and maximum spot area.
Automated Spot Detection: Utilizes adaptive thresholding and morphological operations to identify and count spots.
Visualization: Offers side-by-side visualization of the original and processed images with detected spots highlighted.
Histograms: Generates histograms for the distribution of spot sizes to provide insights into the range and density of the immune response.
Detailed Reporting: Produces a downloadable report with quantitative data on each detected spot, including area and diameter.
Responsive Design: Crafted to work on various devices with an intuitive layout that adapts to different screen sizes.

### Workflow
Image Processing: Upon image upload, the app processes the image, converting it to grayscale and resizing it to suit the user interface.
Parameter Adjustment: Users can adjust analysis parameters using sliders to optimize spot detection according to their specific assay characteristics.
Spot Detection: The app applies adaptive thresholding and morphological operations to detect spots, which are then filtered based on size criteria set by the user.
Result Visualization: Detected spots are circled on the processed image, and the user can compare this with the original image using an interactive slider.
Data Analysis: The app generates a histogram of spot sizes and a detailed report, including a table with metrics for each spot.
Report Download: Users can download the processed image and a CSV file containing the detailed spot analysis.

### Support and Contribution
Information on how to reach out for support, report bugs, or contribute to the project. Encourage contributions such as bug fixes, feature requests, and suggestions for improvement.
