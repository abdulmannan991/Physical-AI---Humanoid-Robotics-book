---
id: openvla-setup
title: "Module 5.3: Setting up OpenVLA / RT-2"
sidebar_label: "5.3 - OpenVLA / RT-2 Setup"
sidebar_position: 4
---

# Module 5.3: Setting up OpenVLA / RT-2 for Local Execution

To truly understand Vision-Language-Action (VLA) models, hands-on experience is invaluable. This chapter will guide you through setting up and running a powerful VLA model locally, focusing on either OpenVLA or Google's RT-2 (Robotics Transformer 2) with quantized models for efficient execution on consumer-grade hardware.

:::info Note on Model Choices
OpenVLA is an open-source, performant VLA model designed for real-world robotic control. RT-2 from Google is another pioneering VLA model that directly translates visual and language inputs into robotic actions. Due to computational demands, we will focus on quantized versions of these models suitable for local deployment.
:::

## Prerequisites

Before you begin, ensure you have:

*   **Python Environment:** A Python 3.9+ environment with `pip`.
*   **GPU:** An NVIDIA GPU (preferably RTX series) with CUDA installed and configured. VLA models are computationally intensive.
*   **Disk Space:** Sufficient disk space for model weights (can be several gigabytes).

## Step-by-Step Setup: OpenVLA (Recommended for Open-Source)

OpenVLA provides a comprehensive framework for VLA research and deployment. Here's how to get started:

1.  **Clone the OpenVLA Repository:**
    ```bash
git clone https://github.com/OpenVLA/openvla.git
cd openvla
    ```
2.  **Install Dependencies:**
    ```bash
pip install -e .
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 # Adjust cu121 for your CUDA version
    ```
3.  **Download Quantized Model Weights:**
    Follow the instructions in the OpenVLA repository to download the pre-trained, quantized model weights. These are typically provided via Hugging Face Hub.
    ```bash
python scripts/download_model.py --model_name OpenVLA/OpenVLA-7B-v0-1 # Example command
    ```
4.  **Run an Example (e.g., Inference Script):**
    OpenVLA often comes with example scripts for inference. You can modify these to test your setup.
    ```bash
python examples/inference.py --model_path /path/to/your/downloaded/model
    ```
    This script will demonstrate how to load the model and perform basic vision-language inference.

## Step-by-Step Setup: RT-2 (Conceptual / Research Focus)

While RT-2 models are typically proprietary or part of larger research frameworks, public releases or similar architectures exist that can be run locally. The exact steps might vary based on the specific public implementation you choose (e.g., community-recreated versions or simplified demonstrations).

1.  **Find a Public RT-2 Implementation:** Search platforms like Hugging Face or GitHub for community implementations of RT-2 or similar Robotics Transformer models.
2.  **Install Dependencies:** Follow the `requirements.txt` or installation instructions provided with the chosen repository.
3.  **Download Model Weights:** Acquire the quantized model weights. For very large models, this might involve using `bitsandbytes` or `quantization` libraries.
4.  **Run Inference:** Use the provided example scripts to load the model and test its ability to generate actions from visual and linguistic inputs.

:::warning Local Performance
Even quantized VLA models are resource-intensive. Expect high GPU memory usage and potentially slow inference speeds on older or lower-end GPUs. Optimizing for inference speed (e.g., with ONNX Runtime, TensorRT) may be necessary for real-time robotic control.
:::

## Understanding the Output

The output of these VLA models will typically be in the form of "action tokens" or continuous action values. These outputs then need to be translated into commands that your robot can understand, which will be covered in the next chapter on the ROS 2 VLA bridge.

By successfully setting up and running a VLA model locally, you gain a tangible understanding of how these cutting-edge models operate and their potential for intelligent robotic control.