
# Energy Data Fetcher

## Overview

The Energy Data Fetcher is a web application designed to fetch, transform, and display electricity load data for various areas. The application uses a Flask backend to handle data extraction and transformation, and a React frontend to display the results.

## Features

- Fetch electricity load data for specified areas and time ranges.
- Display fetched data in a user-friendly interface.
- View newly inserted data.
- Restart the backend server if needed.

## Technologies Used

- **Backend:** Flask, MySQL
- **Frontend:** React, Axios, React Spinners
- **Database:** MySQL

## Project Structure

```
energy-data-fetcher/
├── backend/
│   ├── app.py
│   └── ...
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── ...
│   ├── package.json
│   └── ...
├── README.md
└── ...
```

## Getting Started

### Prerequisites

- Node.js
- Python 3.x
- MySQL

### Setup Instructions

#### Backend

1. **Navigate to the backend directory:**
   ```sh
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required Python packages:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Configure MySQL Database:**
   - Create a MySQL database.
   - Update the database configuration in `app.py` if necessary.

5. **Run the Flask application:**
   ```sh
   flask run --port 5001
   ```

#### Frontend

1. **Navigate to the frontend directory:**
   ```sh
   cd frontend
   ```

2. **Install the required Node.js packages:**
   ```sh
   npm install
   ```

3. **Run the React application:**
   ```sh
   npm start
   ```

## Usage

### Fetch Area Types and Codes

1. Open the application in your browser.
2. Click the "Fetch Area Types & Codes" button.
3. Select an area type and enter the number of days for data fetch.
4. Click the "Fetch Data" button to retrieve the data.

### View Data

- Newly inserted data will be displayed in a table format.
- If no new data is inserted, a message will be shown.

### Restart Backend

- Click the "Restart Backend" button to restart the Flask server if needed.

## Troubleshooting

### Common Issues

- **Database Connection Errors:** Ensure MySQL is running and the database configuration in `app.py` is correct.
- **CORS Issues:** Make sure the Flask-CORS library is properly installed and configured.

### Logs

- Check the backend logs in the terminal where the Flask app is running.
- Check the frontend console for any errors or warnings.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Open a pull request.


## Contact

If you have any questions or suggestions, feel free to reach out to the project maintainer at [cetinefe.ano@gmail.com].
