---
title: "Chapter 3: Gait Generation"
---

# Chapter 3: Gait Generation

## Bipedal Locomotion

Bipedal locomotion refers to the act of moving on two legs. For humanoids, this is a complex task that requires careful coordination of multiple joints and precise balance control. Unlike wheeled robots, bipedal robots must contend with dynamic stability issues, where the center of mass constantly shifts during movement.

## Zero Moment Point (ZMP)

The Zero Moment Point (ZMP) is a crucial concept in bipedal locomotion, particularly for maintaining stability. The ZMP is the point on the ground where the net moment of all forces (gravity, inertia, and ground reaction forces) is zero. If the ZMP remains within the robot's support polygon (the convex hull of its ground contact points), the robot is considered statically stable. For dynamic walking, the ZMP often moves, but its trajectory must be carefully controlled to prevent the robot from falling.

## Inverted Pendulum Model

The Inverted Pendulum Model is a simplified representation commonly used to understand and control bipedal locomotion. In this model, the robot's body is treated as a point mass at the top of an inverted pendulum, with the leg acting as the rigid link. The goal is to control the ankle torque to keep the center of mass over the support region, or to steer its trajectory. This model is fundamental for developing gait patterns and balance control strategies.

## Strict Stability

Strict stability in bipedal locomotion implies that the robot can maintain its balance even in the presence of external disturbances or variations in terrain. This often involves robust control strategies that actively adjust joint torques and foot placements to keep the ZMP within acceptable bounds. Achieving strict stability is challenging but essential for safe and reliable humanoid operation in unstructured environments. Advanced control methods often combine ZMP-based planning with feedback control to achieve robust dynamic walking.