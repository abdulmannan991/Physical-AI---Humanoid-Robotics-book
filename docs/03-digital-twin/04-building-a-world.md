---
id: building-a-world
title: "Module 3.4: Building a Simple World"
sidebar_label: "3.4 - Building a World"
sidebar_position: 5
---

# Module 3.4: Building a Simple World

Creating custom simulation environments is essential for tailored robotics development and testing. Whether you need a simple maze for navigation, a complex factory floor, or a dynamic outdoor scene, simulators provide the tools to build these virtual worlds. This chapter will guide you through creating a basic maze environment in Gazebo.

## Creating a Simple Maze in Gazebo (SDF)

For defining custom worlds in Gazebo, the Simulation Description Format (SDF) is the standard. We will create a simple SDF file that defines a flat ground plane and a few walls to form a basic maze.

### Step 1: Create a World File

Create a new XML file, for example, `my_maze_world.world`, in your Gazebo resource path (e.g., `~/.gazebo/worlds/` or within a ROS 2 package resource directory). For simplicity, let's assume you place it in your current working directory for now.

```xml
<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="my_maze_world">

    <!-- Ground Plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Light Source -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Walls for the Maze -->
    <model name="wall_1">
      <pose>0 2 0.5 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>4 0.1 1</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri><name>Gazebo/Green</name></script></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>4 0.1 1</size></box></geometry>
        </collision>
      </link>
    </model>

    <model name="wall_2">
      <pose>-2 0 0.5 0 0 1.570796</pose> <!-- Rotated 90 degrees (pi/2 radians) -->
      <link name="link">
        <visual name="visual">
          <geometry><box><size>4 0.1 1</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri><name>Gazebo/Red</name></script></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>4 0.1 1</size></box></geometry>
        </collision>
      </link>
    </model>

    <model name="wall_3">
      <pose>0 -2 0.5 0 0 0</pose>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>4 0.1 1</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri><name>Gazebo/Blue</name></script></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>4 0.1 1</size></box></geometry>
        </collision>
      </link>
    </model>

    <model name="wall_4">
      <pose>2 0 0.5 0 0 1.570796</pose>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>4 0.1 1</size></box></geometry>
          <material><script><uri>file://media/materials/scripts/gazebo.material</uri><name>Gazebo/Yellow</name></script></material>
        </visual>
        <collision name="collision">
          <geometry><box><size>4 0.1 1</size></box></geometry>
        </collision>
      </link>
    </model>

  </world>
</sdf>
```

### Step 2: Launch the World in Gazebo

To open this world in Gazebo Ignition (Gazebo), you would use the `gz sim` command:

```bash
gz sim my_maze_world.world
```

If you are using Gazebo Classic, the command is:

```bash
gazebo my_maze_world.world
```

:::tip Understanding the SDF Elements
*   `<sdf version="1.6">`: Specifies the SDF version. Always use the latest compatible version.
*   `<world name="...">`: Defines a simulation world.
*   `<include><uri>model://...</uri></include>`: Includes predefined models (like `ground_plane` and `sun`) from Gazebo's model database.
*   `<model name="...">`: Defines a custom model (e.g., a wall).
*   `<pose>`: Sets the position (x y z) and orientation (roll pitch yaw in radians) of the model.
*   `<link name="...">`: Represents a rigid body of the model.
*   `<visual>`: Defines the visual appearance of the link.
*   `<geometry><box><size>...</size></box></geometry>`: Defines the shape and dimensions of the visual/collision element.
*   `<material>`: Applies a color or texture.
*   `<collision>`: Defines the physical properties for collision detection.
*   `<inertial>`: Defines mass and inertia properties (important for realistic physics).
:::

By following these steps, you can create and launch your own custom virtual environments for testing and simulating your robotic systems.