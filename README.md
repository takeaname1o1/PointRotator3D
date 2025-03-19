# 3D Rotation Visualizer

## Overview
The **3D Rotation Visualizer** is an interactive tool built with Streamlit, NumPy, and Plotly that demonstrates the rotation of a point around an arbitrary axis in 3D space. Users can input a point, define a rotation axis, and visualize the transformation using either matrix transformations or quaternion-based rotation.

## Features
- **Interactive UI:** Input point coordinates and define a rotation axis.
- **Matrix & Quaternion Rotation:** Choose between matrix transformation and quaternion methods.
- **Real-time Visualization:** Animated rotation with trajectory display.
- **Detailed Steps:** Step-by-step breakdown of transformations.
- **Coordinate System Display:** Includes labeled X, Y, and Z axes for better understanding.

## Installation
### Prerequisites
Ensure you have Python 3.8+ installed.

### Setup
Clone the repository:
```bash
git clone https://github.com/yourusername/3d-rotation-visualizer.git
cd 3d-rotation-visualizer
```

Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
### Run the App
```bash
streamlit run app.py
```

### Controls
- **Point to Rotate:** Input X, Y, and Z coordinates.
- **Rotation Axis:** Define a starting and ending point for the rotation axis.
- **Rotation Angle:** Select the angle in degrees.
- **Rotation Method:** Choose between **Matrix Transformation** or **Quaternion Rotation**.
- **Animation Settings:** Enable animation and adjust speed and steps.
- **Apply Rotation:** Click the button to visualize the rotation.

## How It Works
### Matrix Transformation
1. **Translate** the axis to pass through the origin.
2. **Align the axis** with the Z-axis using rotation matrices.
3. **Apply rotation** around the Z-axis.
4. **Reverse transformations** to return to the original orientation.

### Quaternion Rotation
Uses quaternion multiplication to apply rotation in a single step, offering better numerical stability compared to matrix transformations.

## Dependencies
- **Streamlit** (for UI)
- **NumPy** (for numerical computations)
- **Plotly** (for 3D visualization)

## Example Output

[https://pointrotator3d.onrender.com/](https://pointrotator3d.onrender.com/)

![Example Rotation](assets/example.gif)

## License
This project is licensed under the MIT License.

## Acknowledgments
Built using [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/).
