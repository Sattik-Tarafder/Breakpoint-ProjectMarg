import cv2
import numpy as np
from ultralytics import YOLO

def analyze_video(video_path):
    model = YOLO('potholeV2.pt') 
    # video = 'testtt.mp4'  #eta uncomment korte paris jodi front end er sathe connect korar age dry run korte chas
    cap = cv2.VideoCapture(video_path)

    line_position = 0.65  #checker line positon eta thke change korte paris(in percentage)
    confidence = 0.1     
    small_thresh = 3000
    medium_thresh = 9000
    previous_positions = {}
    counted_ids = []
    total_score = 0
    severity_status = "good"
    status_color = (0, 255, 0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        height, width, _ = frame.shape
        cy_line = int(height * line_position)
        results = model.track(frame, persist=True, conf=confidence, tracker="bytetrack.yaml", verbose=False)
        result = results[0]
        cv2.line(frame, (0, cy_line), (width, cy_line), (0, 255, 255), 2)
        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            track_ids = result.boxes.id.int().cpu().tolist()
            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box            
                w = x2 - x1
                h = y2 - y1
                area = w * h
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(frame, str(int(area)), (int(x1), int(y1) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                if track_id in previous_positions:
                    prev_cy = previous_positions[track_id]
                    if prev_cy < cy_line and cy >= cy_line:
                        if track_id not in counted_ids:
                            counted_ids.append(track_id)
                            points = 0
                            if area < small_thresh:
                                points = 2   #small potholee
                            elif area < medium_thresh:
                                points = 5   # medium pothloe
                            else:
                                points = 15  #Big pothole
                            total_score += points
                            print(f"pothole detected id: {track_id}, size: {area}, points: {points}")
                            cv2.line(frame, (0, cy_line), (width, cy_line), (0, 255, 0), 5)
                previous_positions[track_id] = cy

        if total_score < 20:
            severity_status = "good condition"
            status_color = (0, 255, 0)
        elif total_score < 60:
            severity_status = "avg condition"
            status_color = (0, 255, 255)
        elif total_score <90:
            severity_status = "bad condition"
            status_color = (0, 165, 255)
        else:
            severity_status = "Very CRITICAL cpndition"
            status_color = (0, 0, 255)

        cv2.rectangle(frame, (0, 0), (400, 150), (0, 0, 0), -1)
        cv2.putText(frame, f"Total Potholes: {len(counted_ids)}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"damage score: {total_score}", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"live status: {severity_status}", (20, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 3)
        cv2.imshow('potholedetection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

    return len(counted_ids), total_score #return vals for fornt end niggas

if __name__ == "__main__":
    count, score = analyze_video('testtt.mp4')
    print(f"final Count: {count}, final score: {score}")