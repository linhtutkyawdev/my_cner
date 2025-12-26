# Project Context: High-Granularity CNER for Myanmar (Burmese CNER 18)

## 1. Executive Summary

This project addresses a critical gap in Natural Language Processing (NLP) for the **Myanmar (Burmese)** language by developing a high-granularity **Concept and Named Entity Recognition (CNER)** model. While traditional NER focuses on 3-5 basic entities (Person, Location, Organization), this project introduces the **"Burmese CNER 18"**, a novel taxonomy comprising **18 distinct semantic categories** tailored to Myanmar's socio-political, cultural, and economic context.

To overcome the lack of annotated data, we employ a **Knowledge Distillation** strategy. A "Teacher" LLM (`Google Gemini 2.5 Flash`) will synthetically annotate a raw corpus based on our taxonomy. This "Silver Standard" data is then used to fine-tune a compact "Student" model (`josh-ng/myanberta`), creating a deployable, open-source model capable of complex semantic parsing on consumer hardware (T4 GPU).

## 2. Problem Statement

### 2.1. The Semantic Gap
Standard NER is insufficient for high-level text analysis. Identifying "Aung San" as a `Person` is trivial; identifying "General" as a `ROLE`, "Democracy" as a `THEORY`, or "Jade" as a `SUBSTANCE` is crucial for understanding news, legal documents, and economic reports. Current Myanmar models lack this granularity.

### 2.2. The Resource Barrier
Myanmar is a low-resource language. There is no existing dataset that covers these 18 semantic classes. Manual annotation of a sufficient corpus (50k+ sentences) is prohibitively expensive.

### 2.3. Solution: Knowledge Distillation
We leverage the generalization capabilities of Large Language Models (LLMs) to generate training data. The project proves that a small, domain-specific model (the Student) can learn complex semantic boundaries from a larger, general-purpose model (the Teacher).

## 3. The "Burmese CNER 18" Taxonomy

The model must classify tokens into one of the following 18 categories (plus 'O' for Outside):

### Group 1: The Core Entities (Baseline)
- **`PER`**: People (Proper Nouns). *e.g., U Nu.*
- **`LOC`**: Locations (Geo-political). *e.g., Mandalay.*
- **`ORG`**: Organizations. *e.g., United Nations, KBZ Bank.*
- **`DATE`**: Specific dates or periods. *e.g., 2024, Monday.*
- **`NUM`**: Cardinal/Ordinal numbers. *e.g., 10 million, First.*

### Group 2: Sociopolitical Concepts
- **`ROLE`**: Titles, jobs, social positions. *e.g., Prime Minister, Doctor.*
- **`EVENT`**: Wars, festivals, conferences. *e.g., Thingyan, Panglong Conference.*
- **`LAW`**: Laws, treaties, legal acts. *e.g., Constitution, Penal Code.*
- **`THEORY`**: Ideologies, systems. *e.g., Democracy, Federalism.*
- **`GROUP`**: Ethnicities, social groups (not official orgs). *e.g., Bamar, Karen people.*

### Group 3: Knowledge & Culture
- **`FOOD`**: Dishes, ingredients. *e.g., Mohinga, Tea Leaf Salad.*
- **`FIELD`**: Fields of study/profession. *e.g., Engineering, Medicine.*
- **`LANGUAGE`**: Languages and scripts. *e.g., Burmese, English.*
- **`ART`**: Books, songs, movies, literary works. *e.g., Glass Palace Chronicle.*

### Group 4: The Physical World
- **`ARTIFACT`**: Man-made objects, weapons, vehicles. *e.g., Drone, Pagoda structure.*
- **`SUBSTANCE`**: Natural resources, elements. *e.g., Jade, Oil, Gold.*
- **`DISEASE`**: Medical conditions, viruses. *e.g., Covid-19, Malaria.*
- **`MONEY`**: Currency and monetary value. *e.g., Kyat, US Dollar.*

## 4. Architecture Pipeline

### Phase 1: The Teacher (Data Generation)
- **Input**: Raw text (News/Wikipedia).
- **Model**: `Google Gemini 2.5 Flash` (via API).
- **Method**: Few-Shot Chain-of-Thought (CoT) prompting to enforce the 18-class JSON structure.
- **Output**: JSON files containing spans and labels.

### Phase 2: Processing & Alignment
- **Tokenization**: Aligning JSON character spans to `myanberta` sub-word tokens.
- **Tagging**: Converting to **BIO** (Begin-Inside-Outside) format.
- **Stratification**: Splitting data into Train/Val/Test while ensuring rare classes (e.g., `DISEASE`, `ART`) are represented in all sets.

### Phase 3: The Student (Fine-Tuning)
- **Model**: `josh-ng/myanberta`.
- **Loss Function**: **Weighted Cross-Entropy Loss** to handle class imbalance (giving higher penalty for missing rare tags).
- **Hardware**: Google Colab T4 GPU (Mixed Precision `fp16`).

## 5. Technical Stack

-   **Core**: Python 3.10+
-   **Data Gen**: `google-generativeai` (Gemini API)
-   **Model Training**: `transformers` (Hugging Face), `accelerate`, `torch`
-   **Metrics**: `seqeval` (Strict span matching), `scikit-learn` (Confusion Matrix), `seaborn` (Visualization)
-   **Data Ops**: `pandas`, `datasets`

## 6. Directory Structure

```
/
├── data/
│   ├── raw/                 # Input corpus
│   ├── silver_json/         # Gemini output (Raw JSON)
│   ├── processed_bio/       # HF Dataset format (Tokenized + BIO tags)
│   └── gold_manual/         # The 200-sentence Human Ground Truth
├── src/
│   ├── prompts.py           # System prompts & definitions for CNER 18
│   ├── generator.py         # API handling and batch processing
│   ├── converter.py         # JSON -> BIO alignment & Stratified Split
│   └── train.py             # Trainer script with Weighted Loss
├── notebooks/               # Analysis & Visualization (Confusion Matrix)
├── requirements.txt
└── README.md
```

## 7. Implementation Constraints

-   **Unicode Safety**: Explicit handling of Myanmar Unicode strings.
-   **Class Imbalance**: The code *must* calculate class weights from the training set and pass them to the Trainer.
-   **Rate Limiting**: Generator script must handle API 429 errors gracefully.
-   **Reproducibility**: Set random seeds for stratification to ensure the Test set remains constant.
