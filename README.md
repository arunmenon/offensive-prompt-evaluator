### README: **Prompt Loader and Evaluator System**

This README provides detailed instructions and insights into how to run the **Prompt Loader** and **Prompt Evaluator** tools, along with the key benefits and how they can be leveraged to test and improve the quality of prompts.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Benefits](#key-benefits)
3. [Folder Structure](#folder-structure)
4. [Prompt Loader](#prompt-loader)
    - [How to Use](#how-to-use-prompt-loader)
    - [Command-Line Arguments](#command-line-arguments-for-prompt-loader)
5. [Prompt Evaluator](#prompt-evaluator)
    - [How to Use](#how-to-use-prompt-evaluator)
    - [Command-Line Arguments](#command-line-arguments-for-prompt-evaluator)
6. [Testing Prompt Quality](#testing-prompt-quality)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The **Prompt Loader and Evaluator System** is designed to assist in generating, organizing, and evaluating prompts dynamically, particularly for tasks like catalog content evaluation where specific guidelines and exceptions need to be applied. 

The system consists of two main components:

1. **Prompt Loader**: Dynamically generates prompts using a template and a JSON configuration of exceptions. The generated prompts are saved in a specified folder with numbered filenames.
2. **Prompt Evaluator**: Evaluates the quality and effectiveness of the generated prompts by processing them based on predefined criteria.

---

## Key Benefits

### **1. Prompt Loader**

- **Dynamic and Configurable**: The **Prompt Loader** allows dynamic generation of prompts using **templates** and an **exceptions config** (JSON file). It decouples the logic from specific prompts, making it easy to update templates and configurations.
- **Automated Naming**: The generated prompts are automatically named in sequence (`Prompt1.txt`, `Prompt2.txt`, etc.) in the destination folder, ensuring clean organization.
- **Error Handling**: The loader checks for missing placeholders in the exception config and provides clear error messages when a placeholder is missing from the JSON file, ensuring that your prompts are always complete.

### **2. Prompt Evaluator**

- **Prompt Quality Testing**: The **Prompt Evaluator** is designed to test the effectiveness of the generated prompts. It can be used to assess whether the prompts adhere to guidelines and exceptions, and whether they are actionable for specific tasks like content moderation.
- **Automated Evaluation**: By automatically processing and evaluating all generated prompts in a folder, the evaluator allows for large-scale testing of prompt variations, which can help fine-tune and improve prompt quality.
- **Scalability**: The system is designed to handle multiple prompts at scale, making it ideal for iterative testing and refinement of prompts in scenarios like trust and safety reviews, product categorization, and more.

---

## Folder Structure

This is the suggested folder structure for your project:

```plaintext
.
├── downloaded_images/            # Folder to store downloaded images (if applicable)
├── guidelines/                   # Folder containing JSON config for exceptions
│   └── walmart_exceptions.json
├── prompt_loader.py              # Script for loading prompt templates and generating prompts
├── prompt_templates/             # Folder containing prompt template files
│   └── prompt_template.txt       # Example prompt template file
├── prompts/                      # Folder where generated prompts are saved
│   └── Prompt1.txt               # Example generated prompt
├── prompt_eval.py                # Script for evaluating generated prompts
```

---

## Prompt Loader

### **How to Use Prompt Loader**

The **Prompt Loader** script dynamically generates prompts using a template file and an exceptions config (JSON). The generated prompts are saved in the `prompts/` folder with a numbered filename (`Prompt1.txt`, `Prompt2.txt`, etc.).

### **Command-Line Arguments for Prompt Loader**

You need to pass the following arguments when running the script:

1. **`--exceptions`**: Path to the **exceptions JSON file** (e.g., `guidelines/walmart_exceptions.json`).
2. **`--template`**: Path to the **prompt template file** (e.g., `prompt_templates/prompt_template.txt`).
3. **`--destination`**: Folder where the generated prompts will be saved (e.g., `prompts/`).

**Command Example**:

```bash
python prompt_loader.py --exceptions guidelines/walmart_exceptions.json --template prompt_templates/prompt_template.txt --destination prompts/
```

- This command will generate the next available numbered prompt file (e.g., `Prompt3.txt`) and save it in the `prompts/` folder.

---

## Prompt Evaluator

### **How to Use Prompt Evaluator**

The **Prompt Evaluator** script is designed to evaluate the generated prompts. It reads the prompts from the designated folder and processes them to perform evaluations, such as checking for specific criteria in a catalog system.

### **Command-Line Arguments for Prompt Evaluator**

The following arguments are expected for the **Prompt Evaluator** script:

1. **`--prompts_folder`**: Path to the folder containing the generated prompts (e.g., `prompts/`).
2. **`--output`**: Path to the output folder where evaluation results will be saved (e.g., `output/`).

**Command Example**:

```bash
python prompt_eval.py --prompts_folder prompts/ --output output/
```

- This command will evaluate all the generated prompts from the `prompts/` folder and save the evaluation results in the `output/` folder.

---

## Testing Prompt Quality

### **Why Test Prompt Quality?**

Testing prompt quality is essential to ensure that the generated prompts are effective, actionable, and adhere to guidelines such as Trust & Safety (T&S) rules. By testing prompts iteratively, you can:
- Identify areas where prompts may be ambiguous or unclear.
- Ensure that prompts are correctly applying the exception rules from the JSON config.
- Fine-tune prompt wording to improve accuracy in identifying flagged content or adhering to product moderation guidelines.

### **Steps to Test Prompt Quality**

1. **Generate Multiple Prompts**: Use the **Prompt Loader** to generate a range of prompts using different templates and exception configurations. These prompts will be saved in the `prompts/` folder with sequential numbering.

2. **Evaluate Prompts**: Run the **Prompt Evaluator** to assess the generated prompts. The evaluation process will check the prompts against specific criteria (e.g., Trust & Safety guidelines, content moderation rules).

3. **Analyze Results**: The output from the evaluator will help you analyze how well each prompt performs. By comparing the results, you can identify:
   - **Precision**: How accurately the prompt captures the intended content.
   - **Recall**: How many relevant cases the prompt identifies correctly.
   - **False Positives/Negatives**: Instances where the prompt may have flagged content incorrectly or missed relevant content.

4. **Iterate on Improvements**: Based on the evaluation results, adjust your prompt templates and exceptions config. Re-run the **Prompt Loader** to generate new prompts, and repeat the evaluation cycle to continuously improve prompt quality.

---

## Examples

### Example 1: **Generating Prompts**

Assume you have a template (`prompt_template.txt`) and an exceptions config file (`walmart_exceptions.json`). To generate a prompt, run the following command:

```bash
python prompt_loader.py --exceptions guidelines/walmart_exceptions.json --template prompt_templates/prompt_template.txt --destination prompts/
```

If `Prompt1.txt` and `Prompt2.txt` already exist in the `prompts/` folder, this command will generate `Prompt3.txt`.

### Example 2: **Evaluating Generated Prompts**

After generating prompts, you can evaluate them using the **Prompt Evaluator** script:

```bash
python prompt_eval.py --prompts_folder prompts/ --output output/
```

This will process all the prompt files in the `prompts/` folder and save the evaluation results in the `output/` folder.

---

## Troubleshooting

### 1. **File Not Found Errors**

If you receive an error like:
```plaintext
Error: The prompt template file 'prompt_templates/prompt_template.txt' was not found.
```
- Ensure that the file paths provided for `--exceptions` and `--template` are correct.
- Verify that the files exist in the specified locations.

### 2. **Missing Placeholders in Exceptions Config**

If a placeholder in the template cannot be found in the exceptions config, you will see an error like:
```plaintext
Error: Placeholder 'placeholder_name' not found in exceptions config. Unable to generate prompt.
```
- Ensure that the placeholder in the template matches a key in the exceptions config.
- Check your `walmart_exceptions.json` to ensure all necessary keys are present.

### 3. **Empty Prompts Folder**

If no prompts are generated or evaluated, ensure that:
- The `prompts/` folder is correctly specified.
- The prompt loader script is correctly generating numbered files.

---

## Summary

- **Prompt Loader**: Dynamically generates prompts based on templates and exception configs.
- **Prompt Evaluator**: Evaluates the generated prompts for specific criteria.
- Use the **command-line arguments** to specify paths for templates, exceptions, and destination/output folders.
- Ensure that the **file paths are correct** and the placeholders in the templates match the keys in the exceptions config.

By leveraging these tools, you can **iteratively test prompt quality**, ensuring that your prompts are both effective and aligned with specific task requirements, such as Trust & Safety guidelines or product moderation standards.

For any issues, refer to the **Troubleshooting** section.

