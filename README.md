# EEG/ECG Multichannel Data Explorer

A powerful Python tool for **visualizing and exploring EEG/ECG multichannel CSV data** with interactive plots. Using Plotly and Dash to provide seamless pan, zoom, and selection capabilities for multichannel data analysis.

---

## Table of Contents
- [Requirements](#requirements)
- [Usage](#usage)
- [Design Notes](#design-notes)
- [Features](#features)
- [Future Work](#future-work)
- [GIF](#gif)

---
## Requirements

This project requires **Python 3.7+** and the following packages:

- **Create a venv environment and source it**
    ```bash
    python3 -m venv myvenv 
    ```
    ```bash
    source myvenv/bin/activate
    ```
- **Install Plotly and Dash**
    ```bash
    pip install plotly pandas numpy dash
    ```
## Usage
### CSV Format
The tool expects CSV files with:
- Metadata header lines starting with `#`
- A header line starting with `Time,` followed by channel names
- Time values in first column, signal amplitudes in μV in subsequent columns.

### How to Run
```bash
python3 eeg_plotter.py 'EEG and ECG data_02_raw.csv'
```
**This will:**

- Parse the CSV file, automatically detecting the Time column and channels.
- Generate an interactive multichannel EEG/ECG plot
- Launch a Dash web app in the browser

## Design Notes
- **Channel Categorization:** Channel are automatically categorized as:
    - **EEG:** μV signals
    - **ECG:** mV signals
    - **Reference:** μV

- **Scalling:** Each channel is allocated 150 pixels regardless of signal amplitude. Plotly automatically: 
    - Scales each subplot's y-axis to fit data range
    - Maintains visual clarity regardless of whether signals are in  μV or mV range
    - Handles zoom and pan operations seamlessly accross different scales

- **AI Assistance:** Claude was used to help understand ***Plotly*** and ***Dash***, design plotting logic, and improve multichannel layout for readability and usability.

## Features
- Interactive Plotly/Dash visualization for multiple channels
- Proper scaling for EEG/ECG/Reference VS Time
- Linked x-axes for synchronized zooming across channels
- Each x-axes with Time indicators and grids
- Click and drag to move around with panning
- Selectable time windows for amplitude inspection
- Reset axes
- Download plot as PNG image

## Future Work
- Implement dynamic y-axis scaling based on user selection
- Add sticky buttons (pan, zoom, selection) at top of interface
- Include normalization toggles for signal comparison
- Highlight selected rectangles with background color
- Enhanced display of selected time ranges and amplitudes
- Export functionality for selected data segments

## GIF
![Alt text](recording-eeg-ecg.gif)
