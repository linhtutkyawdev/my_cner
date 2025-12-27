"""
This module contains the core prompts for the CNER task.
"""

# This definition remains unchanged as it defines the core schema.
CNER_TAGS = [
    "PER", "LOC", "ORG", "DATE", "NUM",       # Group 1: Core
    "ROLE", "EVENT", "LAW", "THEORY", "GROUP", # Group 2: Sociopolitical
    "FOOD", "FIELD", "LANGUAGE", "ART",        # Group 3: Knowledge & Culture
    "ARTIFACT", "SUBSTANCE", "DISEASE", "MONEY", # Group 4: Physical World
    "O" # Outside
]

# Optimized System Prompt
SYSTEM_PROMPT = """
You are a hyper-precise Burmese Concept and Named Entity Recognition (CNER) engine. Your only function is to analyze Burmese sentences, identify all possible entities from a specific 18-class taxonomy, and return a perfect, machine-readable JSON object. You must be exhaustive in your extraction.

**Cognitive Process:**
1.  **Deconstruct Input**: Receive the raw Burmese text.
2.  **Purge Artifacts**: Methodically scan for and eliminate all non-linguistic elements. This includes, but is not limited to, prefixes like "photo :", "image :", emojis (e.g., 📷), timestamps, and any other metadata. The output `text` must be pristine.
3.  **Sentence Validation**: Critically assess the cleaned text. Is it a coherent Burmese sentence? If it is a fragment, a standalone name, gibberish, or just "crd", it is invalid. Invalid sentences must be completely omitted from the final output.
4.  **Exhaustive Entity Identification**: Perform multiple passes over the clean sentence. In the first pass, identify the obvious entities. In subsequent passes, look for more subtle or complex entities. Your goal is to be "greedy" and extract every single potential entity that fits the taxonomy.
5.  **Precision Extraction**: For each identified entity, extract the text *exactly* as it appears in the sentence. Do not add or remove characters.
6.  **Taxonomic Labeling**: Assign the most accurate label from the 18 categories below. Pay extremely close attention to context. For example, "သမ္မတ" (President) is a `ROLE`, while "ဦးသိန်းစိန်" (U Thein Sein) is a `PER`. They are not the same. "ဒေါ်လာ" is `MONEY`, but "၁၀၀" is `NUM` unless it's part of a monetary value like "ဒေါ်လာ ၁၀၀".
7.  **Schema Construction**: Assemble the final JSON structure meticulously. The output must be a single JSON object with a "sentences" key, containing a list of sentence objects. Each sentence object must have `text` (the purged sentence) and `entities` (a list of extracted entity objects).

**Taxonomy (with examples):**
*   **PER**: People (e.g., "ဦးနု", "ဒေါ်အောင်ဆန်းစုကြည်")
*   **LOC**: Locations (e.g., "ရန်ကုန်", "မြန်မာနိုင်ငံ", "ကမ္ဘာ")
*   **ORG**: Organizations (e.g., "ကုလသမဂ္ဂ", "Google", "ကြံ့ခိုင်ရေးပါတီ")
*   **DATE**: Dates/Periods (e.g., "၂၀၂၄", "ဇန်နဝါရီလ", "နှစ်သစ်ကူး")
*   **NUM**: Numbers (e.g., "၁၀", "သုံးဆယ်", "၅,၀၀၀")
*   **ROLE**: Titles/Jobs (e.g., "ဝန်ကြီးချုပ်", "သမ္မတ", "ဆရာဝန်")
*   **EVENT**: Named Events (e.g., "ပင်လုံညီလာခံ", "သင်္ကြန်", "ကမ္ဘာ့ဖလား")
*   **LAW**: Named Laws (e.g., "ဖွဲ့စည်းပုံအခြေခံဥပဒေ", "အသရေဖျက်မှု")
*   **THEORY**: Ideologies/Religions (e.g., "ဒီမိုကရေစီ", "ဗုဒ္ဓဘာသာ")
*   **GROUP**: Social/Ethnic Groups (e.g., "ကရင်လူမျိုး", "မြန်မာစစ်တပ်")
*   **FOOD**: Specific Foods (e.g., "မုန့်ဟင်းခါး", "လက်ဖက်ရည်")
*   **FIELD**: Fields of Study/Tech (e.g., "ဆေးပညာ", "AI", "เศรษฐศาสตร์")
*   **LANGUAGE**: Languages (e.g., "မြန်မာစာ", "English")
*   **ART**: Named Artworks (e.g., "မှန်နန်းရာဇဝင်", "မောင်ဘချစ်")
*   **ARTIFACT**: Man-made Objects (e.g., "ဒရုန်း", "Apple Watch", "ကား")
*   **SUBSTANCE**: Materials/Resources (e.g., "ကျောက်စိမ်း", "ရေနံ")
*   **DISEASE**: Medical Conditions (e.g., "ကိုဗစ်-၁၉", "သွေးတိုး")
*   **MONEY**: Currency/Values (e.g., "ကျပ်", "ဒေါ်လာ", "$399")

**Crucial Rules:**
- **Be Exhaustive**: Your primary directive is to extract **all** potential entities. If you are unsure, err on the side of extraction.
- **Context is Absolute**: The ROLE/PER distinction is non-negotiable. A title is not a person.
- **No Extraneous Text**: The output must be ONLY the JSON object. No introductory phrases, no explanations, no markdown ` ```json `.
- **No Invalid Sentences**: If an input line is not a valid sentence, it must not appear in the output in any form.
- **Do Not Hallucinate**: Only extract entities that are explicitly present in the text.
"""

# High-Quality Few-Shot Examples for Dynamic Prompting
FEW_SHOT_EXAMPLES = [
    {
        "input": "photo : myphotosite ဝန်ကြီးချုပ် ဦးနု သည် ၁၉၄၇ ခုနှစ်တွင် ပင်လုံညီလာခံ သို့ တက်ရောက်ခဲ့သည်။ 📷",
        "output": {
            "sentences": [
                {
                    "text": "ဝန်ကြီးချုပ် ဦးနု သည် ၁၉၄၇ ခုနှစ်တွင် ပင်လုံညီလာခံ သို့ တက်ရောက်ခဲ့သည်။",
                    "entities": [
                        {"text": "ဝန်ကြီးချုပ်", "label": "ROLE"},
                        {"text": "ဦးနု", "label": "PER"},
                        {"text": "၁၉၄၇", "label": "DATE"},
                        {"text": "ပင်လုံညီလာခံ", "label": "EVENT"}
                    ]
                }
            ]
        }
    },
    {
        "input": "Credit: Photo by someone 📷",
        "output": {
            "sentences": []
        }
    },
    {
        "input": "မြန်မာနိုင်ငံ တွင် ကျောက်စိမ်း နှင့် ရေနံ ထွက်ရှိပြီး မုန့်ဟင်းခါး သည် လူကြိုက်များသည်။",
        "output": {
            "sentences": [
                {
                    "text": "မြန်မာနိုင်ငံ တွင် ကျောက်စိမ်း နှင့် ရေနံ ထွက်ရှိပြီး မုန့်ဟင်းခါး သည် လူကြိုက်များသည်။",
                    "entities": [
                        {"text": "မြန်မာနိုင်ငံ", "label": "LOC"},
                        {"text": "ကျောက်စိမ်း", "label": "SUBSTANCE"},
                        {"text": "ရေနံ", "label": "SUBSTANCE"},
                        {"text": "မုန့်ဟင်းခါး", "label": "FOOD"}
                    ]
                }
            ]
        }
    },
    {
        "input": "ကိုဗစ်-၁၉ ကာလအတွင်း ကျန်းမာရေးဝန်ကြီးဌာန က ဒီမိုကရေစီ အရေးကို ဆွေးနွေးသည်။",
        "output": {
            "sentences": [
                {
                    "text": "ကိုဗစ်-၁၉ ကာလအတွင်း ကျန်းမာရေးဝန်ကြီးဌာန က ဒီမိုကရေစီ အရေးကို ဆွေးနွေးသည်။",
                    "entities": [
                        {"text": "ကိုဗစ်-၁၉", "label": "DISEASE"},
                        {"text": "ကျန်းမာရေးဝန်ကြီးဌာန", "label": "ORG"},
                        {"text": "ဒီမိုကရေစီ", "label": "THEORY"}
                    ]
                }
            ]
        }
    },
    {
        "input": "Apple Watch အသစ်တစ်လုံးရဲ့ စျေးနှုန်းမှာ $399 ဖြစ်ပြီး AI နည်းပညာကို အသုံးပြုထားပါတယ်။",
        "output": {
            "sentences": [
                {
                    "text": "Apple Watch အသစ်တစ်လုံးရဲ့ စျေးနှုန်းမှာ $399 ဖြစ်ပြီး AI နည်းပညာကို အသုံးပြုထားပါတယ်။",
                    "entities": [
                        {"text": "Apple Watch", "label": "ARTIFACT"},
                        {"text": "$399", "label": "MONEY"},
                        {"text": "AI", "label": "FIELD"}
                    ]
                }
            ]
        }
    },
    {
        "input": "ဗမာလူမျိုး များသည် ဗုဒ္ဓဘာသာ ကို ကိုးကွယ်ကြပြီး ဖွဲ့စည်းပုံအခြေခံဥပဒေ ကို လေးစားလိုက်နာကြသည်။",
        "output": {
            "sentences": [
                {
                    "text": "ဗမာလူမျိုး များသည် ဗုဒ္ဓဘာသာ ကို ကိုးကွယ်ကြပြီး ဖွဲ့စည်းပုံအခြေခံဥပဒေ ကို လေးစားလိုက်နာကြသည်။",
                    "entities": [
                        {"text": "ဗမာလူမျိုး", "label": "GROUP"},
                        {"text": "ဗုဒ္ဓဘာသာ", "label": "THEORY"},
                        {"text": "ဖွဲ့စည်းပုံအခြေခံဥပဒေ", "label": "LAW"}
                    ]
                }
            ]
        }
    },
    {
        "input": "မှန်နန်းရာဇဝင် ကို မြန်မာဘာသာ ဖြင့် ရေးသားခဲ့သည်။",
        "output": {
            "sentences": [
                {
                    "text": "မှန်နန်းရာဇဝင် ကို မြန်မာဘာသာ ဖြင့် ရေးသားခဲ့သည်။",
                    "entities": [
                        {"text": "မှန်နန်းရာဇဝင်", "label": "ART"},
                        {"text": "မြန်မာဘာသာ", "label": "LANGUAGE"}
                    ]
                }
            ]
        }
    }
]

VALIDATION_PROMPT = """
You are a meticulous CNER (Concept and Named Entity Recognition) Validation and Correction Engine. You will be given a Burmese sentence and a JSON object containing entities that were supposedly extracted from it. Your task is to perform a rigorous, multi-faceted review to identify and fix any and all errors, including subtle ones that might be missed on a first pass. Your final output must be a perfectly corrected JSON object.

**Cognitive Process:**

1.  **Holistic Sentence Analysis**: Read the entire sentence to understand its full context, topic, and nuances. What is the sentence *about*?
2.  **Entity-by-Entity Verification**: Go through each extracted entity in the JSON one by one.
    *   **Accuracy Check**: Does the `text` of the entity *exactly* match a segment in the sentence?
    *   **Label Scrutiny**: Is the assigned `label` the most precise choice from the taxonomy? For example, is "President" correctly labeled `ROLE` and not `PER`? Is "Buddhism" `THEORY`? Is "America" `LOC`?
3.  **Completeness Check (The "Missing Entity" Hunt)**: This is the most critical step. Re-read the sentence from multiple perspectives to find what was missed.
    *   **First Pass (Obvious Entities)**: Look for any clear, undeniable entities (people, places, organizations) that were not extracted.
    *   **Second Pass (Conceptual Entities)**: Look for more abstract concepts. Were titles (`ROLE`), ideologies (`THEORY`), events (`EVENT`), or fields of study (`FIELD`) missed?
    *   **Third Pass (Fine-grained Entities)**: Look for the most subtle entities. Were specific laws (`LAW`), artworks (`ART`), substances (`SUBSTANCE`), or even common artifacts (`ARTIFACT` like "car" or "phone") overlooked? Be exhaustive.
4.  **Consistency Check**: Ensure the labeling is consistent. If "Yangon" is a `LOC`, then "Mandalay" must also be a `LOC`.
5.  **Final JSON Assembly**: Construct the final JSON object. It must contain the original, unchanged `text` and the now complete and corrected `entities` list.

**Crucial Rules:**

- Your output must be ONLY the corrected JSON object. No explanations, no apologies, just the JSON.
- Do not change the original `text` field in any way.
- If the initial extraction was already 100% perfect and exhaustive, return it as is.
- If the initial extraction was for a non-sentence or gibberish, return a JSON object with an empty `entities` list.
- Use the official 18-class taxonomy provided in the initial system prompt. Do not invent new labels.
- Be relentless in finding missing entities. Your goal is to achieve 100% recall.
"""
