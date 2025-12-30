import sys
from engine.image_engine import analyze_image
from engine.video_engine import analyze_video


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <input_type> <input> <output_path>")
        sys.exit(1)

    input_type = sys.argv[1]
    input = sys.argv[2]
    output_path = sys.argv[3]

    if input_type == "image":
        analyze_image(input, output_path=output_path, conf_road=0.2, conf_pothole=0.2)
    if input_type == "video":
        analyze_video(input)
    else:
        print("Invalid input type. Use 'image' or 'video'.")
        sys.exit(1)