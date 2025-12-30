import json
import sys
from engine.image_engine import analyze_image
from engine.video_engine import analyze_video


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <input_type> <inpu_path> <output_path>")
        sys.exit(1)

    input_type = sys.argv[1]
    input_path = sys.argv[2]
    output_path = sys.argv[3]

    if input_type == "image":
        result = analyze_image(input_path, output_path=output_path, conf_road=0.2, conf_pothole=0.2)
    elif input_type == "video":
        result = analyze_video(input_path)
    else:
        print("Invalid input type. Use 'image' or 'video'.")
        sys.exit(1)

    print(json.dumps(result))