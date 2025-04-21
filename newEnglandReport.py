import math
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
import pandas as pd
import pytesseract
from datetime import datetime, timedelta    
import requests


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class NewEnglandReport:

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

    def findPageWithChart(self):
        search_text = "Daily natural gas consumption by sector"
        matching_pages = self.find_pages_with_text(search_text)
        if not matching_pages:
            print(f"No pages found containing '{search_text}'")
            return
        
        #print(matching_pages)
        page_num = matching_pages[0]
        image_str = self.pdf_page_to_base64(self.pdf_path, page_num)

        if image_str:
            # print("we found an image string")
            image_data = base64.b64decode(image_str)
            nparr = np.frombuffer(image_data, np.uint8)
            img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img_cv2
        return None
    
    # this function finds the "Daily Natural Gas Consumption by Sector" in the image of the full page, and returns it
    def findNaturalGasChart(self, img_cv2):        
        img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)

        target_title = "Daily natural gas consumption by sector"
        title_box = {}
        found_title = False

        legend_str = "commercial"
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

            if legend_str in data["text"][i]:
                legend_box["left"] = data["left"][i]
                legend_box["top"] = data["top"][i]
                legend_box["width"] = data["width"][i]
                legend_box["height"] = data["height"][i]
                found_legend = True
                # print("found legend", legend_box)
              
        if(not (found_title and found_legend)):
            print(f"Found title? {found_title} Found legend? {found_legend}")
            return None
            
        chart_box = {}
        chart_box["left"] = title_box["left"] - 20
        chart_box["top"] = title_box["top"]
        chart_box["width"] = int(((legend_box["left"] + legend_box["width"] - chart_box["left"])*(7/6)))
        chart_box["height"] = int((legend_box["top"] - (legend_box["height"] * 1.5) - title_box["top"]))
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
                subtitle_box["left"] = min([x for x in data2["left"][i:i+3]])
                subtitle_box["top"] = min([y for y in data2["top"][i:i+3]])
                subtitle_box["width"] = max([x+w for x, w in zip(data2["left"][i:i+3], data2["width"][i:i+3])]) - subtitle_box["left"]
                subtitle_box["height"] = max([y+h for y, h in zip(data2["top"][i:i+3], data2["height"][i:i+3])]) - subtitle_box["top"]
                # print(subtitle_box)
                crop2_top = subtitle_box["top"] + subtitle_box["height"]
            
        graph_only_img_cv2 = cropped_img_cv2[crop2_top:, :]
        #cv2.imshow("cropped", graph_only_img_cv2)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        return graph_only_img_cv2


    def findYAxisScale(self, left_band_img, distance_top_to_bottom):
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
        # print(f"Max y yabel is {max(y_labels), min(y_labels_pos)}, Min is {min(y_labels), max(y_labels_pos)}")

        if len(y_labels) == 0:
            print("No y-axis labels found")
            for word, ypos in zip(y_label_candidates["text"], y_label_candidates["top"]):
                print(f"{word}, {ypos}")
            return None

        y_axis_scale = (1.0 * distance_top_to_bottom) / (max(y_labels) - min(y_labels))
        # print(f"y_axis_scale {y_axis_scale} pixels per bcf")

        return y_axis_scale

    def validateXaxis(self, bottom_band_img, left_vertical, right_vertical):
        bottom_band_gray = cv2.cvtColor(bottom_band_img, cv2.COLOR_BGR2GRAY)
       # bottom_band_thresh = cv2.adaptiveThreshold(bottom_band_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        _, bottom_band_thresh = cv2.threshold(bottom_band_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        custom_config = r'--psm 11 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        x_label_candidates = pytesseract.image_to_data(bottom_band_thresh, config=custom_config, output_type=pytesseract.Output.DICT)
        
        x_labels = []
        x_labels_left = []
        x_labels_right = []

        
        #cv2.imshow("edges", bottom_band_thresh)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        # print("x axis labels found:")
        for word, left, width in zip(x_label_candidates["text"], x_label_candidates["left"], x_label_candidates["width"]):
         
            if len(word)>2:
                x_labels.append(word)
                x_labels_left.append(left)
                x_labels_right.append(left+width)
                # print(f"{word}, {left}, {left+width}")
        #print("left-right bounds")
        #print(f"left vertical {left_vertical}, right vertical {right_vertical}")

        left_within_bounds = x_labels_left[0] <= left_vertical <= x_labels_right[0]
        right_within_bounds = x_labels_left[-1] <= right_vertical <= x_labels_right[-1]

        if not (left_within_bounds ^ right_within_bounds):
            print("Bad x-axis labels")
            return False

        
        label_center_span = 0.5 * (x_labels_left[-1] + x_labels_right[-1]) - 0.5 * (x_labels_left[0] + x_labels_right[0])
        day_span = label_center_span / 12.0

        x_axis_span = right_vertical - left_vertical
        ratio = (1.0 * x_axis_span) / day_span
        #print(f"label_center_span {label_center_span}, day_span {day_span}, x_axis_span {x_axis_span}, ratio {ratio}")
        #print(ratio)
        if 12.5 < ratio < 13.5:
            # print(f"X axis OK: ratio {ratio} (should be ~13)")
            return True
        else: 
            print(f"X axis BAD: ratio {ratio} (should be ~13)")
            return False


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
        top_horizontal_line = sorted_horizontal[0]["ypos"]
        bottom_horizontal_line = sorted_horizontal[-1]["ypos"]

        # if we have detected two sides of the same edge, take the midpoint
        if(len(sorted_horizontal) > 1):
            if sorted_horizontal[1]["ypos"] - sorted_horizontal[0]["ypos"] < 6:
                top_horizontal_line = 0.5 * (sorted_horizontal[0]["ypos"] + sorted_horizontal[1]["ypos"])
            if sorted_horizontal[-1]["ypos"] - sorted_horizontal[-2]["ypos"] < 6:
                bottom_horizontal_line = 0.5 * (sorted_horizontal[-1]["ypos"] + sorted_horizontal[-2]["ypos"])

        # make sure that we don't crop vertically from rounding
        top_horizontal_line = int(math.floor(top_horizontal_line))
        bottom_horizontal_line = int(math.ceil(bottom_horizontal_line))

        #print(f"Top gridline {top_horizontal_line}.  X-axis {bottom_horizontal_line}")
        
        left_band_img = img_cv2[:, :sorted_horizontal[0]["left"]]
        y_axis_scale = self.findYAxisScale(left_band_img, bottom_horizontal_line - top_horizontal_line)
        if y_axis_scale is None: 
            return None

        sorted_vertical = sorted(vertical_lines, key = lambda line: line["xpos"])
        left_vertical_line = sorted_vertical[0]["xpos"]
        right_vertical_line = sorted_vertical[-1]["xpos"]
        # if we have detected two sides of the same edge, take the innerermost_edge
        # print(f"Left edge of chart {left_vertical_line}.   Right edge of chart {right_vertical_line}")

        if(len(sorted_vertical) > 1):
            if (sorted_vertical[1]["xpos"] - sorted_vertical[0]["xpos"]) < 6:
                left_vertical_line = (sorted_vertical[1]["xpos"] + sorted_vertical[0]["xpos"])/2
            if (sorted_vertical[-1]["xpos"] - sorted_vertical[-2]["xpos"]) < 6:
                right_vertical_line = (sorted_vertical[-1]["xpos"] + sorted_vertical[-2]["xpos"])/2

        # move the zone of the chart inward by 2 pixels to make sure we are picking up color pixels and not just off edge
        left_vertical_line = left_vertical_line + 1
        right_vertical_line = right_vertical_line - 1

        #print(f"Left edge of chart {left_vertical_line}.   Right edge of chart {right_vertical_line}")

        bottom_band_img = img_cv2[bottom_horizontal_line+8:-25, :]
        valid_days = self.validateXaxis(bottom_band_img, left_vertical_line, right_vertical_line)
        if not valid_days:
            return None

        two_week_span = right_vertical_line - left_vertical_line
        date_locations = [int((round((left_vertical_line + (two_week_span) * (i/13)), 0))) for i in range(14)]
        # print(date_locations)

        color_ranges = {
            'blue': ((40, 150, 170), (90, 200, 255)), 
            'brown': ((180, 120, 70), (220, 160, 120)),    # industrial
            'green': ((80, 140, 80), (140, 200, 140)),  
        }     

        start_date = self.report_date.date() - timedelta(days=13)
        dates = [start_date + timedelta(days=i) for i in range(14)]
        data = []
        for date, xpos in zip(dates, date_locations[:14]):
            counts = {'green': 0, 'brown': 0, 'blue': 0}
            for ypos in range(top_horizontal_line, bottom_horizontal_line):
                pixel = rgb[ypos, xpos]
                # print(pixel)
                for color, (lower, upper) in color_ranges.items():
                    if np.all(np.array(lower) <= pixel) and np.all(pixel <= np.array(upper)):
                        counts[color] += 1
                        # print(f"found {color}")
                        break
            #print(f"Counts for {xpos} are {counts}")
            data.append({"date": date,
                    "electric": round(counts["green"] / y_axis_scale, 2),
                    "industrial": round(counts["brown"] / y_axis_scale + counts["green"] / y_axis_scale,2 ),
                    "resi_comm": round(counts["blue"] / y_axis_scale + counts["brown"] / y_axis_scale + counts["green"] / y_axis_scale, 2),
                })
            
        df = pd.DataFrame(data)
        # print(df)

        if(False):
            top_left = (date_locations[0], top_horizontal_line)       # (x1, y1)
            bottom_right = (date_locations[-1], bottom_horizontal_line)  # (x2, y2)    
            #Draw red rectangle — note: in RGB, red = (255, 0, 0)
            img_box = cv2.rectangle(img_cv2, top_left, bottom_right, color=(255, 0, 0), thickness=1)
            for d in date_locations:
                pt1 = (d, top_horizontal_line)
                pt2 = (d, bottom_horizontal_line)
                cv2.line(img_box, pt1, pt2, color=(0, 255, 0), thickness=1)  
            
            cv2.imshow("img_box", img_box)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return df

    def __init__(self, pdf_path, report_date):
        self.pdf_path = pdf_path
        self.report_date = report_date
        
        img_cv2 = self.findPageWithChart()
        if img_cv2 is not None:
            cropped_img_cv2 = self.findNaturalGasChart(img_cv2)
            if cropped_img_cv2 is not None:
                self.df = self.findChartDimensions(cropped_img_cv2)


def downloadReportIfAbsent(report_date):
    report_date_str = report_date.strftime("%Y%m%d")
    report_year = report_date.strftime("%Y")
    report_month = report_date.strftime("%m")
    pdf_path = f"./new_england_natgas/{report_date_str}_new_england_dashboard.pdf"
    if not os.path.exists(pdf_path):
        url = f"https://www.eia.gov/dashboard/new-england-energy-api/archives/{report_year}{report_month}/{report_date_str}_new_england_dashboard.pdf"
        print(f"Downloading {url} to {pdf_path}")
        response = requests.get(url)
        if response.status_code == 200:
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
                print(f"Download successful {report_date}.")
        else:
            print(f"Download failed {report_date}:", response.status_code)
            print(response)
            return None
    return pdf_path

if __name__ == "__main__":
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 4, 18)
    curr_date = start_date

    raw_bcf_values_electric = {}
    raw_bcf_values_industrial = {}
    raw_bcf_values_resi_comm = {}


    while curr_date <= end_date:
        weekday = curr_date.weekday()
        if (weekday < 5): # it's not a weekend
            path = downloadReportIfAbsent(curr_date)
            if path is None:
                curr_date = curr_date + timedelta(days=1)
                continue

            print(f"accessing date: {curr_date}")
            report = NewEnglandReport(path, curr_date)
            if report.df is not None:
                for row in report.df.itertuples(index = False):
                    # print(row)
                    row_date = row.date
                    if raw_bcf_values_electric.get(row_date) is None: raw_bcf_values_electric[row_date] = []
                    if raw_bcf_values_industrial.get(row_date) is None: raw_bcf_values_industrial[row_date] = []
                    if raw_bcf_values_resi_comm.get(row_date) is None: raw_bcf_values_resi_comm[row_date] = []

                    raw_bcf_values_electric[row_date].append(row.electric)
                    raw_bcf_values_industrial[row_date].append(row.industrial)
                    raw_bcf_values_resi_comm[row_date].append(row.resi_comm)
                # print(report.df)
            else:
                print(f"Failed to extract data for {curr_date}")

        curr_date = curr_date + timedelta(days=1)

    all_data = []
    for date in raw_bcf_values_resi_comm.keys():
        d = {   "date": date, 
                "electric": sum(raw_bcf_values_electric[date])/len(raw_bcf_values_electric[date]),
                "industrial": sum(raw_bcf_values_industrial[date])/len(raw_bcf_values_industrial[date]),
                "resi_comm": sum(raw_bcf_values_resi_comm[date])/len(raw_bcf_values_resi_comm[date])
            }
        all_data.append(d)

    df = pd.DataFrame(all_data)
    print(df)
    df.to_csv("new_england_natgas.csv", index=False)



