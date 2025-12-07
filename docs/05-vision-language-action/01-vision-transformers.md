---
id: vision-transformers
title: "Module 5.1: Vision Transformers"
sidebar_label: "5.1 - Vision Transformers"
sidebar_position: 2
---

# Module 5.1: Vision Transformers: A New Paradigm for Visual Perception

For years, Convolutional Neural Networks (CNNs) were the undisputed champions of computer vision. However, with the groundbreaking success of Transformers in Natural Language Processing (NLP), researchers began exploring their application to visual tasks. This led to the development of **Vision Transformers (ViT)**, which have revolutionized how we approach visual perception in AI and robotics.

## CNNs vs. Vision Transformers (ViT)

### Convolutional Neural Networks (CNNs)

CNNs extract features from images by applying convolutional filters, which are highly effective at capturing local patterns (edges, textures). They use hierarchical layers to build more complex features from these local patterns. CNNs inherently understand spatial relationships due to their architecture.

**Pros:**

*   Excellent for local feature extraction.
*   Translationally equivariant.
*   Smaller datasets can yield good results.

**Cons:**

*   Limited global understanding (receptive field).
*   Can struggle with long-range dependencies.

### Vision Transformers (ViT)

Unlike CNNs, ViTs do not use convolutions. Instead, they treat an image as a sequence of smaller, non-overlapping patches, similar to how a Transformer processes a sequence of words (tokens) in NLP. Each patch is then linearly embedded and combined with positional information before being fed into a standard Transformer encoder.

:::info Key Idea: Patch Embeddings
The core idea behind ViT is to **tokenize** an image by splitting it into fixed-size patches, linearly embedding each patch, and then adding positional embeddings to retain spatial information. These patch embeddings are then treated as a sequence, allowing the Transformer's self-attention mechanism to learn global dependencies across the entire image.
:::

<Mermaid chart={`
graph LR;
    A[Input Image] --> B[Split into Patches (e.g., 16x16 pixels)];
    B --> C[Linear Embedding (Flatten + Dense Layer)];
    C --> D[Add Positional Embeddings];
    D --> E[Transformer Encoder];
    E --> F[Classification Head];
`} />

**Pros:**

*   Excellent for capturing global relationships and long-range dependencies.
*   Scales effectively with larger datasets and model sizes.
*   Achieves state-of-the-art performance on various vision tasks.

**Cons:**

*   Requires very large datasets for pre-training to achieve competitive performance (often pre-trained on huge image datasets like JFT-300M or ImageNet-21K).
*   Computationally more expensive for high-resolution images without specific optimizations.

## ViT in Robotics

In Physical AI, ViTs are becoming increasingly important for:

*   **Perception:** Robust object detection, semantic segmentation, and scene understanding from camera images.
*   **State Estimation:** Learning rich visual representations for robot localization and mapping.
*   **Foundation Models:** Serving as the visual backbone for multimodal models that integrate vision and language.

By processing visual information in a holistic, global manner, ViTs enable robots to develop a more comprehensive understanding of their operational environment, which is crucial for complex tasks and safe interaction.