---
id: gazebo-comparison
title: "Module 3.1: Gazebo Classic vs. Ignition"
sidebar_label: "3.1 - Gazebo Comparison"
sidebar_position: 2
---

# Module 3.1: Gazebo Classic vs. Ignition (Gazebo)

Gazebo has been the de facto standard simulator in the ROS community for many years. However, with the evolution of robotics and simulation needs, a new generation of Gazebo, often referred to as Gazebo Ignition (or just Gazebo), has emerged. This chapter will compare these two powerful simulation platforms.

## Gazebo Classic

Gazebo Classic is the older, well-established version of the Gazebo simulator. It has been tightly integrated with ROS 1 for a long time and is still widely used in many existing projects.

:::info Key Features of Gazebo Classic
*   **Maturity:** Extensive community support and a vast library of existing models.
*   **ROS 1 Integration:** Deep integration with the ROS 1 ecosystem.
*   **Plugin System:** Allows for custom sensor models, control interfaces, and environmental interactions.
:::

## Gazebo Ignition (Gazebo)

Gazebo Ignition is the modern, re-architected version designed to be more modular, flexible, and future-proof. It is the officially supported simulator for ROS 2 and offers improved performance and advanced features.

:::info Key Features of Gazebo Ignition
*   **Modular Architecture:** Designed with a component-based structure, allowing for greater flexibility and independent development of features.
*   **ROS 2 Integration:** Natively integrates with ROS 2 through `ros_gz` bridges, facilitating seamless communication.
*   **Modern Graphics:** Improved rendering capabilities and graphical fidelity.
*   **Distributed Simulation:** Better support for simulating multiple robots and complex distributed systems.
*   **Physics Engines:** Supports multiple physics engines, including DART, ODE, and Bullet.
:::

## Comparison Table

| Feature           | Gazebo Classic                            | Gazebo Ignition (Gazebo)                       |
| :---------------- | :---------------------------------------- | :--------------------------------------------- |
| **ROS Version**   | Primarily ROS 1 (some ROS 2 bridges)      | Primarily ROS 2 (native integration)           |
| **Architecture**  | Monolithic                                | Modular, component-based                       |
| **Communication** | Custom protocols                          | DDS (Data Distribution Service)                |
| **Graphics**      | Older rendering engine                    | Modern rendering engine, improved graphics     |
| **Scalability**   | Limited for distributed systems           | Better support for multi-robot/distributed sim |
| **Development**   | Stable, less active new feature development | Active development, new features               |

## Installation Commands (for ROS Humble on Ubuntu)

To install Gazebo Classic and Ignition with ROS Humble, you would typically use the following commands:

:::info Gazebo Classic Installation
```bash
sudo apt install ros-humble-gazebo-ros-pkgs
```
This package includes the necessary ROS 2 bridges for Gazebo Classic.
:::

:::info Gazebo Ignition (Gazebo) Installation
```bash
sudo apt install ros-humble-ros-gz
```
This package provides the core Gazebo (Ignition) simulator and the `ros_gz` bridge for ROS 2 integration.
:::

Remember to source your ROS 2 environment after installation to ensure the tools are available in your terminal.