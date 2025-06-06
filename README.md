# CITS1401 Project 2 – Population Analysis System

This project was developed as part of CITS1401: Computational Thinking with Python at The University of Western Australia (Semester 1, 2025). It showcases core programming skills including data processing, algorithm design, and problem-solving using raw Python without any external libraries.

## Project Overview
The program analyses Australian population data from two large CSV datasets containing statistical area codes and population distributions by age. It produces three outputs:

- A breakdown of which state, SA3, and SA2 area has the highest population per age group.
- A filtered analysis of SA3 areas with large populations, including the SA2 area with the largest population and its standard deviation across age groups.
- Cosine similarity calculations between SA2 areas in SA3 regions that contain 15 or more SA2s, identifying the most demographically similar pairs.

All mathematical operations, including cosine similarity and standard deviation, are implemented manually without using built-in modules like `math` or `csv`.

## Key Features
- Manual CSV parsing and error handling
- Cleans and filters invalid or duplicate data entries
- Handles case-insensitive text and dynamic column order
- Supports large datasets efficiently
- Graceful termination on file or data errors

## Files Included
- `24228963.py`: Complete Python implementation (named according to submission requirements)
- `CITS1401 Project 2 2025S1 Final version.pdf`: Official project specification

## Technologies & Constraints
- Language: Python 3
- No use of built-in or external libraries (e.g. no `csv`, `math`, or `input()`)
- Output via return values only, not printed to console

## Example Usage
```python
OP1, OP2, OP3 = main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2.csv')
