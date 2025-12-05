---
id: ros2-python-nodes
title: "Module 2.3: Coding Python Nodes"
sidebar_label: "2.3 - Python Nodes"
sidebar_position: 3
---

# Module 2.3: Coding Python Nodes

One of the strengths of ROS 2 is its support for multiple programming languages. Python is a popular choice due to its readability and extensive libraries, making it ideal for rapid prototyping and complex AI algorithms. In this chapter, we will learn how to write a simple ROS 2 Python node.

## Creating a Simple Publisher (Talker) Node

Let's create a `minimal_publisher` node that continuously publishes a "Hello World" message to a topic.

First, ensure you have a ROS 2 package set up. If you don't, you can create one using:

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_python_pkg
```

Now, navigate into `my_python_pkg/my_python_pkg` (or your package's `src` equivalent) and create a file named `publisher_member_function.py`:

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Code Explanation (Line-by-Line)

*   **Lines 1-4: Imports**
    ```python
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    ```
    These lines import the necessary ROS 2 Python client library (`rclpy`), the base `Node` class, and the `String` message type from `std_msgs` (standard messages).

*   **Lines 6-8: Node Class Definition**
    ```python
    class MinimalPublisher(Node):
        def __init__(self):
            super().__init__('minimal_publisher')
    ```
    We define a class `MinimalPublisher` that inherits from `rclpy.node.Node`. In the constructor, `super().__init__('minimal_publisher')` initializes the ROS 2 node with the name `minimal_publisher`.

*   **Line 9: Create Publisher**
    ```python
    self.publisher_ = self.create_publisher(String, 'topic', 10)
    ```
    This line creates a publisher. It takes three arguments:
    1.  The message type (`String`).
    2.  The topic name (`'topic'`).
    3.  The quality-of-service (QoS) profile depth (`10`), which is the size of the message queue.

*   **Lines 10-12: Timer Setup**
    ```python
    timer_period = 0.5  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.i = 0
    ```
    A timer is created to call the `timer_callback` function every 0.5 seconds, which will publish messages periodically. `self.i` is an integer used to count the messages.

*   **Lines 14-18: Timer Callback Function**
    ```python
    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1
    ```
    This function is executed every time the timer fires. It creates a `String` message, populates its `data` field, publishes it using `self.publisher_.publish(msg)`, logs the published message, and increments the counter `self.i`.

*   **Lines 20-32: Main Function and Node Execution**
    ```python
    def main(args=None):
        rclpy.init(args=args)

        minimal_publisher = MinimalPublisher()

        rclpy.spin(minimal_publisher)

        minimal_publisher.destroy_node()
        rclpy.shutdown()


    if __name__ == '__main__':
        main()
    ```
    The `main` function is the entry point. `rclpy.init()` initializes the ROS 2 client library. An instance of `MinimalPublisher` is created. `rclpy.spin()` keeps the node alive, processing callbacks (like our timer callback) until `Ctrl+C` is pressed or `destroy_node()` is called. Finally, `destroy_node()` and `rclpy.shutdown()` properly clean up the ROS 2 resources.

## Running the Publisher Node

To make this node executable, you need to add an entry point in your `setup.py` file (located in the root of `my_python_pkg`).

In `setup.py`, find the `entry_points` dictionary and add the following:

```python
entry_points={
    'console_scripts': [
        'talker = my_python_pkg.publisher_member_function:main',
    ],
},
```

After modifying `setup.py`, rebuild your package and source your workspace:

```bash
cd ~/ros2_ws/
colcon build --packages-select my_python_pkg
source install/setup.bash
```

Now, you can run your talker node:

```bash
ros2 run my_python_pkg talker
```

This will start the publisher node, and you will see messages being printed to the console indicating that it's publishing "Hello World" messages.