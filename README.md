# Physical AI & Humanoid Robotics Course

[![Docusaurus](https://img.shields.io/badge/Built%20with-Docusaurus-green)](https://docusaurus.io/)
[![Node.js](https://img.shields.io/badge/Node.js-%3E%3D20.0-brightgreen)](https://nodejs.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A comprehensive, interactive digital textbook for learning Physical AI and Humanoid Robotics. This course covers everything from ROS 2 fundamentals to advanced topics like Vision-Language-Action models, humanoid control systems, and deployment on real hardware.

## About the Project

This is an advanced course designed to equip learners with the knowledge and practical skills to develop intelligent systems that interact with the physical world. The course focuses on embodied AI systems that use sensors to understand their surroundings and actuators to perform physical tasks.

### Course Topics

- **Module 1: Physical AI Foundations** - Understanding the Perception-Action Loop and fundamental concepts
- **Module 2: ROS 2 Fundamentals** - Robot Operating System architecture, nodes, topics, and services
- **Module 3: Digital Twin Development** - Gazebo, Unity Robotics Hub, URDF/SDF modeling
- **Module 4: NVIDIA Isaac Sim** - Advanced simulation, USD fundamentals, and Isaac Lab
- **Module 5: Vision-Language-Action Models** - CLIP, OpenVLA, and multimodal AI integration
- **Module 6: Humanoid Control Systems** - Inverse kinematics, MoveIt2, gait generation, and RL control

### Learning Paths

This course offers three distinct hardware implementation paths:

1. **Digital Twin (Simulation Only)** - Work with Gazebo and NVIDIA Isaac Sim without physical hardware
2. **Edge AI Kit (Physical Hardware)** - Deploy AI models on embedded systems with real robots
3. **Cloud Robotics (Remote Access)** - Control physical robots remotely via cloud infrastructure

## Getting Started

### Prerequisites

- **Node.js** >= 20.0
- **Yarn** package manager
- Basic knowledge of Python, Linux, and mathematics (Linear Algebra & Calculus)

### Clone the Repository

```bash
git clone https://github.com/ai-humanoid-book/ai-book.git
cd ai-book
```

### Installation

Install all dependencies using Yarn:

```bash
yarn
```

Or using npm:

```bash
npm install
```

### Local Development

Start the development server:

```bash
yarn start
```

This command starts a local development server and opens up a browser window at `http://localhost:3000`. Most changes are reflected live without having to restart the server.

### Build for Production

Generate static content for deployment:

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Preview Production Build

After building, you can preview the production build locally:

```bash
yarn serve
```

## Project Structure

```
ai-book/
├── docs/              # Course content (Markdown files)
│   ├── 01-intro/      # Physical AI Foundations
│   ├── 02-ros2/       # ROS 2 Fundamentals
│   ├── 03-digital-twin/   # Digital Twin Development
│   ├── 04-isaac-sim/  # NVIDIA Isaac Sim
│   ├── 05-vision-language-action/  # VLA Models
│   └── 06-humanoid-control/   # Humanoid Control Systems
├── src/               # Custom React components and styling
├── static/            # Static assets (images, files)
├── docusaurus.config.ts  # Docusaurus configuration
├── sidebars.ts        # Sidebar navigation structure
└── package.json       # Project dependencies and scripts
```

## Features

- **Interactive Learning** - Built with Docusaurus for a modern documentation experience
- **Mermaid Diagrams** - Visual representations of concepts and architectures
- **Math Support** - KaTeX integration for mathematical equations
- **Code Highlighting** - Syntax highlighting for multiple programming languages
- **Dark Mode** - Automatic theme switching based on system preferences
- **Responsive Design** - Mobile-friendly interface

## Deployment

### GitHub Pages

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

This command builds the website and pushes to the `gh-pages` branch.

### Vercel / Netlify

This project can also be deployed to modern hosting platforms like Vercel or Netlify. Simply connect your repository and these platforms will automatically build and deploy your site.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Technology Stack

- **Docusaurus 3.9.2** - Static site generator
- **React 19** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Mermaid** - Diagram and flowchart generation
- **KaTeX** - Math typesetting
- **Prism** - Syntax highlighting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Docusaurus](https://docusaurus.io/)
- Special thanks to the ROS 2, NVIDIA Isaac Sim, and Physical AI communities

## Support

If you encounter any issues or have questions, please:
- Open an issue in the GitHub repository
- Check the [Docusaurus documentation](https://docusaurus.io/docs)
- Review existing course materials in the `docs/` directory

---

**Happy Learning!** Start your journey into Physical AI and Humanoid Robotics today.
