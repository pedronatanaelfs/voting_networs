# Analysis of Brazil's Chamber of Deputies Data

This repository contains scripts and datasets for analyzing data obtained from the official Open Data API of Brazil's Chamber of Deputies.

## Project Description

This project aims to analyze the influence and behavior of various political groups within Brazil's Chamber of Deputies using data fetched from the official API. The analysis focuses on understanding influential groups in bill approvals, correlations between legislators' popularity and their bill approval rates, alliance patterns among political parties in key votes, and predictions regarding the approval of new bills and alliance behaviors under different scenarios.

## Repository Structure

- `/data`: Contains all datasets collected from the API.
- `/scripts`: Contains Python scripts used to fetch data from the API.
- `README.md`: Provides an overview of the project and instructions on how to use the scripts.

## Setup and Installation

### Prerequisites

- Anaconda (Python 3.10)

### Setting up the Environment

1. **Install Anaconda**: Download and install Anaconda from [Anaconda's website](https://www.anaconda.com/download/), if it's not already installed.
2. **Create an Anaconda Environment**:
   - Open your Anaconda Command Prompt.
   - Create a new environment with Python 3.10 by running:  
     ```
     conda create --name camara-analysis python=3.10
     ```
   - Activate the environment:  
     ```
     conda activate camara-analysis
     ```

3. **Install Dependencies**:
   - Ensure you have a `requirements.txt` file in the repository.
   - Install the required Python packages by running:
     ```
     pip install -r requirements.txt
     ```

## Data Collection

Data is collected using the Open Data API provided by the Chamber of Deputies of Brazil. The script `fetch_data.py` in the `/scripts` directory makes API calls and stores the results in appropriate formats for further analysis.

### Collected Data

- **Deputies**: Details on each deputy, including biographical data.
- **Propositions**: Information on legislative proposals and their outcomes.
- **Votings**: Details of voting sessions, including how each party voted on key issues.
- **Parties**: Information on political parties.
- **Blocs**: Details of parliamentary blocs, which often indicate coalitional politics.

## How to Use

- Navigate to the `/scripts` directory.
- Run `python fetch_data.py` to start the data collection process.
- Check the `/data` directory for the CSV files containing the fetched data.

## Dependencies

- Python 3.10
- Other dependencies listed in `requirements.txt`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Chamber of Deputies of Brazil for maintaining the Open Data API.
- Contributors to the Python packages used in this project.