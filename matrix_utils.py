import numpy as np

def matrix_rotation(point, axis_start, axis_end, angle, return_steps=False):
    """
    Rotates a point around an arbitrary axis in 3D space using matrix transformations.
    
    Args:
        point (ndarray): The point to rotate [x, y, z]
        axis_start (ndarray): The starting point of the rotation axis [x, y, z]
        axis_end (ndarray): The ending point of the rotation axis [x, y, z]
        angle (float): The rotation angle in radians
        return_steps (bool): Whether to return intermediate transformation steps
    
    Returns:
        ndarray: The rotated point [x, y, z]
        list: (Optional) A list of transformation steps [(name, point), ...]
    """
    # Initialize the transformation steps list if needed
    steps = []
    if return_steps:
        steps.append(("Original Point", point.copy()))
    
    # Convert points to homogeneous coordinates
    p = np.append(point, 1)
    
    # Step 1: Translate axis_start to origin
    T = np.eye(4)
    T[0:3, 3] = -axis_start
    p_translated = T @ p
    
    if return_steps:
        steps.append(("Translated to Origin", p_translated[0:3]))
    
    # Calculate the direction vector of the axis
    axis_vector = axis_end - axis_start
    axis_length = np.linalg.norm(axis_vector)
    
    # Normalize the axis vector
    if axis_length > 0:
        axis_unit = axis_vector / axis_length
    else:
        # Handle the case where axis_start and axis_end are the same
        axis_unit = np.array([0, 0, 1])
    
    # Step 2: Rotate the axis to align with the Z-axis
    # First, rotate around the Y-axis to bring the axis into the YZ-plane
    # Calculate the angle between the projection of the axis on the XZ-plane and the Z-axis
    z_axis = np.array([0, 0, 1])
    
    # Project the axis onto the XZ-plane
    proj_xz = np.array([axis_unit[0], 0, axis_unit[2]])
    proj_xz_norm = np.linalg.norm(proj_xz)
    
    # Skip this step if the axis is already in the YZ-plane
    if proj_xz_norm > 1e-10:
        # Normalize the projection
        proj_xz = proj_xz / proj_xz_norm
        
        # Calculate the rotation angle around Y
        cos_alpha = np.dot(proj_xz, z_axis)
        sin_alpha = np.cross(proj_xz, z_axis)[1]  # Y-component of the cross product
        alpha = np.arctan2(sin_alpha, cos_alpha)
        
        # Create the rotation matrix around Y
        Ry = np.eye(4)
        Ry[0, 0] = np.cos(alpha)
        Ry[0, 2] = np.sin(alpha)
        Ry[2, 0] = -np.sin(alpha)
        Ry[2, 2] = np.cos(alpha)
        
        # Apply the Y rotation
        p_rotated_y = Ry @ p_translated
        
        if return_steps:
            steps.append(("Rotated to YZ-plane", p_rotated_y[0:3]))
    else:
        # Skip Y rotation
        p_rotated_y = p_translated
        Ry = np.eye(4)
    
    # Now rotate around the X-axis to align with Z
    # Calculate the new axis direction after Y rotation
    new_axis = Ry[0:3, 0:3] @ axis_unit
    
    # Calculate the angle between the new axis and the Z-axis
    cos_beta = np.dot(new_axis, z_axis)
    # X-component of the cross product
    sin_beta = np.cross(new_axis, z_axis)[0]
    beta = np.arctan2(sin_beta, cos_beta)
    
    # Create the rotation matrix around X
    Rx = np.eye(4)
    Rx[1, 1] = np.cos(beta)
    Rx[1, 2] = -np.sin(beta)
    Rx[2, 1] = np.sin(beta)
    Rx[2, 2] = np.cos(beta)
    
    # Apply the X rotation
    p_aligned = Rx @ p_rotated_y
    
    if return_steps:
        steps.append(("Aligned with Z-axis", p_aligned[0:3]))
    
    # Step 3: Rotate around Z-axis by the specified angle
    Rz = np.eye(4)
    Rz[0, 0] = np.cos(angle)
    Rz[0, 1] = -np.sin(angle)
    Rz[1, 0] = np.sin(angle)
    Rz[1, 1] = np.cos(angle)
    
    p_rotated_z = Rz @ p_aligned
    
    if return_steps:
        steps.append(("Rotated around Z-axis", p_rotated_z[0:3]))
    
    # Step 4: Reverse the alignment transforms
    p_unaligned = np.linalg.inv(Rx) @ p_rotated_z
    
    if return_steps:
        steps.append(("Reversed X-axis Alignment", p_unaligned[0:3]))
    
    p_unrotated_y = np.linalg.inv(Ry) @ p_unaligned
    
    if return_steps:
        steps.append(("Reversed Y-axis Alignment", p_unrotated_y[0:3]))
    
    # Step 5: Translate back
    T_inv = np.eye(4)
    T_inv[0:3, 3] = axis_start
    p_final = T_inv @ p_unrotated_y
    
    if return_steps:
        steps.append(("Final Rotated Point", p_final[0:3]))
    
    # Extract the 3D coordinates from the homogeneous result
    result = p_final[0:3]
    
    if return_steps:
        return result, steps
    else:
        return result
