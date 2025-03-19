import numpy as np

def quaternion_rotation(point, axis_start, axis_end, angle):
    """
    Rotates a point around an arbitrary axis in 3D space using quaternions.
    
    Args:
        point (ndarray): The point to rotate [x, y, z]
        axis_start (ndarray): The starting point of the rotation axis [x, y, z]
        axis_end (ndarray): The ending point of the rotation axis [x, y, z]
        angle (float): The rotation angle in radians
    
    Returns:
        ndarray: The rotated point [x, y, z]
    """
    # Calculate the axis direction vector
    axis_vector = axis_end - axis_start
    axis_length = np.linalg.norm(axis_vector)
    
    # Normalize the axis vector
    if axis_length > 0:
        axis_vector = axis_vector / axis_length
    else:
        # Handle the case where axis_start and axis_end are the same
        # Default to Z-axis rotation in this case
        axis_vector = np.array([0, 0, 1])
    
    # Create the rotation quaternion
    q_w = np.cos(angle / 2)
    q_x = axis_vector[0] * np.sin(angle / 2)
    q_y = axis_vector[1] * np.sin(angle / 2)
    q_z = axis_vector[2] * np.sin(angle / 2)
    q = np.array([q_w, q_x, q_y, q_z])
    
    # Normalize the quaternion (should already be normalized, but just to be safe)
    q = q / np.linalg.norm(q)
    
    # Translate the point so that axis_start is at the origin
    p_translated = point - axis_start
    
    # Convert the point to a quaternion (with w=0)
    p_quaternion = np.array([0, p_translated[0], p_translated[1], p_translated[2]])
    
    # Perform the quaternion rotation: q * p * q^-1
    # First, calculate q^-1 (the conjugate, since q is normalized)
    q_inv = np.array([q[0], -q[1], -q[2], -q[3]])
    
    # Calculate q * p
    # (q_w, q_v) * (0, p_v) = (-q_v·p_v, q_w*p_v + q_v×p_v)
    intermediate_w = -q[1]*p_quaternion[1] - q[2]*p_quaternion[2] - q[3]*p_quaternion[3]
    intermediate_x = q[0]*p_quaternion[1] + q[2]*p_quaternion[3] - q[3]*p_quaternion[2]
    intermediate_y = q[0]*p_quaternion[2] + q[3]*p_quaternion[1] - q[1]*p_quaternion[3]
    intermediate_z = q[0]*p_quaternion[3] + q[1]*p_quaternion[2] - q[2]*p_quaternion[1]
    intermediate = np.array([intermediate_w, intermediate_x, intermediate_y, intermediate_z])
    
    # Calculate (q * p) * q^-1
    # (intermediate_w, intermediate_v) * (q_w, -q_v)
    result_w = intermediate[0]*q_inv[0] - intermediate[1]*q_inv[1] - intermediate[2]*q_inv[2] - intermediate[3]*q_inv[3]
    result_x = intermediate[0]*q_inv[1] + intermediate[1]*q_inv[0] + intermediate[2]*q_inv[3] - intermediate[3]*q_inv[2]
    result_y = intermediate[0]*q_inv[2] + intermediate[2]*q_inv[0] + intermediate[3]*q_inv[1] - intermediate[1]*q_inv[3]
    result_z = intermediate[0]*q_inv[3] + intermediate[3]*q_inv[0] + intermediate[1]*q_inv[2] - intermediate[2]*q_inv[1]
    
    # Extract the vector part (x, y, z) and translate back
    rotated_point = np.array([result_x, result_y, result_z]) + axis_start
    
    return rotated_point
