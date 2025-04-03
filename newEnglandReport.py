
from anthropic import Anthropic
import os
from PIL import Image as PILImage
import base64
from dotenv import load_dotenv
import pdfplumber
import pdf2image
import io
import cv2
import numpy as np
import pytesseract


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class NewEnglandReport:

    def initiate_anthropic(self):
        load_dotenv()
        print(os.environ.get("ANTHROPIC_API_KEY"))
        self.anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        

    def find_pages_with_text(self, search_text):
        matching_pages = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if search_text in text:
                    matching_pages.append(i)
        return matching_pages

    def pdf_page_to_base64(self, pdf_path, page_num):
        images = pdf2image.convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        if images:
            img = images[0]
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return img_str
        return None

    def prepare_image(self):
        search_text = "Daily natural gas consumption by sector"
        matching_pages = self.find_pages_with_text(search_text)
        if not matching_pages:
            print(f"No pages found containing '{search_text}'")
            return
        
        print(matching_pages)
        page_num = matching_pages[0]
        image_str = self.pdf_page_to_base64(self.pdf_path, page_num)

        if image_str:
            # print("we found an image string")
            image_data = base64.b64decode(image_str)
            nparr = np.frombuffer(image_data, np.uint8)
            img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img_cv2
        return None
    


    def cropChart(self, img_cv2):        
            img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
            data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)

            target_title = "Daily natural gas consumption by sector"
            title_box = {}
            found_title = False

            legend_str = "residential/commercial"
            legend_box = {}
            found_legend = False

            for i, word in enumerate(data["text"]):
                if i > len(data["text"]) - 7:
                    continue

                test_phrase = " ".join(data["text"][i:i+6])

                if target_title.lower() in test_phrase.lower():
                    title_box["left"] = min([x for x in data["left"][i:i+6]])
                    title_box["top"] = min([y for y in data["top"][i:i+6]])
                    title_box["width"] = max([x+w for x, w in zip(data["left"][i:i+6], data["width"][i:i+6])]) - title_box["left"]
                    title_box["height"] = max([y+h for y, h in zip(data["top"][i:i+6], data["height"][i:i+6])]) - title_box["top"]
                    found_title = True
                    # print("found title", title_box)

                if legend_str in data["text"][i]:
                    legend_box["left"] = data["left"][i]
                    legend_box["top"] = data["top"][i]
                    legend_box["width"] = data["width"][i]
                    legend_box["height"] = data["height"][i]
                    found_legend = True
                    # print("found legend", legend_box)
              
            if(not (found_title and found_legend)):
                print("Could not find title and legend")
                return None
            
            chart_box = {}
            chart_box["left"] = title_box["left"] - 20
            chart_box["top"] = title_box["top"]
            chart_box["width"] = (int) ((legend_box["left"] + legend_box["width"] - chart_box["left"])*(7/6))
            chart_box["height"] = (int) (legend_box["top"] - (legend_box["height"] * 1.5) - title_box["top"])
            # print(chart_box)

            cropped_img_cv2 = img_cv2[chart_box["top"]:chart_box["top"]+chart_box["height"], chart_box["left"]:chart_box["left"]+chart_box["width"]]
            cropped_img_rgb = cv2.cvtColor(cropped_img_cv2, cv2.COLOR_BGR2RGB)

            data2 = pytesseract.image_to_data(cropped_img_rgb, output_type=pytesseract.Output.DICT)
            target_subtitle = "billion cubic feet"
            subtitle_box = {}
            
            crop2_top = 0
            for i, word in enumerate(data2["text"]):
                #print(word, data2["left"][i], data2["top"][i])
                if i > len(data2["text"]) - 4:
                    continue

                test_phrase = " ".join(data2["text"][i:i+3])
                if target_subtitle.lower() in test_phrase.lower():
                    # print("found the subtitle")
                    subtitle_box["left"] = min([x for x in data2["left"][i:i+3]])
                    subtitle_box["top"] = min([y for y in data2["top"][i:i+3]])
                    subtitle_box["width"] = max([x+w for x, w in zip(data2["left"][i:i+3], data["width"][i:i+3])]) - subtitle_box["left"]
                    subtitle_box["height"] = max([y+h for y, h in zip(data2["top"][i:i+3], data["height"][i:i+3])]) - subtitle_box["top"]
                    # print(subtitle_box)
                    crop2_top = subtitle_box["top"] + subtitle_box["height"]
            
            graph_only_img_cv2 = cropped_img_cv2[crop2_top:, :]
            cv2.imshow("cropped", graph_only_img_cv2)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return graph_only_img_cv2
    
    def findChartDimensions(self, img_cv2):    
        img_height = img_cv2.shape[0]
        img_width = img_cv2.shape[1]
        
        # preproccessing
        rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
            )
        
        # Step 1: Edge detection        
        edges = cv2.Canny(thresh, 30, 100, apertureSize=5)
        
        # Step 2: Hough Line Transform to find lines
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

        horizontal_lines = []
        vertical_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                # Step 3A: filter for only the horizontal lines that are at least 1/2 the length of the image
                if (abs(y2 - y1) < 5) and (abs(x2 - x1) > (img_width/2)):  # Horizontal line (tolerance for small angle)
                    horizontal_lines.append({"left": x1, "right": x2, "ypos": (y1+y2)/2})

                # Step 3B: filter for only the vertical lines that are at least 1/4 the height of the image
                elif (abs(x2 - x1) < 5 and (abs(y2 - y1) > (img_height/4))):  # Vertical line (tolerance for angle)
                    vertical_lines.append({"top": y1, "bottom": y2, "xpos": (x1+x2)/2})

        sorted_horizontal = sorted(horizontal_lines, key = lambda line: line["ypos"])

        filtered_horizontal = []
        line_just_added = None
        for line in sorted_horizontal:
            if line_just_added is None:  # if this is the first line, add it.
                filtered_horizontal.append(line)
                line_just_added = line
            elif line["ypos"] - line_just_added["ypos"] > 6:   # otherwise only add it if it is distinct from the previous line added.
                filtered_horizontal.append(line)
                line_just_added = line

        top_horizontal_line = 2*img_height # start below bottom of chart and replace if higher
        bottom_horizontal_line = -1 # start above top of chart and replace if lower

        for i, fl in enumerate(filtered_horizontal):
            if fl["ypos"] < top_horizontal_line:
                top_horizontal_line = fl["ypos"]
            if fl["ypos"] > bottom_horizontal_line:
                bottom_horizontal_line = fl["ypos"]

        print(f"Top gridline {top_horizontal_line}.  X-axis {bottom_horizontal_line}")

        sorted_vertical = sorted(vertical_lines, key = lambda line: line["xpos"])
        for i, vl in enumerate(sorted_vertical):
            print(f"vertical line {i}: {vl}")
            

        left_band_img = img_cv2[:, :filtered_horizontal[0]["left"]]
        left_band_gray = cv2.cvtColor(left_band_img, cv2.COLOR_BGR2GRAY)
        left_band_thresh = cv2.adaptiveThreshold(left_band_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 11, 2)
        custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789.'
        y_label_candidates = pytesseract.image_to_data(left_band_thresh, config=custom_config, output_type=pytesseract.Output.DICT)
        
        y_labels = []
        y_labels_pos = []

        for word, ypos in zip(y_label_candidates["text"], y_label_candidates["top"]):
            if(is_number(word)):
                y_labels.append(float(word))
                y_labels_pos.append(ypos)
        print(f"Max y yabel is {max(y_labels), min(y_labels_pos)}, Min is {min(y_labels), max(y_labels_pos)}")
        
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.initiate_anthropic()
        img_cv2 = self.prepare_image()
        if img_cv2 is not None:
            cropped_img_cv2 = self.cropChart(img_cv2)
            self.findChartDimensions(cropped_img_cv2)

if __name__ == "__main__":
    report = NewEnglandReport("./new_england_natgas/20250101_new_england_dashboard.pdf")
    report = NewEnglandReport("./new_england_natgas/20241227_new_england_dashboard.pdf")
    report = NewEnglandReport("./new_england_natgas/20240905_new_england_dashboard.pdf")
    report = NewEnglandReport("./new_england_natgas/20240802_new_england_dashboard.pdf")

