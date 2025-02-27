# Business Idea Scorer

An AI-driven scoring system that allows investors, venture studios, and accelerators to analyze and rank business ideas based on custom criteria.

## 🔹 Key Features

- Upload business ideas via Excel/CSV
- Analyze and rank ideas based on customizable criteria
- Use GPT API to generate reasoning for each score
- Handle missing data and standardize inputs automatically
- Flag investment risks (public customers, network effects, regulatory barriers, etc.)
- Provide a dashboard for filtering and exporting ranked ideas

## 📌 Core Functionalities

1. Data Ingestion & Cleaning (Excel/CSV Handling)
2. Scoring Logic & Weighting System
3. GPT API for Detailed Reasoning Behind Scores
4. Risk Factor Analysis
5. Interactive Dashboard

## 🛠️ Tech Stack

- **Backend**: Python (FastAPI), Scikit-learn, NLTK, pandas, NumPy, OpenAI GPT API
- **Frontend**: React/Next.js, Plotly/D3.js
- **Infrastructure**: AWS/GCP/Azure, Docker, PostgreSQL

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker (optional for containerized deployment)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Oreoluwa1993/business-idea-scorer.git
   cd business-idea-scorer
   ```

2. Set up the Python environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend
   ```bash
   cd frontend
   npm install
   ```

4. Set environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key and other configuration
   ```

5. Start the backend server
   ```bash
   cd ../backend
   uvicorn main:app --reload
   ```

6. Start the frontend development server
   ```bash
   cd ../frontend
   npm run dev
   ```

7. Open your browser and navigate to http://localhost:3000

## 📊 Project Structure

```
business-idea-scorer/
├── backend/                # Python FastAPI backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   ├── main.py            # Application entry point
│   └── requirements.txt   # Python dependencies
├── frontend/              # React/Next.js frontend
│   ├── components/        # React components
│   ├── pages/             # Next.js pages
│   ├── public/            # Static assets
│   ├── styles/            # CSS styles
│   └── package.json       # Node.js dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
├── docker-compose.yml     # Docker Compose configuration
└── README.md              # Project documentation
```

## 🔄 User Flow

1. Upload Business Ideas (Excel/CSV)
2. Data Cleansing & Standardization
3. Scoring Algorithm Applies ML Model
4. GPT API Generates Detailed Insights
5. Risk Analysis Flags Potential Issues
6. Investor Dashboard Displays Ranked Startups
7. Export to CSV for External Review

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
