import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import glob

# --- Configuration ---
FOLDER_PATH = os.path.dirname(__file__)  # Folder where this script lives
FONT_SIZE = 36      # Extra Large
TEXT_COLOR = "blue"
CSV_KEY_COL = 0    # Assuming key is in first column
CELL_LOCATION = (2, 1) # Excel B3 is row 3, col 2 (0-indexed: row 2, col 1)

def get_value_from_csv(csv_path):
    """Reads cell B3 (row 2, col 1) from a CSV file."""
    try:
        # Assuming no header, reading the specific row/col
        df = pd.read_csv(csv_path, header=None)
        return df.iloc[CELL_LOCATION[0], CELL_LOCATION[1]]
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return None

def process_images():
    # Find all JPG files (case-insensitive by checking common extensions)
    jpg_files = glob.glob(os.path.join(FOLDER_PATH, "*.jpg")) + glob.glob(os.path.join(FOLDER_PATH, "*.JPG"))
    
    for img_path in jpg_files:
        filename = os.path.basename(img_path)
        
        # Extract 13 characters after "SL_"
        if "SL_" not in filename:
            print(f"Skipping {filename}: No 'SL_' found.")
            continue
        key = filename.split("SL_")[1][:13]

        # Find corresponding CSV
        corresponding_csv = glob.glob(os.path.join(FOLDER_PATH, f"*{key}*.csv"))
        
        if not corresponding_csv:
            print(f"No CSV found for {filename} (key: {key})")
            continue
            
        csv_path = corresponding_csv[0]
        value = get_value_from_csv(csv_path)
        
        if value is None:
            continue

        # Add text to image
        try:
            img = Image.open(img_path)
            draw = ImageDraw.Draw(img)
            
            # Try a system truetype font, otherwise fall back to default.
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", FONT_SIZE)
            except Exception:
                try:
                    font = ImageFont.truetype("Arial.ttf", FONT_SIZE)
                except Exception:
                    font = ImageFont.load_default()
            
            text = f"% BLUE = {value}"
            
            # Position: Upper right corner (roughly)
            # Adjust (x,y) based on image size
            width, height = img.size
            position = (width - 380, 20) 
            
            draw.text(position, text, fill=TEXT_COLOR, font=font)
            
            # Save or Overwrite
            img.save(img_path)
            print(f"Updated {filename} with value {value}")
            
        except Exception as e:
            print(f"Error processing image {filename}: {e}")

if __name__ == "__main__":
    process_images()