---
id: unity-robotics-hub
title: "Module 3.3: Unity Robotics Hub"
sidebar_label: "3.3 - Unity Robotics Hub"
sidebar_position: 4
---

# Module 3.3: Unity Robotics Hub

While Gazebo is prevalent in the ROS community, Unity offers a powerful alternative for high-fidelity visualization, advanced physics, and rich interactive environments, especially when photo-realistic rendering or complex human-robot interaction is desired. The Unity Robotics Hub provides tools to integrate Unity projects with ROS 2, enabling sophisticated simulation capabilities.

## Introduction to Unity Robotics Hub

The Unity Robotics Hub is a collection of Unity packages designed to facilitate robotics development within the Unity ecosystem. It includes:

*   **ROS-TCP-Connector:** Enables seamless communication between Unity and ROS 2 via TCP sockets, allowing Unity to act as a ROS 2 node.
*   **ROS-Unity-Message-Generation:** Tools to generate C# message types from ROS `.msg` and `.srv` definitions, ensuring type-safe communication.
*   **URDF Importer:** Imports URDF files directly into Unity, converting robot models into Unity GameObjects.
*   **Robotics Simulation:** Provides foundational tools for building and interacting with robotic simulations in Unity.

## Setting up the Unity-ROS TCP Connector

To establish communication between your Unity simulation and your ROS 2 environment, you need to set up the ROS-TCP-Connector. This involves both Unity project configuration and running a ROS 2 bridge.

### In your Unity Project:

1.  **Create a new Unity Project:** Open Unity Hub and create a new 3D (URP or HDRP recommended) project.
2.  **Install Robotics Hub Packages:**
    *   Go to `Window > Package Manager`.
    *   Click the `+` icon -> `Add package from git URL...`.
    *   Add `com.unity.robotics.ros-tcp-connector`.
    *   This will automatically pull in other necessary Robotics Hub packages like Message Generation.
3.  **Configure ROS TCP Connector:**
    *   In your Unity scene, create an empty GameObject and name it `ROSConnection`.
    *   Add the `ROSConnection` script component to this GameObject (`Add Component > ROSConnection`).
    *   Configure the `ROS IP Address` (usually your ROS 2 machine's IP) and `ROS Port` (default 10000).
4.  **Generate ROS Messages (C#):**
    *   Follow the instructions provided by the ROS-Unity-Message-Generation package to import your ROS 2 `.msg` and `.srv` files and generate their C# equivalents. This typically involves placing your `.msg`/`.srv` files in a specific folder (e.g., `Assets/ROSMessages`) and using a Unity editor tool.

### In your ROS 2 Environment:

1.  **Install ROS-TCP-Endpoint:**
    ```bash
    sudo apt install ros-humble-ros-tcp-endpoint
    ```
    (Replace `humble` with your ROS 2 distribution if different).
2.  **Run the ROS-TCP-Endpoint:**
    ```bash
    ros2 run ros_tcp_endpoint default_server
    ```
    This command starts the TCP server that your Unity application will connect to.

:::tip Network Configuration
Ensure your firewall allows connections on the specified ROS Port (default 10000). If Unity and ROS 2 are on different machines, make sure they can communicate over the network.
:::

Once both the Unity project and the ROS 2 endpoint are configured, your Unity application can send and receive ROS messages, allowing it to function as a powerful simulator or visualization tool within your ROS 2 robotics ecosystem.