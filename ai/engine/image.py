from ultralytics import YOLO
import cv2

model = YOLO('models/potholeV2.pt')

def analyze_image(image_path, output_path = 'output.jpg', conf = 0.25):
    image = cv2.imread(image_path)
    h, w = image.shape[0:2]
    image_area = h * w

    results = model.predict(
        source = image,
        conf = conf,
        save = False,
        verbose = False
    )

    boxes = results[0].boxes
    pothole_count = 0
    pothole_area = 0
    severity_score = 0

    if boxes is not None:
        pothole_count = len(boxes)
        for box in boxes.xyxy:
            x1, y1, x2, y2 = box.cpu().numpy()
            box_area =(x2 - x1) * (y2 - y1)
            
            box_center_y = (y1 + y2) / 2
            distance_weight = 1 + (1 - box_center_y / h)
            weight_area = box_area * distance_weight
            pothole_area += weight_area

            cv2.rectangle(
                image,
                (int(x1), int(y1)),
                (int(x2),int(y2)),
                (0, 0, 255),
                2
            )
            label = "Pothole"
            x = int(x1)
            y = int(y1)-10 if int(y1) - 10 > 10 else int(y1) + 10
            cv2.putText(
                image,
                label,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                1,
                cv2.LINE_AA)

    ratio = pothole_area / image_area

    pothole_count_normalize = min(pothole_count / 10, 1.0)
    severity_score = (ratio * 50 + pothole_count_normalize * 50)
    severity_score = int(min(severity_score, 100))
    cv2.imwrite(output_path, image)

    return {
        'Pothole Count': pothole_count,
        'Severity Score': severity_score,
        'Output Image Path': output_path
    }
        

if __name__ == "__main__":
    result = analyze_image('test_samples/4.jpg', 'output.jpg', conf=0.25)
    print(result)