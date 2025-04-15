# Algerian History Educational Dataset

## Dataset Overview

This dataset contains educational resources about Algerian history, organized to support learning at various educational stages, including primary school, junior school, high school, and university levels. The data is structured to help students and educators explore Algerian history across different eras and topics, providing insights from prehistoric times to the modern era.

## Data Format

The dataset is structured in JSON format, with each record following this template:

```json
{
  "EducationalStage": "JS1",
  "HistoricalEra": "العصور ما قبل التاريخ",
  "Topic": "دراسة الآثار واستعمال القطع الأثرية",
  "Content": "Description of the topic's content goes here...",
  "Source": "Original",
  "Level": 1
}
```

### EducationalStage
Indicates the educational stage the content is intended for. It includes values like:
- **PS**: Primary School
- **JS**: Junior School
- **HS**: High School - General
- **HSS**: High School - Scientific
- **HSL**: High School - Literature
- **UNI**: University

### HistoricalEra
Represents the era in Algerian history the content pertains to. Possible values include:
- **Prehistoric Era** (العصور ما قبل التاريخ)
- **Ancient Era** (العصر القديم)
- **Byzantine Era** (العصر البيزنطي)
- **Islamic Era** (العصر الإسلامي)
- **Ottoman Era** (العصر العثماني)
- **Colonial Era** (عصر الاستعمار)
- **War of Independence** (حرب الاستقلال)
- **Post-Independence Era** (فترة ما بعد الاستقلال)
- **Modern Era** (العصر الحديث)

### Topic
A brief title or description of the main subject covered in the content. This can be the title of a document or the central topic addressed.

### Content
The main text or description related to the topic. This section includes educational explanations or narratives relevant to the specified historical era and topic.

### Source
Indicates the origin of the content. If marked as **Original**, it means the content was created from academic sources. Other values may include references to specific texts or authors.

### Level
Specifies the order or sequence of the content within the educational curriculum. A lower level number (e.g., `1`) indicates content that should be introduced earlier, with higher numbers representing content that should be taught later.


