import cv2
from ultralytics import YOLO
import time

pothole_model = YOLO('models/pothole.pt')
road_model = YOLO('models/road.pt')

def analyze_video(video_path):
    print(f"Processing video: {video_path}")
    print("Loading models...")

    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return -1, -1

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    
    if fps > 0:
        duration = total_frames / fps
    else:
        duration = 0
        
    print(f"Video Duration: {duration:.2f} seconds")
    
    if duration > 10:
        print("Error: Video duration exceeds 10 seconds limit.")
        cap.release()
        return -1, -1

    print(f"total frames to process: {total_frames}")

    line_position = 0.65 
    confidence = 0.2      
    road_check_interval = 30 

    previous_positions = {}
    counted_ids = []
    total_score = 0
    frame_count = 0
    current_road_width = 1000 
    
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        height, width, _ = frame.shape
        cy_line = int(height * line_position)
        
        if frame_count % road_check_interval == 0 or frame_count == 1:
            road_results = road_model.predict(frame, conf=0.25, verbose=False)
            largest_width = 0
            if road_results[0].boxes:
                for box in road_results[0].boxes.xyxy.cpu().numpy():
                    rx1, ry1, rx2, ry2 = box
                    r_w = rx2 - rx1
                    if r_w > largest_width:
                        largest_width = r_w
                if largest_width > 0:
                    current_road_width = largest_width

        results = pothole_model.track(frame, persist=True, conf=confidence, 
                                      tracker="bytetrack.yaml", imgsz=1280, verbose=False)
        result = results[0]

        if result.boxes is not None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.cpu().numpy()
            track_ids = result.boxes.id.int().cpu().tolist()
            
            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box            
                w = x2 - x1
                cy = int((y1 + y2) / 2)
                
                if track_id in previous_positions:
                    prev_cy = previous_positions[track_id]
                    if prev_cy < cy_line and cy >= cy_line:
                        if track_id not in counted_ids:
                            counted_ids.append(track_id)
                            
                            severity_ratio = w / current_road_width
                            points = 0
                            if severity_ratio < 0.15:
                                points = 2 
                            elif severity_ratio < 0.30:
                                points = 5 
                            else:
                                points = 15

                            total_score += points
                            print(f" -> Detect: ID {track_id} | Ratio: {severity_ratio:.2f} | Pts: {points}")
                            
                previous_positions[track_id] = cy

        if frame_count % 100 == 0:
            print(f"Processed {frame_count}/{total_frames} frames")

    cap.release()
    
    end_time = time.time()
    print(f"\nProcessing Complete in {end_time - start_time:.2f} secss")
    
    return {
        'Pothole Count': len(counted_ids),
        'Severity Score': total_score}