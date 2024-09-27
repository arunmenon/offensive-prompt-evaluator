---

# **Offensive Image Prompt Evaluation Framework**

This repository provides a framework to compare the **efficacy of different prompt templates** against an offensive image dataset using GPT models for image classification. It helps evaluate multiple prompts and measure their performance by comparing model predictions with a labeled ground truth dataset. Additionally, the framework supports **prompt metadata generation** using GPT-4, enabling prompt scoring, versioning, and governance.

## **1. Overview of the Framework**

### **Purpose**:
The primary goal of this framework is to automate the comparison of different prompts to identify offensive images based on a pre-labeled ground truth dataset. The framework handles:
- **Batch processing of images**: Evaluates a dataset of images and checks each image using different prompt templates.
- **Prompt comparison**: Compares multiple prompt templates and measures their accuracy and efficiency in detecting offensive content.
- **Dynamic prompt handling**: It includes a **dynamic prompt loader**, which allows the system to load prompts and their corresponding exception rules from external files, making the framework adaptable to new rules or prompt formats.
- **Prompt metadata generation**: Automates metadata extraction and prompt scoring using GPT-4, enabling **prompt governance** and tracking prompt evolution over time.

### **Current Prompts**:
The prompts currently implemented in this framework are designed to detect offensive content such as:
- **Nudity or sexually suggestive content**
- **Hate speech or discriminatory symbols**
- **Graphic and violent imagery**
- **Misleading or harmful information**
- **Illegal or unsafe products**

Each of these prompts is dynamically loaded and can be adjusted based on evolving requirements. The framework is built to accommodate customizable exclusions (e.g., educational or artistic contexts), which are loaded dynamically to handle edge cases (e.g., classical art depictions of nudity).

---

### **Third Prompt Template: Structure and Exclusions**

The **third prompt template** is specifically designed to incorporate **exclusions** or **exceptions** dynamically from a configuration file. This allows for more precise handling of edge cases such as classical art or medical content, which might otherwise be flagged incorrectly.

#### **Template Structure**:
The third prompt is structured to flag offensive content while considering specific **exceptions**. The prompt will dynamically fill in exclusions based on a JSON configuration file that defines rules and edge cases for each category. 

#### **Combining with Exclusions**:
The **exclusions** (like **Classical Art**, **Medical Content**, etc.) are pulled dynamically from a **separate configuration file** (e.g., `exceptions.json`). The system injects these exclusions into the prompt based on predefined rules for each category.

#### **Example Exclusions Configuration (`exceptions.json`)**:
```json
{
    "nudity": {
        "exceptions": [
            {
                "type": "classical_art",
                "description": "Full or partial nudity in classical art or educational materials is acceptable."
            },
            {
                "type": "medical_content",
                "description": "Nudity in medical or educational products related to anatomy may be acceptable if properly labeled."
            }
        ]
    },
    "violence": {
        "exceptions": [
            {
                "type": "fictional_media",
                "description": "Imagery of violence in books, movies, or video games may be acceptable, provided it aligns with product labeling."
            },
            {
                "type": "self_defense",
                "description": "Items such as pepper spray might depict controlled violence for self-defense purposes."
            }
        ]
    }
    // Additional categories...
}
```

The **dynamic prompt loader** reads this configuration and inserts the relevant exclusions into the prompt template when generating the final prompts.

---

## **2. Prompt Metadata Generation and Prompt Governance**

In addition to evaluating the efficacy of prompts, this framework supports **prompt metadata generation** using **GPT-4**. The **Prompt Metadata Generator** script enables automated extraction of key information about each prompt, including **title**, **summary**, **content categories**, **scope**, **risk sensitivity**, **prompt score**, and **score reasoning**.

### **1. GPT-4 Powered Scoring Mechanism**:
- The framework uses **GPT-4** to analyze each prompt and extract relevant metadata. This process includes generating a **short summary**, categorizing the content (e.g., nudity, violence), and providing a **score** between 1 and 5.
- **Scoring Criteria**: The score reflects how clear, safe, and reliable the prompt is, based on GPT-4’s understanding of the prompt structure and its ability to handle exceptions. A score of 5 indicates a highly reliable prompt, while lower scores might indicate areas for improvement.

### **2. Versioning Support**:
- **Versioning**: Each prompt’s metadata is version-controlled. This allows tracking the **evolution of prompts** over time, making it possible to see how a prompt has changed or improved after adjustments.
- **Change Detection**: The framework compares the latest version of each prompt with the previous versions and identifies **similarities** or **differences** using **cosine similarity**. Minor changes are marked as “Slightly updated,” while significant changes trigger a new version.

### **3. Benefits for Prompt Governance**:
- **Prompt Governance**: The **metadata generation** and **versioning** features are essential for **prompt governance**, as they allow stakeholders to:
  - **Track prompt evolution**: Understand how prompts are evolving in terms of scope, exclusions, and overall clarity.
  - **Monitor prompt quality**: Review prompt scores and adjust the templates based on the performance or feedback from the evaluation.
  - **Ensure compliance**: Make sure that prompts follow the guidelines for detecting offensive content, while considering appropriate exceptions for specific content types.
  - **Version Control**: Revert to previous versions if required and compare performance metrics across versions.

### **Example of Prompt Metadata CSV**:
The prompt metadata is stored in a CSV file (`prompt_metadata.csv`), which includes versioned records of each prompt. Here's an example of how the metadata is structured:

```plaintext
Prompt File Location,Version,Prompt Title,Creation Date,Last Modified Date,Summary,Content Categories,Prompt Scope,Risk Sensitivity,Prompt Score,Score Reason
./prompts/Prompt1.txt,1,Product Image Content Analysis,2024-09-26 17:45:56,2024-09-26 17:40:47,This prompt asks for an analysis of a product image for offensive content.,Image Analysis, Content Moderation, Specific, High, 5, The prompt is clear, specific, and promotes the detection of offensive content.
./prompts/Prompt2.txt,1,Product Description Evaluation,2024-09-26 23:27:14,2024-09-26 17:49:42,Evaluate product descriptions for offensive content.,Nudity, Violence, Hate Speech, Broad, Medium, 4, Provides detailed guidelines but may need adjustments for cultural sensitivity.
./prompts/Prompt1.txt,2,Product Image Content Analysis,2024-09-26 17:45:56,2024-09-27 09:30:47,Slightly updated: Review product image for potential violations.,Nudity, Violence, Image Analysis, Specific, High, 5, Same as before.
./prompts/Prompt2.txt,2,Product Description Evaluation,2024-09-26 23:27:14,2024-09-27 09:32:42,Updated for clarity and additional content categories.,Nudity, Violence, Hate Speech, Misleading Content, Broad, Medium, 5, Adjustments made for a broader coverage of violations.
```

In this example:
- **Versioning**: You can see how each prompt evolves with updates to the title, summary, categories, and score.
- **Content Categories**: Reflects the list of offensive content types the prompt addresses.
- **Scope and Risk Sensitivity**: Indicate whether the prompt is broad or specific and the associated risks.
- **Scoring**: Provides a score that reflects the overall quality of the prompt.

With this metadata, you can better manage and govern how prompts evolve and perform over time.

---

## **3. Folder Structure**

The project is structured as follows:

```plaintext
.
├── downloaded_images/             # Folder containing images for evaluation.
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── prompts/                       # Folder containing dynamically generated prompts.
│   ├── Prompt1.txt
│   ├── Prompt2.txt
│   └── ...
├── prompt_templates/              # Folder containing prompt templates with placeholders.
│   ├── template1.txt
│   └── template2.txt
├── guidelines/                    # Folder containing exception rules and safety guidelines.
│   ├── safety_guidelines.json
│   └── exceptions.json            # File containing exception rules for each category.
├── results/                       # Folder where the evaluation results are stored.
│   └── metrics_Prompt1.txt
├── prompt_metadata.csv            # CSV file that stores the metadata generated for each prompt.
├── Image-downloader.py            # Script for downloading images from URLs.
├── prompt_eval.py                 # Main script for evaluating prompts against the image dataset.
├── prompt_loader.py               # Script for dynamically loading prompts and handling exceptions.
├── prompt_metadata_gen.py         # Script for generating prompt metadata using GPT-4.
└── Images_Ground_Truth.csv        # CSV file containing the image paths and their ground truth labels.
```

---

## **4. How to Run the Scripts

**

### **Running the Dynamic Prompt Loader**:
To load prompts dynamically, run the following command:
```bash
python3 prompt_loader.py --template_path prompt_templates/ --guidelines_path guidelines/safety_guidelines.json --exclusions_path guidelines/exceptions.json --output_path prompts/
```

### **Running the Prompt Metadata Generation**:
To generate prompt metadata, run the following command:
```bash
python3 prompt_metadata_gen.py --prompts_folder ./prompts/ --output_file prompt_metadata.csv
```

This script will:
- Generate metadata using **GPT-4** for each prompt.
- Score prompts and track their versions in the **prompt_metadata.csv** file.

---
