from ultralytics import YOLO
import cv2
import numpy as np
from math import sqrt


road_model = YOLO('../models/road.pt')
pothole_model = YOLO('../models/pothole.pt')


def analyze_image(image_path, output_path='output.jpg', conf_road=0.2, conf_pothole=0.2):
    image = cv2.imread(image_path)
    
    AREA_MAX = 0.25
    DENSITY_MAX = 0.00015
    road_results = road_model.predict(
        source=image,
        conf=conf_road,
        save=False,
        verbose=False
    )

    road_area = 0
    

    if road_results[0].masks is not None:
        road_masks = road_results[0].masks.data

        for mask in road_masks:
            mask = mask.cpu().numpy()
            mask = (mask > 0.5).astype(np.uint8)
            road_area += np.sum(mask)


    
    pothole_results = pothole_model.predict(
        source=image,
        conf=conf_pothole,
        save=False,
        verbose=False
    )

    pothole_area = 0
    pothole_count = 0
    

    if pothole_results[0].masks is not None:
        pothole_masks = pothole_results[0].masks.data
        pothole_boxes = pothole_results[0].boxes.xyxy
        pothole_count = len(pothole_masks)

        for mask in pothole_masks:
            mask = mask.cpu().numpy()
            mask = (mask > 0.5).astype(np.uint8)
            pothole_area += np.sum(mask)

        for box in pothole_boxes:
            x1, y1, x2, y2 = box.cpu().numpy().astype(int)

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (0, 0, 255),
                2
            )

            label = "Pothole"

            label_y = y1 - 10 if y1 - 10 > 10 else y1 + 10
            cv2.putText(
                image,
                label,
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )


    if road_area == 0:
        severity_score = 0
    else:
        area_ratio = pothole_area / road_area
        area_score = min(area_ratio / AREA_MAX, 1.0)
        boost = sqrt(area_score)
        pothole_density = pothole_count / road_area
        density_score = min(pothole_density / DENSITY_MAX, 1.0)
        severity_score = int(100 * (0.4 * density_score + 0.6 * boost))

        #cv2.imwrite(output_path, image)
    return {
        'Pothole Count': pothole_count,
        'Severity Score': severity_score
    }

if __name__ == "__main__":
    results = analyze_image("input.jpg")
    print(results)