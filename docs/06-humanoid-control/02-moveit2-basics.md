---
id: moveit2-basics
title: "Module 6.2: MoveIt 2 Basics for Motion Planning"
sidebar_label: "6.2 - MoveIt 2 Basics"
sidebar_position: 3
---

# Module 6.2: MoveIt 2 Basics for Motion Planning

Motion planning is a fundamental aspect of robotic manipulation, ensuring that a robot can move its limbs or end-effector from a starting configuration to a target configuration without colliding with itself, obstacles in the environment, or even the objects it intends to interact with. **MoveIt 2** is the most widely used software suite for mobile manipulation in ROS 2, providing a comprehensive set of tools for motion planning, manipulation, and control.

## What is MoveIt 2?

:::info Definition: MoveIt 2
**MoveIt 2** is an open-source robotics manipulation platform for ROS 2. It integrates state-of-the-art motion planning algorithms, kinematics, collision checking, and control capabilities, allowing developers to easily enable complex manipulation tasks for a wide range of robotic arms and mobile manipulators.
:::

**Key Features of MoveIt 2:**

*   **Motion Planning:** Implements various sampling-based (e.g., OMPL, RRT-Connect, PRM) and optimization-based motion planners.
*   **Kinematics:** Integrates with KDL, OpenRave, or custom kinematics solvers for Forward and Inverse Kinematics.
*   **Collision Detection:** Uses FCL (Flexible Collision Library) for efficient collision checking between robot links and environmental objects.
*   **Robot State Monitoring:** Keeps track of the robot's current joint states and transforms.
*   **Manipulation Primitives:** Provides tools for common manipulation tasks like grasping, placing, and collision avoidance.
*   **Visualization:** Seamlessly integrates with RViz for real-time visualization of robot motion and planned trajectories.

## Core Concepts in MoveIt 2

### Planning Scene

The **Planning Scene** is MoveIt 2's internal representation of the robot and its environment. It includes:

*   The robot's URDF/SRDF model.
*   The current joint states of the robot.
*   Attached collision objects (objects held by the robot).
*   Known static and dynamic obstacles in the environment.

The Planning Scene is constantly updated with sensor data (e.g., from depth cameras) to maintain an accurate representation of the real world.

### Motion Planning Request

To plan a motion, you typically specify:

*   **Start State:** The robot's current configuration.
*   **Goal State:** A desired end-effector pose or joint configuration.
*   **Constraints:** Optional requirements like keeping the end-effector level, avoiding certain regions, or maintaining specific joint limits.

MoveIt 2 then uses its planners to find a collision-free trajectory that satisfies these criteria.

## Basic Workflow for Motion Planning (Python Example)

Here's a conceptual Python workflow using `moveit_commander` (a Python interface for MoveIt 2) to plan a simple motion:

```python
import rclpy
from moveit_commander import PlanningSceneInterface, MoveGroupCommander, RobotCommander

def main():
    rclpy.init()
    node = rclpy.create_node('moveit_simple_example')

    robot = RobotCommander(node=node)
    scene = PlanningSceneInterface(node=node)
    group = MoveGroupCommander("arm", node=node) # Replace "arm" with your robot's planning group

    # 1. Define a target pose for the end-effector
    pose_goal = geometry_msgs.msg.Pose()
    pose_goal.orientation.w = 1.0
    pose_goal.position.x = 0.4
    pose_goal.position.y = 0.1
    pose_goal.position.z = 0.4

    group.set_pose_target(pose_goal)

    # 2. Plan the motion
    plan = group.plan()

    if plan[0]: # Check if a plan was found
        node.get_logger().info("Motion plan found, executing...")
        group.execute(plan[1], wait=True)
    else:
        node.get_logger().warn("Could not plan motion to target pose.")

    group.stop()
    group.clear_pose_targets()

    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

:::tip Installation
To use MoveIt 2, you typically install it as part of your ROS 2 distribution (e.g., `sudo apt install ros-humble-moveit` for humble) and then configure it for your specific robot using the MoveIt Setup Assistant.
:::

MoveIt 2 is an indispensable tool for developing sophisticated robotic manipulation applications, providing a robust and flexible framework for motion planning and control.