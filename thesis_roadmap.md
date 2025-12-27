# 🎓 Thesis Roadmap: "Burmese CNER 18" Implementation

**Goal:** Create an 18-class semantic tagger for Myanmar using Knowledge Distillation.
**Timeline:** 12-14 Weeks.

## Phase 0: Setup & Definitions (Week 1)

- [X] **Repo Setup**
  - [X] Initialize `beyond_proper_nouns_myanmar_cner` repo.
  - [X] Create `src/prompts.py`: Define the 18 classes clearly in Python strings for the API prompt.
- [X] **Data Sourcing**
  - [X] Acquire ~50k raw Myanmar sentences (mix of News, Wiki, Legal text if possible).
  - [X] Clean text (remove non-Burmese noise).

## Phase 1: The Teacher & Synthetic Data (Weeks 2-5)

- [X] **Prompt Engineering (Critical)**
  - [X] Design **Few-Shot Prompt**: Create 3-5 perfect examples showing how to tag complex cases (e.g., distinguishing `LOC` vs `ARTIFACT`).
  - [X] Test on 50 diverse sentences. Verify Gemini understands "Role" vs "Person".**Mass Generation**

- - [ ] Run `generator.py` in batches.
  - [ ] **Validation Step**: Write a script to check JSON validity and discard hallucinations/malformed outputs.
  - [ ] Target: 40k - 50k valid annotated sentences.

## Phase 2: Processing & Stratification (Weeks 6-7)

- [ ] **Token Alignment**
  - [ ] Develop `converter.py`: Map character indices (from Gemini) to `myanberta` tokens.
  - [ ] Handle "Script Continua" issues (mismatches between tokenizer and logic).
- [ ] **Handling Imbalance**
  - [ ] **Statistics**: Count occurrences of every tag (e.g., `PER`: 10,000, `DISEASE`: 200).
  - [ ] **Stratified Split**: Use `sklearn.model_selection.train_test_split` with stratification to ensure the Validation set gets rare tags.
  - [ ] **Weight Calculation**: Compute inverse class weights for the Loss Function.

## Phase 3: The Student Training (Weeks 8-10)

- [ ] **Environment**
  - [ ] Setup Colab with T4 GPU.
  - [ ] Load `josh-ng/myanberta`.
- [ ] **Training Loop**
  - [ ] Implement `CustomTrainer` class to accept `class_weights`.
  - [ ] Train: 3-5 Epochs, Batch Size 16/32, FP16 enabled.
  - [ ] Monitor: Watch 'Validation Loss' and 'F1-Macro'. If Validation Loss goes up, stop (Overfitting).
- [ ] **Baseline Comparison**
  - [ ] Train `bert-base-multilingual-cased` (mBERT) or `XLM-R` on the same data for comparison.

## Phase 4: Evaluation & Thesis Writing (Weeks 11-14)

- [ ] **Gold Standard Creation**
  - [ ] **Manual Annotation**: Hand-label 200 *new* sentences (not seen by Gemini) to act as the absolute truth.
- [ ] **Scoring**
  - [ ] Run Student Model on the Gold Set.
  - [ ] Calculate `seqeval` metrics (Precision/Recall/F1).
- [ ] **Visual Analysis (For the Deck)**
  - [ ] Generate **Confusion Matrix** (Heatmap).
  - [ ] Analyze specific errors (e.g., "Why did it confuse `LAW` with `THEORY`?").
- [ ] **Final Deliverables**
  - [ ] Push Model to Hugging Face Hub.
  - [ ] Finalize Thesis Paper & Slide Deck.
