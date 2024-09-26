# **Offensive Image Prompt Eval Framework**

This repository provides a framework to compare the **efficacy of different prompt templates** against an offensive image dataset, using GPT models for image classification. It helps evaluate multiple prompts and measure their performance by comparing model predictions with a labeled ground truth dataset. This framework is designed to automate the process of running prompts against a dataset, collecting results, and calculating precision, recall, and F1-score metrics for each prompt.

## **1. Overview of the Framework**

### **Purpose**:
The primary goal of this framework is to automate the comparison of different prompts to identify offensive images based on a pre-labeled ground truth dataset. The framework is designed to handle:
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
  
Each of these prompts is dynamically loaded and can be adjusted based on evolving requirements. The framework is built to accommodate customizable exceptions (e.g., educational or artistic contexts), which are also loaded dynamically to handle edge cases (e.g., classical art depictions of nudity).

### **Dynamic Prompt Loader**:
The **Dynamic Prompt Loader** allows you to easily manage and modify the prompts used for image analysis. You can define new prompt templates or modify existing ones and load them at runtime without changing the underlying codebase. It also ensures that exceptions (such as classical art or medical content) are dynamically integrated into the prompt logic.

This system provides:
- **Flexibility**: Modify and load new prompts or exceptions without altering the core code.
- **Scalability**: Easily add more prompts or adjust the detection rules as new offensive categories or guidelines are introduced.
- **Maintainability**: Prompts and their corresponding rules can be managed as external files, making it easier to iterate and refine over time.

---

## **2. Folder Structure**

The project is structured as follows:

```plaintext
.
├── downloaded_images/             # Folder containing images for evaluation.
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── prompts/                       # Folder containing prompt text files (dynamic prompts).
│   ├── Prompt1.txt
│   ├── Prompt2.txt
│   └── ...
├── prompt_templates/              # Folder containing prompt templates with placeholders.
│   ├── template1.txt
│   └── template2.txt
├── guidelines/                    # Folder containing exception rules and safety guidelines.
│   ├── safety_guidelines.json
│   └── exceptions.json
├── results/                       # Folder where the evaluation results are stored.
│   └── metrics_Prompt1.txt
├── Image-downloader.py            # Script for downloading images from URLs.
├── prompt_eval.py                 # Main script for evaluating prompts against the image dataset.
├── prompt_loader.py               # Script for dynamically loading prompts and handling exceptions.
└── Images_Ground_Truth.csv        # CSV file containing the image paths and their ground truth labels.
```

### **Folder Descriptions**:
- **`downloaded_images/`**: This folder contains the images you want to evaluate. Each image should be listed in the `Images_Ground_Truth.csv` file with its path and label (offensive or not_offensive).
  
- **`prompts/`**: This folder contains the prompt files that are dynamically loaded during evaluation. You can create or modify these prompts to meet your specific use cases. Each prompt file will be evaluated against the image dataset.
  
- **`prompt_templates/`**: This folder contains **prompt templates** with placeholders for exceptions or rules. The **Dynamic Prompt Loader** reads these templates and fills them based on guidelines and rules from the `guidelines/` folder.
  
- **`guidelines/`**: This folder contains safety guidelines and exceptions that are dynamically injected into the prompts. Files such as `safety_guidelines.json` define what kind of content is flagged, and `exceptions.json` defines exceptions like "classical art" or "medical content."

- **`results/`**: This folder stores the results of the prompt evaluation, including metrics for each prompt in a text file. These metrics include precision, recall, and F1-scores for how well each prompt detects offensive content.
  
- **`Images_Ground_Truth.csv`**: The CSV file where each row corresponds to an image in the `downloaded_images/` folder and includes its ground truth label (either `offensive` or `not_offensive`). This dataset is used to compare the model's output with the actual label.

---

## **3. How to Run the Scripts**

### **Running the Dynamic Prompt Loader**:
The **prompt_loader.py** script is responsible for dynamically loading prompts and injecting relevant safety rules or exceptions.

To load prompts dynamically, run the following command:
```bash
python3 prompt_loader.py --template_path prompt_templates/ --guidelines_path guidelines/safety_guidelines.json --output_path prompts/
```

This script will:
- Read prompt templates from the `prompt_templates/` folder.
- Load safety rules and exceptions from the `guidelines/` folder.
- Dynamically generate the final prompts and save them into the `prompts/` folder.

### **Running the Prompt Evaluation**:
Once the prompts are loaded, you can evaluate the image dataset using the **prompt_eval.py** script.

```bash
python3 prompt_eval.py --image_dataset ./downloaded_images/Images_Ground_Truth.csv --prompts_folder prompts/ --output results/
```

This will:
- Evaluate each image in `downloaded_images/` using each prompt in the `prompts/` folder.
- For each prompt, the system will calculate **precision**, **recall**, and **F1-score** metrics based on the ground truth labels in the `Images_Ground_Truth.csv` file.
- The evaluation results will be saved into the `results/` folder.

---

## **4. Key Benefits of This Framework**

### **1. Prompt Evaluation**:
- Provides a structured way to compare the efficacy of different prompts for detecting offensive content in product images.
- Automatically calculates key metrics such as **precision**, **recall**, and **F1-score** to help you evaluate the performance of each prompt.

### **2. Dynamic Prompt Loading**:
- Enables the system to adjust prompts dynamically by injecting safety guidelines and exception rules, making it highly flexible and adaptable to evolving requirements.
- Supports easy integration of new rules and guidelines without changing the underlying code.

### **3. Scalable and Maintainable**:
- This framework can scale as more prompts and images are added. It also makes it easy to maintain the system since prompts and rules are stored externally and can be updated independently.

### **4. Versatile Application**:
- You can use this framework not only for offensive content detection but also for other use cases, such as detecting harmful, misleading, or illegal products, depending on how the prompts and guidelines are configured.

---

Let me know if you need any further changes or additions!