# Capstone Project — Mamaearth Returns & Growth Intelligence Pipeline

## About the Project

This project is based on Mamaearth sales data. The main aim is to study the sales data, find useful patterns, and understand what the numbers tell us about the business.

I have used SQL for database operations and reports, Python for data cleaning and exploratory data analysis, and visualizations to make the results easier to understand. In the final part, I used Gemini to turn the main findings into a business summary using the Situation, Complication, and Resolution (SCR) format.

The project is divided into three main parts:
- SQL analysis
- Python analysis and Visualization
- Narrative generation

## Project Structure

The repository contains the following folders and files:

- `SQL/` contains SQL scripts which are used to create tables, load data, and generate reports.
- `analysis/` contains the Python scripts for data cleaning, EDA, and visualization.
- `data/` contains the customer, order, and product CSV files.
- `narrator/` contains the findings JSON file and the script used to generate the final narrative.
- `visualizations/` stores the visual outputs created during the analysis.

## Requirements

Before running the project, make sure you have:

- A python library to run these codes, I have used Google Colab
- A MySQL-compatible environment for running the SQL scripts, I have used MySQL Workbench
- A Gemini API key if you want to use Gemini for generating the narrative. The key is optional because the script also supports an offline fallback.

## Part 1: SQL Analysis

The first part focuses on setting up the database and running SQL reports. The files are located in the `SQL/` folder.

Run the SQL files in the following order:

1. **`SQL/schema.sql`** — creates the database tables and their structure.
2. **`SQL/seed_data.sql`** — inserts the initial data into the tables.
3. **`SQL/reports.sql`** — runs the SQL reports on the loaded data.

It is important to run these files in the correct order because the data must be loaded into the tables before the reports can be executed.

## Part 2: Data Cleaning, EDA and Visualization

After completing the SQL part, move to the Python analysis.

The input data is available in the `data/` folder:

- `customers.csv`
- `orders.csv`
- `products.csv`

Run the Python scripts in this order:

1. **`analysis/clean_and_eda.py`** — cleans the data and performs exploratory data analysis (EDA). This helps identify issues in the data and understand the main sales patterns.
2. **`analysis/visualize.py`** — creates visualizations to make the findings easier to read and compare.

The visual outputs are stored in the `visualizations/` folder.

### Generating the Findings

As part of Part 2, Task 5, generate `narrator/findings.json`. This file contains the important numerical findings from the analysis.

The findings file is used in Part 3, so make sure it has been generated before running the narrative-generation script.

## Part 3: SCR Narrative Generation

The final part uses the findings from the previous stage to create a business summary.

Run **`narrator/generate_narrative.py`** after `narrator/findings.json` is ready. The script uses the findings to generate a narrative in three sections:

- **Situation:** explains the current business situation based on the results.
- **Complication:** describes the important issues or patterns found in the analysis.
- **Resolution:** gives recommendations based on the findings.

### Setting Up the Gemini API Key

To generate the narrative using Gemini, set your API key as an environment variable named `GEMINI_API_KEY` before running the script.

### Running Without an API Key

A Gemini API key is not required to run the offline fallback. If the key is unavailable or Gemini generation fails, the script can generate the narrative using its offline method.

The generated narrative is saved to:

`narrator/sample_output.txt`

## Complete Run Order

To run the project from the beginning, follow these steps in order:

1. Run `SQL/schema.sql` to create the tables.
2. Run `SQL/seed_data.sql` to load the data.
3. Run `SQL/reports.sql` to generate the SQL reports.
4. Run `analysis/clean_and_eda.py` to clean and analyze the data.
5. Run `analysis/visualize.py` to create the visualizations.
6. Complete Part 2, Task 5 to generate `narrator/findings.json`.
7. Set `GEMINI_API_KEY` if you want to use Gemini.
8. Run `narrator/generate_narrative.py` to generate the final SCR narrative.
9. Check `narrator/sample_output.txt` for the generated result.

Make sure each stage is completed before moving to the next one, as later stages depend on the outputs created earlier.

## Final Output

At the end of the pipeline, the project produces SQL reports, Python analysis results, visualizations, a JSON file containing the main findings, and a final SCR business narrative.

The purpose of the complete pipeline is to go from the original sales data to useful findings and then turn those findings into a readable business summary.
This completes the full project pipeline.
