import os
import cv2
import requests
import numpy as np
import logging
from pygrabber.dshow_graph import FilterGraph
from urllib.request import urlopen

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API credentials
PREDICTION_KEY = os.getenv("PREDICTION_KEY")
PREDICTION_ENDPOINT = os.getenv("PREDICTION_ENDPOINT")
PROBABILITY_THRESHOLD = 0.9  # Minimum probability for a valid detection

if not PREDICTION_KEY or not PREDICTION_ENDPOINT:
    raise ValueError("Prediction Key or Endpoint not set. Please configure environment variables.")

HEADERS = {
    "Prediction-Key": PREDICTION_KEY,
    "Content-Type": "application/octet-stream",
}


def predict_image(image: bytes) -> dict:
    """
    Sends the image to the Custom Vision API for predictions.
    """
    try:
        response = requests.post(PREDICTION_ENDPOINT, headers=HEADERS, data=image)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch predictions: {e}")
        return {}


def process_detections(frame: np.ndarray, detections: dict) -> np.ndarray:
    """
    Process detections and overlay bounding boxes and labels.
    """
    if not detections or "predictions" not in detections:
        logging.info("No valid objects detected.")
        return frame

    valid_detections = [
        pred for pred in detections["predictions"] if pred["probability"] > PROBABILITY_THRESHOLD
    ]

    for detection in valid_detections:
        tag_name = detection["tagName"]
        probability = detection["probability"]
        bbox = detection["boundingBox"]

        height, width, _ = frame.shape
        left = int(bbox["left"] * width)
        top = int(bbox["top"] * height)
        right = int((bbox["left"] + bbox["width"]) * width)
        bottom = int((bbox["top"] + bbox["height"]) * height)

        # Draw rectangle and label
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        label = f"{tag_name} ({probability * 100:.2f}%)"
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        logging.info(f"Detected: {tag_name} with probability {probability * 100:.2f}%")

    return frame


def list_cameras():
    """
    Lists all available cameras on the system.
    """
    graph = FilterGraph()
    devices = graph.get_input_devices()
    return devices


def real_time_detection():
    """
    Real-time detection with a selected camera.
    """
    devices = list_cameras()
    if not devices:
        logging.error("No cameras found.")
        return

    print("Available Cameras:")
    for i, device in enumerate(devices):
        print(f"{i}: {device}")

    try:
        camera_index = int(input("Select a camera by index: "))
        if camera_index < 0 or camera_index >= len(devices):
            logging.error("Invalid camera index selected.")
            return
    except ValueError:
        logging.error("Invalid input. Please enter a valid number.")
        return

    logging.info(f"Using camera index {camera_index}: {devices[camera_index]}")
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        logging.error("Error: Could not open the selected camera.")
        return

    logging.info("Starting real-time detection...")
    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("Error reading frame.")
            break

        _, img_encoded = cv2.imencode(".jpg", frame)
        detections = predict_image(img_encoded.tobytes())

        frame = process_detections(frame, detections)
        cv2.imshow("Banknote Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def detect_from_path_or_url(input_path: str):
    """
    Detects objects in an image from a local path or URL.
    """
    try:
        if input_path.startswith("http"):
            logging.info(f"Fetching image from URL: {input_path}")
            resp = urlopen(input_path)
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        else:
            logging.info(f"Reading image from path: {input_path}")
            image = cv2.imread(input_path)

        if image is None:
            logging.error("Failed to load image. Please check the path or URL.")
            return

        _, img_encoded = cv2.imencode(".jpg", image)
        detections = predict_image(img_encoded.tobytes())

        result_frame = process_detections(image, detections)
        cv2.imshow("Detection Result", result_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        logging.error(f"Error processing the image: {e}")


if __name__ == "__main__":
    logging.info("Welcome to Banknote Detection!")
    print("Choose an option:")
    print("1. Real-Time Detection")
    print("2. Detect from Image Path/URL")

    choice = input("Enter your choice (1 or 2): ").strip()
    if choice == "1":
        real_time_detection()
    elif choice == "2":
        input_path = input("Enter the image path or URL: ").strip()
        detect_from_path_or_url(input_path)
    else:
        logging.error("Invalid choice. Exiting.")
