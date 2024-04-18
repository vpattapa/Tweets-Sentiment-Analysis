# Twitter Sentiment Analysis Dashboard

This project provides a web-based application for real-time sentiment analysis of tweets associated with specific hashtags. The application fetches tweets, analyzes their sentiment, and visualizes the results using D3.js charts. The backend is built with Flask and uses Selenium for scraping Twitter data, while the frontend leverages D3.js for dynamic data visualization.

## Features

- **Live Tweet Scraping**: Fetches live tweets based on user-inputted hashtags.
- **Sentiment Analysis**: Utilizes NLTK's VADER tool to analyze tweet sentiment.
- **Dynamic Visualization**: Displays sentiment analysis results through interactive D3.js bar charts.
- **Server-Sent Events**: Uses Flask to stream processing updates to the client in real time.

## Prerequisites

Before you can run this application, you will need the following:

- Python 3.8 or higher
- Pip for Python package installation
- PostgreSQL database
- A modern web browser that supports JavaScript and SSE (Server-Sent Events)

## Installation

Follow these steps to set up and run the project:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/vpattapa/Tweets-Sentiment-Analysis.git
   cd Tweets-Sentiment-Analysis
   ```

2. **Set Up a Virtual Environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:

   - Ensure PostgreSQL is installed and running.
   - Create a database and update the connection string in `api.py`.

5. **Environment Variables**:

   - Set environment variables for sensitive credentials (optional but recommended for production).

6. **Run the Application**:
   ```bash
   python api.py
   ```

## Usage

Once the application is running:

- Navigate to `http://localhost:5000` in your web browser.
- Enter a Twitter hashtag to analyze.
- View live updates as tweets are fetched, analyzed, and visualized.

## Contributing

Contributions to this project are welcome! Please consider the following steps:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - vpattapa@asu.edu

---
