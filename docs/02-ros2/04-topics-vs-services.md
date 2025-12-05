---
id: ros2-topics-services
title: "Module 2.4: Topics vs. Services"
sidebar_label: "2.4 - Topics vs. Services"
sidebar_position: 4
---

# Module 2.4: Topics vs. Services: Choosing the Right Communication

ROS 2 provides several communication mechanisms, each suited for different scenarios. While Topics are excellent for streaming data, sometimes a robot needs to request a specific action or piece of information and receive a direct response. This is where Services come into play. This chapter will clarify the distinction between Topics and Services and guide you on when to use each.

## Topics: Asynchronous Data Streams

As discussed in Module 2.1, Topics implement a publish/subscribe model. Publishers send messages without knowing or caring if anyone is listening, and subscribers receive messages without requesting them. This is a one-to-many or many-to-many asynchronous communication pattern.

:::info Use Cases for Topics
*   **Sensor Data:** Continuous streams from cameras, LiDARs, IMUs (Inertial Measurement Units), microphones.
*   **Robot State:** Odometry, joint states, battery level updates.
*   **Logging:** Outputting diagnostic information.
*   **Event Notifications:** Alerting other parts of the system to occurrences.
:::

## Services: Synchronous Request/Response

Services provide a synchronous request/response communication model. A client node sends a request to a service server node, and the service server processes the request and sends back a response. The client typically blocks (waits) until it receives a response or a timeout occurs.

:::info Use Cases for Services
*   **Discrete Actions:** Commanding a robot to perform a specific, one-time action (e.g., "move arm to position X," "take a picture").
*   **Configuration:** Changing a node's parameters (e.g., "set camera resolution to 1080p").
*   **Querying Information:** Requesting a specific piece of data that is not continuously streamed (e.g., "get current map," "what is the robot's battery percentage right now?").
*   **Calculations:** Requesting a computation to be performed (e.g., "calculate inverse kinematics for this pose").
:::

## Comparison: Topics vs. Services

The following table summarizes the key differences between Topics and Services:

| Feature             | Topics                                 | Services                               |
| :------------------ | :------------------------------------- | :------------------------------------- |
| **Communication Model** | Publish/Subscribe (asynchronous)     | Request/Response (synchronous)         |
| **Data Flow**       | One-way streaming                      | Two-way (request then response)        |
| **Timing**          | Continuous, periodic, or event-driven  | Discrete, on-demand                    |
| **Reliability**     | Best-effort (usually)                  | Guaranteed delivery (request/response) |
| **Use Case Example**| Sensor data streams, robot odometry    | Single commands, parameter changes     |
| **Blocking**        | Non-blocking                           | Client typically blocks                |

Choosing between Topics and Services depends on the nature of the data and the interaction required. For continuous data streams, Topics are efficient and scalable. For discrete actions or information requests that require a direct acknowledgment or result, Services are the appropriate choice.