---
id: importing-robots
title: "Module 4.3: Importing Robots into Isaac Sim"
sidebar_label: "4.3 - Importing Robots"
sidebar_position: 4
---

# Module 4.3: Importing Robots into Isaac Sim

To simulate a robot in NVIDIA Isaac Sim, you first need to bring its model into the Omniverse environment. The Unified Robot Description Format (URDF) is a common way to describe robots in the ROS ecosystem. Isaac Sim provides a powerful "URDF Importer" extension to facilitate this process, converting your URDF robot description into a USD asset.

## The URDF Importer Extension

The URDF Importer is an Isaac Sim extension that parses URDF files and converts them into USD. This process involves creating USD prims for each link and joint, assigning physics properties, and configuring visual meshes.

### Step-by-Step Guide to Importing a URDF Robot

1.  **Launch Isaac Sim:** Open NVIDIA Isaac Sim from the Omniverse Launcher.
2.  **Enable URDF Importer Extension:**
    *   Go to `Window > Extensions`.
    *   In the Extensions panel, search for "URDF Importer" and ensure it is enabled. You might need to search in the "Omni" or "Robotics" categories.
3.  **Open the URDF Importer Window:**
    *   Go to `Isaac Sim > Import > URDF`.
    *   This will open the URDF Importer panel.
4.  **Load Your URDF File:**
    *   In the URDF Importer panel, click the folder icon next to the "URDF File Path" field.
    *   Navigate to your `.urdf` file (or `.xacro` file, which the importer can also process if `xacro` is installed and configured in your environment) and select it.
5.  **Configure Import Settings:**
    *   **Scale:** Adjust if your URDF units don't match Isaac Sim's (meters by default).
    *   **Fix Base:** If your robot's base link should be fixed to the world, check this option.
    *   **Merge Fixed Joints:** Often useful to simplify the scene graph and improve performance.
    *   **Self-Collision:** Configure how self-collisions are handled.
    *   **Target Prim Path:** Specify where in the USD stage the robot model will be imported.
6.  **Import the Robot:**
    *   Click the **"Import"** button.
    *   Isaac Sim will process the URDF and import your robot onto the stage.

### Post-Import Adjustments

After importing, you may need to make some adjustments:

*   **Material and Textures:** Sometimes, materials or textures referenced in the URDF might not be automatically applied correctly. You may need to manually assign materials using the "Material Editor" in Isaac Sim.
*   **Physics Properties:** Review the automatically generated physics properties (mass, inertia, collision meshes) to ensure they accurately reflect your physical robot. You can modify these in the "Property" panel for each prim.
*   **ROS 2 Integration:** For ROS 2 communication, you'll typically add ROS 2 specific components (e.g., `ROS1 Bridge`, `ROS2 Bridge` extensions) and attach ROS 2 interfaces (like `ROS2 Publish Joint State`, `ROS2 Subscribe Twist`) to your robot prims.

By following these steps, you can effectively bring your robot models from URDF into NVIDIA Isaac Sim, paving the way for advanced simulation and AI training.