---
id: ros2-workspace-setup
title: "Module 2.2: Workspace Setup"
sidebar_label: "2.2 - Workspace Setup"
sidebar_position: 2
---

# Module 2.2: ROS 2 Workspace Setup

To begin developing with ROS 2, you need to set up a dedicated workspace. A ROS 2 workspace is a directory where you store your ROS 2 packages, build them, and manage their dependencies. This chapter will guide you through creating and building a typical ROS 2 workspace.

## Creating Your ROS 2 Workspace

First, let's create the workspace directory and a `src` folder inside it. The `src` folder is where your ROS 2 packages (e.g., your robot's code) will reside.

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

:::info `mkdir -p` Explained
*   `mkdir`: Creates directories.
*   `-p`: Ensures that parent directories are created if they don't already exist. If `~/ros2_ws` does not exist, it will be created along with `~/ros2_ws/src`.
:::

## Building Your Workspace with `colcon`

`colcon` is the recommended build tool for ROS 2. It orchestrates the compilation of multiple packages in your workspace, handling dependencies and ensuring proper build order.

After creating your workspace and placing your packages in the `src` directory, navigate to the root of your workspace (`~/ros2_ws`) and run the build command:

```bash
colcon build
```

:::info First Build Considerations
On your first build, `colcon` will compile all packages in your `src` directory, as well as any dependencies it finds. This might take some time depending on the number of packages and your system's specifications.
:::

## Sourcing the Setup File

After a successful build, `colcon` generates a `setup.bash` (or `setup.ps1` for PowerShell, `setup.zsh` for Zsh, etc.) file in your workspace's `install` directory (e.g., `~/ros2_ws/install/setup.bash`). This file sets up your environment variables so that ROS 2 knows where to find your newly built packages.

**You must source this file in every new terminal session where you intend to use your workspace packages.**

```bash
source install/setup.bash
```

:::warning Forgetting to Source
A common mistake for new ROS 2 users is forgetting to source the `setup.bash` file. If you run a ROS 2 command (e.g., `ros2 run <package_name> <node_name>`) and get an error like `[ERROR] [ros2cli]: 'ros2 run' requires a package name, and a node name to run.`, it's very likely that you haven't sourced your workspace setup file, or you've opened a new terminal without sourcing it again.
:::

To avoid repeatedly sourcing the setup file, you can add it to your shell's startup script (e.g., `~/.bashrc` for Bash, `~/.zshrc` for Zsh). However, be cautious when adding multiple ROS 2 setup files to your startup script, as this can lead to environment conflicts. It's often better to source the specific workspace you're working on when you need it.

By following these steps, you will have a functional ROS 2 workspace ready for developing your robotic applications.