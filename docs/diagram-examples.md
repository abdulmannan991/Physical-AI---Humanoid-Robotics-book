# Diagram Examples

This document demonstrates how to create various types of diagrams using Mermaid in this documentation.

## Flowchart Example

Flowcharts are useful for showing processes and decision trees:

```mermaid
flowchart TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> E[Fix Issue]
    E --> B
    C --> F[End]
```

## Sequence Diagram Example

Sequence diagrams show interactions between components over time:

```mermaid
sequenceDiagram
    participant User
    participant ROS2
    participant Robot
    participant Sensor

    User->>ROS2: Send Command
    ROS2->>Robot: Execute Action
    Robot->>Sensor: Request Data
    Sensor-->>Robot: Return Sensor Data
    Robot-->>ROS2: Action Complete
    ROS2-->>User: Confirm Success
```

## Class Diagram Example

Class diagrams illustrate object-oriented structures:

```mermaid
classDiagram
    class Robot {
        +String name
        +int id
        +move()
        +stop()
    }
    class Sensor {
        +String type
        +getData()
    }
    class Controller {
        +processInput()
        +sendCommand()
    }

    Robot "1" --> "many" Sensor
    Controller --> Robot
```

## State Diagram Example

State diagrams show different states and transitions:

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Moving: start_command
    Moving --> Processing: task_received
    Processing --> Moving: continue
    Processing --> Idle: task_complete
    Moving --> Idle: stop_command
    Idle --> [*]
```

## Gantt Chart Example

Gantt charts are useful for project timelines:

```mermaid
gantt
    title Robot Development Timeline
    dateFormat YYYY-MM-DD
    section Design
    Requirements Analysis    :a1, 2024-01-01, 30d
    System Architecture      :a2, after a1, 20d
    section Development
    Hardware Setup          :b1, 2024-02-01, 45d
    Software Development    :b2, after b1, 60d
    section Testing
    Integration Testing     :c1, after b2, 30d
    Field Testing          :c2, after c1, 20d
```

## Entity Relationship Diagram

ER diagrams show database or data model relationships:

```mermaid
erDiagram
    ROBOT ||--o{ SENSOR : has
    ROBOT ||--o{ ACTUATOR : controls
    ROBOT {
        int id
        string name
        string model
    }
    SENSOR {
        int id
        string type
        float reading
    }
    ACTUATOR {
        int id
        string type
        float position
    }
```

## Git Graph Example

Git graphs visualize version control workflows:

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
    branch feature
    checkout feature
    commit
    checkout main
    merge feature
```

## Pie Chart Example

Pie charts show proportional data:

```mermaid
pie title Robot Component Costs
    "Sensors" : 35
    "Actuators" : 30
    "Controller" : 20
    "Structure" : 15
```

## Mindmap Example

Mindmaps organize hierarchical information:

```mermaid
mindmap
  root((Physical AI))
    ROS2
      Nodes
      Topics
      Services
    Simulation
      Gazebo
      Isaac Sim
      Unity
    Control
      Kinematics
      Path Planning
      ML Control
    Perception
      Vision
      LIDAR
      Sensors
```

## Timeline Example

Timelines show chronological events:

```mermaid
timeline
    title History of Robotics Development
    2010 : First prototype
         : ROS integration
    2015 : Advanced sensors
         : Machine learning
    2020 : Humanoid features
         : VLA integration
    2025 : Production ready
         : Commercial deployment
```

## Usage Tips

### Syntax Highlighting

Always use the ` ```mermaid ` code fence for diagrams.

### Accessibility

Add descriptive text before diagrams to explain their purpose for screen readers and users who may have difficulty viewing diagrams.

### Performance

Keep diagrams simple and focused. Complex diagrams can be slow to render and difficult to understand.

### Responsive Design

Mermaid diagrams automatically scale to fit their container, making them mobile-friendly.

## Additional Resources

- [Mermaid Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/) - Test your diagrams online
- [Docusaurus Mermaid Plugin](https://docusaurus.io/docs/markdown-features/diagrams)
