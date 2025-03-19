import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time
from matrix_utils import matrix_rotation
from quaternion_utils import quaternion_rotation

st.set_page_config(
    page_title="3D Rotation Visualizer",
    page_icon="🔄",
    layout="wide",
)

# Title and description
st.title("3D Rotation Visualizer")
st.markdown("""
This interactive tool demonstrates the rotation of a point around an arbitrary axis in 3D space.
You can input coordinates for a point, define a rotation axis, and visualize the rotation using 
either the matrix transformation method or quaternion method.
""")

# Control panel
with st.sidebar:
    st.header("Controls")
    
    # Point coordinates
    st.subheader("Point to Rotate")
    point_x = st.number_input("X Coordinate", value=2.0, step=0.1)
    point_y = st.number_input("Y Coordinate", value=1.0, step=0.1)
    point_z = st.number_input("Z Coordinate", value=1.0, step=0.1)
    point = np.array([point_x, point_y, point_z])
    
    # Axis definition
    st.subheader("Rotation Axis")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Starting Point")
        axis_start_x = st.number_input("X₁", value=0.0, step=0.1)
        axis_start_y = st.number_input("Y₁", value=0.0, step=0.1)
        axis_start_z = st.number_input("Z₁", value=0.0, step=0.1)
    with col2:
        st.write("Ending Point")
        axis_end_x = st.number_input("X₂", value=0.0, step=0.1)
        axis_end_y = st.number_input("Y₂", value=1.0, step=0.1)
        axis_end_z = st.number_input("Z₂", value=0.0, step=0.1)
    
    axis_start = np.array([axis_start_x, axis_start_y, axis_start_z])
    axis_end = np.array([axis_end_x, axis_end_y, axis_end_z])
    
    # Check if axis is valid (start and end points must be different)
    axis_is_valid = not np.array_equal(axis_start, axis_end)
    if not axis_is_valid:
        st.error("⚠️ The axis start and end points must be different.")
    
    # Rotation angle
    st.subheader("Rotation Angle")
    angle_deg = st.slider("Angle (degrees)", min_value=0, max_value=360, value=45, step=5)
    angle_rad = np.radians(angle_deg)
    
    # Rotation method selection
    st.subheader("Rotation Method")
    rotation_method = st.radio(
        "Select a method:",
        options=["Matrix Transformation", "Quaternion"],
        index=0
    )
    
    # Animation controls
    st.subheader("Animation")
    animate = st.checkbox("Animate Rotation", value=False)
    if animate:
        animation_speed = st.slider("Animation Speed", min_value=1, max_value=10, value=5)
        steps = st.slider("Number of Steps", min_value=10, max_value=100, value=30)
    
    # Execute rotation
    run_rotation = st.button("Apply Rotation", disabled=not axis_is_valid, type="primary")

# Function to create the 3D visualization
def create_3d_visualization(point, axis_start, axis_end, rotated_point=None, 
                           intermediate_points=None, highlight_index=None):
    # Create figure
    fig = go.Figure()
    
    # Determine plot bounds based on points
    all_points = [point, axis_start, axis_end]
    if rotated_point is not None:
        all_points.append(rotated_point)
    if intermediate_points is not None:
        all_points.extend(intermediate_points)
    
    all_points = np.array(all_points)
    point_ranges = np.ptp(all_points, axis=0)  # Get range in each dimension
    max_range = np.max(point_ranges)
    center = np.mean(all_points, axis=0)
    
    # Set bounds to fit the points better
    # Use a smaller padding factor for tighter view
    padding_factor = 1.2  # Reduced from 1.5 to zoom in more
    bounds = max(max_range * padding_factor, 2.5)  # At least 2.5 units wide
    
    # Add original point
    fig.add_trace(go.Scatter3d(
        x=[point[0]], y=[point[1]], z=[point[2]],
        mode='markers',
        marker=dict(size=10, color='blue'),
        name='Original Point'
    ))
    
    # Add rotation axis
    fig.add_trace(go.Scatter3d(
        x=[axis_start[0], axis_end[0]], 
        y=[axis_start[1], axis_end[1]], 
        z=[axis_start[2], axis_end[2]],
        mode='lines',
        line=dict(color='purple', width=6),
        name='Rotation Axis'
    ))
    
    # Add rotated point if available
    if rotated_point is not None:
        fig.add_trace(go.Scatter3d(
            x=[rotated_point[0]], y=[rotated_point[1]], z=[rotated_point[2]],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='Rotated Point'
        ))
    
    # Add intermediate points if available
    if intermediate_points is not None and len(intermediate_points) > 0:
        positions = np.array(intermediate_points)
        colors = ['lightblue'] * len(positions)
        
        # Highlight a specific intermediate point if requested
        if highlight_index is not None and 0 <= highlight_index < len(positions):
            colors[highlight_index] = 'orange'
        
        fig.add_trace(go.Scatter3d(
            x=positions[:, 0], y=positions[:, 1], z=positions[:, 2],
            mode='markers+lines',
            marker=dict(
                size=6,
                color=colors,
                opacity=0.7
            ),
            line=dict(color='lightblue', width=2),
            name='Trajectory'
        ))
    
    # Add coordinate system
    origin = [0, 0, 0]
    axis_length = bounds / 2
    
    # X-axis
    fig.add_trace(go.Scatter3d(
        x=[origin[0], axis_length], y=[origin[1], origin[1]], z=[origin[2], origin[2]],
        mode='lines',
        line=dict(color='red', width=2),
        name='X-axis'
    ))
    
    # Y-axis
    fig.add_trace(go.Scatter3d(
        x=[origin[0], origin[0]], y=[origin[1], axis_length], z=[origin[2], origin[2]],
        mode='lines',
        line=dict(color='green', width=2),
        name='Y-axis'
    ))
    
    # Z-axis
    fig.add_trace(go.Scatter3d(
        x=[origin[0], origin[0]], y=[origin[1], origin[1]], z=[origin[2], axis_length],
        mode='lines',
        line=dict(color='blue', width=2),
        name='Z-axis'
    ))
    
    # Update layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-bounds + center[0], bounds + center[0]], title='X'),
            yaxis=dict(range=[-bounds + center[1], bounds + center[1]], title='Y'),
            zaxis=dict(range=[-bounds + center[2], bounds + center[2]], title='Z'),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=600,
    )
    
    return fig

# Main visualization area
if axis_is_valid:
    # Initialize visualization
    if not run_rotation:
        # Show initial setup without rotation
        fig = create_3d_visualization(point, axis_start, axis_end)
        st.plotly_chart(fig, use_container_width=True)
        
        # Instructions
        st.info("Adjust the parameters in the sidebar and click 'Apply Rotation' to see the result.")
        
    else:
        # Apply rotation based on selected method
        if rotation_method == "Matrix Transformation":
            if animate:
                # Perform animation for matrix rotation
                st.subheader("Matrix Transformation Animation")
                rotation_placeholder = st.empty()
                steps_info = st.empty()
                
                # Calculate intermediate points for animation
                angles = np.linspace(0, angle_rad, steps)
                intermediate_points = []
                
                # Precompute all intermediate points
                for i, step_angle in enumerate(angles):
                    rotated, transformation_steps = matrix_rotation(
                        point, axis_start, axis_end, step_angle, return_steps=True
                    )
                    intermediate_points.append(rotated)
                
                # Animate through the intermediate points
                for i in range(steps):
                    # Highlight the current step in the animation
                    fig = create_3d_visualization(
                        point, axis_start, axis_end, 
                        intermediate_points[i], intermediate_points[:i+1], i
                    )
                    rotation_placeholder.plotly_chart(fig, use_container_width=True)
                    steps_info.text(f"Step {i+1}/{steps}: Rotation angle = {np.degrees(angles[i]):.1f}°")
                    time.sleep(1 / animation_speed)  # Control animation speed
                
                # Show the detailed steps of the final rotation
                rotated_point, transformation_steps = matrix_rotation(
                    point, axis_start, axis_end, angle_rad, return_steps=True
                )
                
                # Display the transformation steps
                st.subheader("Matrix Transformation Steps")
                for i, (step_name, step_point) in enumerate(transformation_steps):
                    st.write(f"{i+1}. **{step_name}**: [{step_point[0]:.4f}, {step_point[1]:.4f}, {step_point[2]:.4f}]")
            
            else:
                # Perform direct rotation without animation
                rotated_point, transformation_steps = matrix_rotation(
                    point, axis_start, axis_end, angle_rad, return_steps=True
                )
                
                # Create the visualization
                fig = create_3d_visualization(point, axis_start, axis_end, rotated_point)
                st.plotly_chart(fig, use_container_width=True)
                
                # Display the transformation steps
                st.subheader("Matrix Transformation Steps")
                for i, (step_name, step_point) in enumerate(transformation_steps):
                    st.write(f"{i+1}. **{step_name}**: [{step_point[0]:.4f}, {step_point[1]:.4f}, {step_point[2]:.4f}]")
        
        else:  # Quaternion method
            if animate:
                # Perform animation for quaternion rotation
                st.subheader("Quaternion Rotation Animation")
                rotation_placeholder = st.empty()
                steps_info = st.empty()
                
                # Calculate intermediate points for animation
                angles = np.linspace(0, angle_rad, steps)
                intermediate_points = []
                
                # Precompute all intermediate points
                for step_angle in angles:
                    rotated = quaternion_rotation(point, axis_start, axis_end, step_angle)
                    intermediate_points.append(rotated)
                
                # Animate through the intermediate points
                for i in range(steps):
                    # Highlight the current step in the animation
                    fig = create_3d_visualization(
                        point, axis_start, axis_end, 
                        intermediate_points[i], intermediate_points[:i+1], i
                    )
                    rotation_placeholder.plotly_chart(fig, use_container_width=True)
                    steps_info.text(f"Step {i+1}/{steps}: Rotation angle = {np.degrees(angles[i]):.1f}°")
                    time.sleep(1 / animation_speed)  # Control animation speed
                
                # Display the final quaternion
                rotated_point = quaternion_rotation(point, axis_start, axis_end, angle_rad)
                st.subheader("Quaternion Rotation Information")
                
                # Calculate and display the rotation quaternion
                axis_vector = axis_end - axis_start
                axis_vector = axis_vector / np.linalg.norm(axis_vector)
                q_w = np.cos(angle_rad / 2)
                q_x = axis_vector[0] * np.sin(angle_rad / 2)
                q_y = axis_vector[1] * np.sin(angle_rad / 2)
                q_z = axis_vector[2] * np.sin(angle_rad / 2)
                
                st.write(f"Rotation Quaternion: q = [{q_w:.4f}, {q_x:.4f}, {q_y:.4f}, {q_z:.4f}]")
            
            else:
                # Perform direct quaternion rotation without animation
                rotated_point = quaternion_rotation(point, axis_start, axis_end, angle_rad)
                
                # Create the visualization
                fig = create_3d_visualization(point, axis_start, axis_end, rotated_point)
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate and display the rotation quaternion
                axis_vector = axis_end - axis_start
                axis_vector = axis_vector / np.linalg.norm(axis_vector)
                q_w = np.cos(angle_rad / 2)
                q_x = axis_vector[0] * np.sin(angle_rad / 2)
                q_y = axis_vector[1] * np.sin(angle_rad / 2)
                q_z = axis_vector[2] * np.sin(angle_rad / 2)
                
                st.subheader("Quaternion Rotation Information")
                st.write(f"Rotation Quaternion: q = [{q_w:.4f}, {q_x:.4f}, {q_y:.4f}, {q_z:.4f}]")
        
        # Display result
        st.success(f"Rotation completed! Original Point: [{point[0]:.4f}, {point[1]:.4f}, {point[2]:.4f}] → Rotated Point: [{rotated_point[0]:.4f}, {rotated_point[1]:.4f}, {rotated_point[2]:.4f}]")

# Add explanation
st.markdown("""
---
### How It Works

#### Matrix Transformation Method:
1. **Translation**: Move the starting point of the rotation axis to the origin
2. **Align with Z-axis**: Rotate the axis to align with the Z-axis
3. **Rotate**: Perform the desired rotation around the Z-axis
4. **Reverse alignment**: Apply the inverse transformations to return the axis to its original position

#### Quaternion Method:
Uses quaternion mathematics to directly rotate the point around the specified axis in a single operation.
This approach avoids the multiple matrix transformations of the matrix method and can be more numerically stable.

---
""")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 40px; color: #888;">
    Created with Streamlit, NumPy, and Plotly
    <br>
    <a href="https://github.com/yourusername/3d-rotation-visualizer" target="_blank">
        <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="20" style="vertical-align: middle;"> 
        View on GitHub
    </a>
</div>
""", unsafe_allow_html=True)
