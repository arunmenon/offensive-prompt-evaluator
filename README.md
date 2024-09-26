# **Offensive Image Prompt Eval Framework**

This repository provides a framework to compare the **efficacy of different prompt templates** against an offensive image dataset using GPT models for image classification. It helps evaluate multiple prompts and measure their performance by comparing model predictions with a labeled ground truth dataset. This framework is designed to automate the process of running prompts against a dataset, collecting results, and calculating precision, recall, and F1-score metrics for each prompt.

## **1. Overview of the Framework**

### **Purpose**:
The primary goal of this framework is to automate the comparison of different prompts to identify offensive images based on a pre-labeled ground truth dataset. The framework handles:
- **Batch processing of images**: Evaluates a dataset of images and checks each image using different prompt templates.
- **Prompt comparison**: Compares multiple prompt templates and measures their accuracy and efficiency in detecting offensive content.
- **Dynamic prompt handling**: It includes a **dynamic prompt loader**, which allows the system to load prompts and their corresponding exception rules from external files, making the framework adaptable to new rules or prompt formats.

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

### **Template Structure**:
The third prompt is structured to flag offensive content while considering specific **exceptions**. The prompt will dynamically fill in exclusions based on a JSON configuration file that defines rules and edge cases for each category. 

#### **Example Prompt Template**:
```plaintext
Context: You are tasked with evaluating product images and descriptions in a catalog. Your goal is to flag products that violate the following offensive content guidelines as specified by the Trust and Safety Team, while also considering predefined exceptions.

Categories to Evaluate with Exceptions:

1. Nudity and Sexually Suggestive Content
    Flag Criteria:
    - Does the image contain nudity, partial nudity, or sexually suggestive content?

    Exceptions: 
    - Classical Art: Full or partial nudity in classical art or educational materials may be exempt from flagging, as long as the context clearly indicates educational or artistic value.

2. Violence and Dangerous Activities
    Flag Criteria:
    - Does the product promote or depict violence, self-harm, or dangerous activities?

    Exceptions:
    - Fictional Media Products: Imagery of violence may be acceptable for books, movies, or video games.

[Other categories and their exceptions continue...]

Instructions for Flagging:
- Review the product image and description.
- Provide a detailed assessment, structured as follows:
    - Offensive: true/false
    - Issues:
        - Nudity: true/false
        - Violence: true/false
        - Hate Speech: true/false
        - [other categories...]

    - Exception Applied: true/false
    - Reason: Provide an explanation for why the product is flagged, if applicable.
```

### **Combining with Exclusions**:
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

## **2. Folder Structure**

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
├── Image-downloader.py            # Script for downloading images from URLs.
├── prompt_eval.py                 # Main script for evaluating prompts against the image dataset.
├── prompt_loader.py               # Script for dynamically loading prompts and handling exceptions.
└── Images_Ground_Truth.csv        # CSV file containing the image paths and their ground truth labels.
```

---

## **3. How to Run the Scripts**

### **Running the Dynamic Prompt Loader**:
To load prompts dynamically, run the following command:
```bash
python3 prompt_loader.py --template_path prompt_templates/ --guidelines_path guidelines/safety_guidelines.json --exclusions_path guidelines/exceptions.json --output_path prompts/
```

This script will:
- Read prompt templates from the `prompt_templates/` folder.
- Load safety rules and exclusions from the `guidelines/` folder.
- Dynamically generate the final prompts and save them into the `prompts/` folder.

### **Running the Prompt Evaluation**:
Once the prompts are loaded, you can evaluate the image dataset using the **prompt_eval.py** script.

```bash
python3 prompt_eval.py --image_dataset ./downloaded_images/Images_Ground_Truth.csv --prompts_folder prompts/ --output results/
```

---

## **4. Key Benefits of This Framework**

### **1. Prompt Evaluation**:
- Provides a structured way to compare the efficacy of different prompts for detecting offensive content in product images.
- Automatically calculates key metrics such as **precision**, **recall**, and **F1-score** to help you evaluate the performance of each prompt.

### **2. Dynamic Prompt Loading**:
- **Exclusions Injection**: The dynamic prompt loader injects specific exclusions like "classical art" and "medical content" from the `exceptions.json` file into the prompt templates, making the system flexible to account for exceptions.
- **Flexibility**: Modify and load new prompts or exceptions without altering the core code.
- **Scalability**: Easily add more prompts or adjust the detection rules as new offensive categories or guidelines are introduced.

### **3. Scalable and Maintainable**:
- This framework can scale as more prompts and images are added. It also makes it easy to maintain the system since prompts and rules are stored externally and can be updated independently.

### **4. Versatile Application**:
- You can use this framework not only for offensive content detection but also for other use cases, such as detecting harmful, misleading, or illegal products, depending on how the prompts and guidelines are configured.

---

With these updates, the ReadMe should now offer a clear understanding of how the **third prompt template** is structured and how the **exclusions** are handled dynamically, along with the rest of the project's functionality.

Let me know if you'd like to refine any other parts!