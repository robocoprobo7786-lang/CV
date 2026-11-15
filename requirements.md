# Requirements: Edge Detection Using Sobel, Prewitt, and Laplacian Operators

## 1. Project Overview

**Course:** Computer Vision (256PUPC275)\
**Course Code:** 256PUPC275\
**Assignment:** Option 2 -- Implementation of Image Segmentation and
Feature Detection Techniques\
**Selected Topic:** Topic 3 -- Edge Detection

This project will implement and demonstrate edge detection on a suitable
input image using Python. The application will apply the Sobel, Prewitt,
and Laplacian operators, display the original and processed images, and
compare the results.

## 2. Objective

To understand and implement edge detection using suitable
image-processing operators, visualize the detected edges, and analyse
the effectiveness and limitations of each operator.

## 3. Scope

The project will:

-   Load a suitable grayscale or colour image.
-   Convert the input image to grayscale for edge processing.
-   Apply the Sobel operator.
-   Apply the Prewitt operator.
-   Apply the Laplacian operator.
-   Display the original image and the output from each operator.
-   Compare the visual results and discuss observations.

The project is an educational image-processing demonstration. It is not
intended for medical, security, or other safety-critical use.

## 4. Functional Requirements

  -----------------------------------------------------------------------
  ID                                  Requirement
  ----------------------------------- -----------------------------------
  FR-01                               The application shall load an image
                                      from a local file.

  FR-02                               The application shall display the
                                      original input image.

  FR-03                               The application shall convert the
                                      image to grayscale before applying
                                      the edge-detection operators.

  FR-04                               The application shall apply the
                                      Sobel operator to detect image
                                      intensity changes in horizontal and
                                      vertical directions.

  FR-05                               The application shall apply the
                                      Prewitt operator to detect edges in
                                      horizontal and vertical directions.

  FR-06                               The application shall apply the
                                      Laplacian operator to highlight
                                      rapid intensity changes.

  FR-07                               The application shall display the
                                      processed output for each operator.

  FR-08                               The application shall make it
                                      possible to compare the outputs
                                      with the original image.

  FR-09                               The notebook shall include
                                      explanations of the processing
                                      steps and the algorithms used.

  FR-10                               The project shall include an
                                      analysis of the observed results
                                      and the limitations of the
                                      techniques.
  -----------------------------------------------------------------------

## 5. Non-Functional Requirements

-   **Usability:** Code and output visualizations should be easy to
    follow.
-   **Readability:** Python code should be organized into logical
    sections and include comments.
-   **Reproducibility:** The notebook should run from top to bottom in
    Google Colab or Jupyter Notebook when the required packages and
    input image are available.
-   **Compatibility:** Use commonly available Python image-processing
    and visualization libraries.
-   **Clarity:** Plots should have meaningful titles and labels.

## 6. Tools and Technologies

-   **Programming language:** Python
-   **Recommended environment:** Google Colab or Jupyter Notebook
-   **Libraries:**
    -   OpenCV (`opencv-python`) for image loading and image-processing
        operations.
    -   NumPy for numerical array operations.
    -   Matplotlib for displaying images and results.

Install the required packages, if they are not already available:

``` bash
pip install opencv-python numpy matplotlib
```

## 7. Input Requirements

-   Use at least one suitable image in a common format such as PNG or
    JPG.
-   The image should contain visible objects, boundaries, or texture so
    that edge detection results can be observed.
-   The input image must be available to the notebook at runtime.
-   Preserve the original image for comparison with the processed
    outputs.

## 8. Processing Requirements

The implementation should follow this general workflow:

1.  Import the required Python libraries.
2.  Load the input image.
3.  Check that the image was loaded successfully.
4.  Display the original image.
5.  Convert the image to grayscale.
6.  Apply the Sobel operator and generate a combined edge-strength image
    from the horizontal and vertical responses.
7.  Apply the Prewitt operator using horizontal and vertical kernels,
    and combine the responses.
8.  Apply the Laplacian operator to the grayscale image.
9.  Display the grayscale image and the three edge-detection results.
10. Compare the outputs and record observations.

Where output values need to be displayed as images, normalize or convert
them appropriately for visualization without changing the underlying
explanation of the method.

## 9. Expected Outputs

The notebook should show:

-   Original input image.
-   Grayscale image.
-   Sobel edge-detection result.
-   Prewitt edge-detection result.
-   Laplacian edge-detection result.
-   A comparison view containing the original image and the processed
    outputs.

The report should explain which edges are emphasized by each method and
note visible differences, such as sensitivity to noise or the amount of
detail detected.

## 10. Analysis Requirements

The analysis should address:

-   Whether the main object boundaries are detected clearly.
-   Differences between the Sobel and Prewitt results.
-   The type of edge response produced by the Laplacian operator.
-   Whether noise or texture creates unwanted responses.
-   The strengths and limitations observed for each operator.
-   Which method appears most suitable for the selected input image,
    with a reason based on the results.

Do not claim that one operator is universally best; conclusions should
be based on the selected image and the observed outputs.

## 11. Deliverables

As specified in the assignment brief, the project submission should
include:

1.  Python program or Jupyter Notebook (`.ipynb`).
2.  Input image and corresponding processed output.
3.  Explanation of the algorithm and implementation.
4.  Screenshots demonstrating the results.
5.  Brief conclusion based on the observations.

The assignment submission requirements also specify a short report in
PDF format and a video presentation involving all team members
explaining the work.

## 12. Acceptance Criteria

The project will be considered complete when:

-   [ ] A suitable input image loads successfully.
-   [ ] The original and grayscale images are displayed.
-   [ ] Sobel edge detection is implemented and its output is displayed.
-   [ ] Prewitt edge detection is implemented and its output is
    displayed.
-   [ ] Laplacian edge detection is implemented and its output is
    displayed.
-   [ ] The outputs are presented clearly for comparison.
-   [ ] The notebook contains comments and explanations of the
    algorithms.
-   [ ] The results are analysed, including strengths and limitations.
-   [ ] A brief conclusion is included.
-   [ ] The notebook, input/output images, report, screenshots, and
    presentation materials are prepared for submission.

## 13. Out of Scope

-   Training a machine-learning or deep-learning model.
-   Object recognition or object classification.
-   Real-time video edge detection.
-   Building a production application or graphical user interface.
-   Claiming that edge detection alone performs complete object or
    semantic segmentation.

## 14. Reference

Requirements are based on the **Computer Vision (256PUPC275) School
Assessment, 2026--27**, Option 2, Topic 3 -- Edge Detection, and its
tasks, expected deliverables, and submission requirements.
