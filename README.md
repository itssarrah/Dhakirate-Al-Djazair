# Dhakirate-Al-Djazair: Reviving Algerian History Education with Large Language Models and Retrieval-Augmented Generation

## Project Overview
Dhakirate-Al-Djazair is an educational platform that leverages state-of-the-art NLP techniques, Retrieval-Augmented Generation, and gamification to enhance the teaching and learning of Algerian history.

## Repository Structure
- **Backend Logic**: Flask application providing API endpoints for the frontend
- **Notebooks and Data**: Educational dataset on Algerian history and analysis notebooks
- **Platform**: React-based frontend for the educational platform
- **Dhakirate-AL-Djazair_Project_Report.pdf**: Comprehensive project documentation

## Installation & Setup

### Frontend (React)
**Note**: The frontend and backend must run together to work properly.

#### Prerequisites
You need to install the latest Node.js and npm:

**On Windows (using Chocolatey):**
```powershell
# Download and install Chocolatey
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"

# Download and install Node.js
choco install nodejs-lts --version="23"

# Verify installation
node -v  # Should print "v23.6.0"
npm -v   # Should print "10.9.2"
```

**On Linux (using NVM):**
```bash
# Download and install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# Close and reopen terminal

# Download and install Node.js
nvm install 23

# Verify installation
node -v  # Should print "v23.6.0"
nvm current  # Should print "v23.6.0"
npm -v   # Should print "10.9.2"
```

#### Setup and Run
```bash
# In the frontend directory
npm install

# If errors occur, try:
npm install --legacy-peer-deps
# or
npm install --force

# Start the application
npm start
# This will run the frontend on localhost:3000
```

### Backend (Flask)
The backend app provides an API for the frontend to consume. It represents the most refined version of the code, with enhancements to the chatbot, RAG implementation, and quiz generation.

**Note**: Running this app will download approximately 3GB of data (SentenceTransformers package and RAG model from Huggingface).

#### Setup and Run
```bash
# In the project directory
pip install -r requirements.txt

# Run the application
python run.py
# or
python3 run.py
# or
py run.py
```

## Data Description
The project uses a structured educational dataset on Algerian history, organized by educational stage and historical era.

### Data Format
The dataset is in JSON format with records structured as:
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

### Fields Description
- **EducationalStage**: Intended educational level (PS, JS, HS, HSS, HSL, UNI)
- **HistoricalEra**: Historical period in Algerian history
- **Topic**: Main subject title or description
- **Content**: Educational text or narratives
- **Source**: Origin of the content
- **Level**: Sequential order within curriculum

## Project Results

The Dhakirate-Al-Djazair project demonstrates the potential of combining NLP techniques with RAG and gamification to overcome challenges in teaching Algerian history:

### Key Findings:
- **Embedding Models**: The Alibaba-NLP/gte-multilingual-base model performed best in retrieving contextually relevant content
- **Retrieval Methods**: BM25 outperformed TF-IDF, especially with lemmatized content
- **Learning Features**: Gamified quizzes successfully engaged users, while the RAG-powered chatbot provided accurate, contextually appropriate responses

For more detailed information about methodologies, technical implementation, and comprehensive results, please refer to the full project report (Dhakirate-AL-Djazair_Project_Report.pdf).
