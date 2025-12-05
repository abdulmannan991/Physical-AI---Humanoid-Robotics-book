---
id: installing-omniverse
title: "Module 4.1: Installing NVIDIA Omniverse"
sidebar_label: "4.1 - Installing Omniverse"
sidebar_position: 2
---

# Module 4.1: Installing NVIDIA Omniverse and Isaac Sim

To begin working with NVIDIA Isaac Sim, you first need to install the NVIDIA Omniverse Launcher and set up the necessary components. This chapter will guide you through the process of getting Omniverse and Isaac Sim ready on your system.

## Prerequisites

Before you start, ensure your system meets the minimum requirements, especially concerning your GPU.

:::warning GPU Requirement Reminder
NVIDIA Isaac Sim requires a powerful NVIDIA RTX GPU. Make sure your drivers are up to date. Performance will be significantly impacted on non-RTX cards.
:::

## Step-by-Step Installation

### 1. Download NVIDIA Omniverse Launcher

*   Go to the [NVIDIA Omniverse website](https://www.nvidia.com/omniverse/).
*   Download and install the **Omniverse Launcher**. This is your central hub for installing and managing Omniverse applications like Isaac Sim.

### 2. Install Omniverse Nucleus

After installing and opening the Launcher, you'll need to set up Omniverse Nucleus. Nucleus is the collaboration engine that allows you to manage and share USD assets.

*   In the Omniverse Launcher, navigate to the **"Nucleus"** tab.
*   Click **"Add Local Nucleus Service"** to install a local Nucleus server. This is essential for storing your USD files and project data. Follow the on-screen instructions to set up your username and password.

### 3. Install Isaac Sim

Once Nucleus is configured, you can install Isaac Sim.

*   In the Omniverse Launcher, navigate to the **"Exchange"** tab or **"Library"** > **"Apps"**.
*   Find **"Isaac Sim"** and click **"Install"**.
*   Choose your desired installation path. Isaac Sim is a large application, so ensure you have sufficient disk space (typically tens of gigabytes).

### 4. Configure Omniverse Cache

The Omniverse Cache service improves performance by storing frequently accessed data locally. It's crucial for a smooth experience with Isaac Sim.

*   In the Omniverse Launcher, go to the **"Cache"** tab.
*   Ensure the Cache service is running. If not, start it.
*   You can also configure the cache location and size here if needed.

### 5. Launch Isaac Sim

Once installed, you can launch Isaac Sim directly from the Omniverse Launcher.

*   Go to the **"Library"** > **"Apps"** tab.
*   Click **"Launch"** next to Isaac Sim.

Upon launching, Isaac Sim will open, and you'll see its interface. You are now ready to start creating and simulating robotic systems in a GPU-accelerated environment.