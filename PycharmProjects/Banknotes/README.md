# Banknote Detection Project

This project is designed to detect and classify Hungarian banknotes (HUF) in real-time or from static images using Microsoft's Azure Custom Vision.

## Features

- Real-time detection using webcam.
- Image-based detection from paths or URLs.
- Highlights detected banknotes with bounding boxes and probabilities.

## Prerequisites

1. Python 3.8 or higher.
2. Required Python libraries:
   - `opencv-python`
   - `requests`
   - `numpy`
   - `pygrabber`
3. Azure Custom Vision training and prediction endpoints.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/USERNAME/banknote-detection.git
   cd banknote-detection
