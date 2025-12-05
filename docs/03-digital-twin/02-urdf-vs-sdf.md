---
id: urdf-vs-sdf
title: "Module 3.2: URDF vs. SDF"
sidebar_label: "3.2 - URDF vs. SDF"
sidebar_position: 3
---

# Module 3.2: URDF vs. SDF: Describing Robots and Worlds

When working with robotic simulators like Gazebo, you need a way to describe your robot's physical properties (links, joints, sensors) and the environment it operates in. ROS and Gazebo primarily use two XML-based formats for this purpose: URDF and SDF. This chapter will explain the differences and appropriate use cases for each.

## URDF: Unified Robot Description Format

:::info Definition: URDF
The **Unified Robot Description Format (URDF)** is an XML file format used in ROS to describe all elements of a robot. It focuses specifically on the kinematic and dynamic properties of a single robot, including its visual appearance, collision properties, and inertial characteristics. URDF is excellent for defining the structure of a robot in a modular way.
:::

**Key Characteristics of URDF:**

*   **Single Robot:** Designed to describe only one robot.
*   **Tree Structure:** Represents the robot as a tree-like kinematic chain (no loops allowed).
*   **Limited Environment Description:** Cannot describe complex environments, only the robot itself.
*   **Extensible:** Can be extended with `xacro` macros for more complex and parameterized robot descriptions.

### Simple URDF Link Example

Here's a basic example of a single link definition in URDF:

```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  <link name="base_link">
    <visual>
      <geometry>
        <cylinder length="0.6" radius="0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.6" radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.0" ixy="0.0" ixz="0.0" iyy="0.0" iyz="0.0" izz="0.0"/>
    </inertial>
  </link>
</robot>
```

This XML snippet describes a cylindrical `base_link` for a robot, including its visual properties (a blue cylinder), collision geometry, and inertial properties.

## SDF: Simulation Description Format

:::info Definition: SDF
The **Simulation Description Format (SDF)** is an XML file format designed to describe environments, objects, and robots for simulators like Gazebo. It is a more comprehensive format than URDF, capable of describing entire worlds, including terrain, lights, static objects, and multiple robots with their sensors and actuators.
:::

**Key Characteristics of SDF:**

*   **Full World Description:** Can describe anything in a simulation world, not just a single robot.
*   **Graph Structure:** Supports a full graph structure, allowing for kinematic loops (e.g., parallel linkages).
*   **Sensor and Plugin Support:** Natively supports various sensor types and simulator-specific plugins.
*   **Standard for Gazebo:** The primary format used by Gazebo for world and model descriptions.

## Why Two Formats?

Historically, URDF was developed for ROS to describe robots for visualization (like RViz) and basic kinematics, while SDF was created specifically for Gazebo to provide a complete description for physical simulation. Although SDF can describe robots, URDF remains popular in the ROS community due to its simplicity for defining robot kinematics.

Often, URDF files are converted to SDF for use in Gazebo, or a hybrid approach is taken where a URDF describes the robot, and an SDF describes the world around it.

Understanding both formats is crucial for effectively integrating your robot models into simulation environments.