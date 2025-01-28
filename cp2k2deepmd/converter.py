# cp2k2deepmd/converter.py

import os
import json
import numpy as np

def ensure_directory(path):
    """Ensure that a directory exists."""
    os.makedirs(path, exist_ok=True)
    print(f"Ensured directory exists: {path}")

def read_energy(ener_file):
    """Read and convert energy values from the energy file."""
    conversion_factor = 27.211386245  # a.u. to eV
    energies = []
    with open(ener_file, "r") as file:
        next(file)  # Skip header
        for line in file:
            columns = line.split()
            if len(columns) > 4:
                try:
                    energies.append(float(columns[4]) * conversion_factor)
                except ValueError:
                    continue
    return np.round(energies, 9).astype(np.float64)

def read_forces(frc_file, conversion_factor):
    """Read and convert forces from the force file."""
    forces = []
    frame = []
    with open(frc_file, "r") as file:
        for line in file:
            cols = line.split()
            if len(cols) == 1:
                if frame:
                    forces.append(np.array(frame).flatten())
                    frame = []
            elif len(cols) == 4:
                try:
                    converted = [float(col) * conversion_factor for col in cols[1:4]]
                    frame.append(converted)
                except ValueError:
                    continue
        if frame:
            forces.append(np.array(frame).flatten())
    return np.round(forces, 9).astype(np.float64)

def read_positions(pos_file):
    """Read and process coordinates from the position file."""
    positions = []
    frame = []
    with open(pos_file, "r") as file:
        for line in file:
            cols = line.split()
            if len(cols) == 1:
                if frame:
                    positions.append(np.array(frame).flatten())
                    frame = []
            elif len(cols) == 4:
                try:
                    coords = [float(col) for col in cols[1:4]]
                    frame.append(coords)
                except ValueError:
                    continue
        if frame:
            positions.append(np.array(frame).flatten())
    return np.round(positions, 9).astype(np.float64)

def read_cell(cell_file):
    """Read box dimensions from the cell file."""
    boxes = []
    with open(cell_file, "r") as file:
        next(file)  # Skip header
        for line in file:
            cols = line.split()
            if len(cols) >= 11:
                try:
                    box = [float(col) for col in cols[2:11]]
                    boxes.append(box)
                except ValueError:
                    continue
    return np.array(boxes, dtype=np.float64)

def extract_elements(pos_file):
    """Extract element types and create mapping."""
    with open(pos_file, "r") as file:
        lines = file.readlines()
    
    elements = []
    frame_start_idx = -1
    frame_end_idx = -1
    for i, line in enumerate(lines):
        if "i =" in line:
            if frame_start_idx == -1:
                frame_start_idx = i  # First frame start
            elif frame_end_idx == -1:
                frame_end_idx = i  # Second frame start
                break
    
    if frame_start_idx != -1 and frame_end_idx != -1:
        for line in lines[frame_start_idx + 1 : frame_end_idx - 1]:
            cols = line.split()
            if cols:
                elements.append(cols[0])
    else:
        raise ValueError("Could not find valid frame data.")
    
    unique_elements = list(dict.fromkeys(elements))  # Preserve order
    element_map = {elem: idx for idx, elem in enumerate(unique_elements)}
    element_indices = [element_map[elem] for elem in elements]
    
    return np.array(element_indices, dtype=np.int32), np.array(unique_elements, dtype=str)

def load_config(config_path):
    """Load configuration from a JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r") as file:
        config = json.load(file)
    return config

def cp2k2deepmd(config_path):
    """
    Convert CP2K output files to DeepMD format based on a JSON configuration file.

    Parameters:
    - config_path (str): Path to the JSON configuration file.
    """
    # Load configuration
    config = load_config(config_path)
    
    # Extract parameters with defaults
    base_path = config.get("base_path")
    ener_file = config.get("ener_file")
    frc_file = config.get("frc_file")
    pos_file = config.get("pos_file")
    cell_file = config.get("cell_file")
    interval = config.get("interval", 1)
    
    if not all([base_path, ener_file, frc_file, pos_file, cell_file]):
        raise ValueError("Missing required configuration parameters.")
    
    deepmd_path = os.path.join(base_path, "deepmd")
    set_folder = os.path.join(deepmd_path, "set.000")
    
    # Ensure directories exist
    ensure_directory(deepmd_path)
    ensure_directory(set_folder)
    
    # Energy
    energy = read_energy(ener_file)[::interval]
    energy_file_out = os.path.join(set_folder, "energy.npy")
    np.save(energy_file_out, energy)
    print(f"Energy saved to: {energy_file_out}")
    
    # Forces
    conversion_factor = 27.211386245 / 0.529177210  # Hartree/Bohr to eV/Å
    forces = read_forces(frc_file, conversion_factor)[::interval]
    forces_file_out = os.path.join(set_folder, "force.npy")
    np.save(forces_file_out, forces)
    print(f"Forces saved to: {forces_file_out}")
    
    # Positions
    positions = read_positions(pos_file)[::interval]
    positions_file_out = os.path.join(set_folder, "coord.npy")
    np.save(positions_file_out, positions)
    print(f"Positions saved to: {positions_file_out}")
    
    # Cell
    cells = read_cell(cell_file)[::interval]
    cell_file_out = os.path.join(set_folder, "box.npy")
    np.save(cell_file_out, cells)
    print(f"Box dimensions saved to: {cell_file_out}")
    
    # Elements
    element_indices, unique_elements = extract_elements(pos_file)
    element_indices = element_indices
    
    type_file = os.path.join(deepmd_path, "type.raw")
    type_map_file = os.path.join(deepmd_path, "type_map.raw")
    np.savetxt(type_file, element_indices, fmt="%d")
    np.savetxt(type_map_file, unique_elements, fmt="%s")
    print(f"Element indices saved to: {type_file}")
    print(f"Element map saved to: {type_map_file}")
