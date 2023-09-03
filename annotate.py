import cv2
import os
import time
import numpy as np
import json

class Annotator:
    def __init__(self, basedir):
        self.double_click_threshold = 0.2

        self.img = None
        self.curr_idx = 0
        self.clicked_points = []
        self.click_times = []

        self.images = []
        self.anno_dict = {}

        self.basedir = basedir

        self.read_images(basedir)

    def click_event(self, event, x, y, flags, params):
        """Handles mouse click events."""

        # lable point when left double clicked
        if event == cv2.EVENT_LBUTTONDOWN:

            # Save the point coordinates when double clicked
            if len(self.click_times) > 0 and time.time() - self.click_times[-1] < self.double_click_threshold:

                cv2.circle(self.img, (x, y), 7, (255, 255, 255), -1)

                # show prompt
                cv2.putText(self.img, 'Enter number:', (100, 500), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 20)

                cv2.imshow('image', self.img)

                # wait for key number input
                while True:
                    key = cv2.waitKey(1) & 0xFF
                    if key >= ord('0') and key <= ord('9'):
                        n = key - ord('0')
                        if not self.check_repeated_points(n):
                            break
                    # exit when q is pressed
                    elif key == ord('q'):
                        exit()

                self.clicked_points.append([x, y, n])
                self.update_image()

            self.click_times.append(time.time())

        # delete point when right clicked
        elif event == cv2.EVENT_RBUTTONDOWN:
            if len(self.clicked_points) > 0:
                self.clicked_points.pop()
                self.click_times.pop()
                self.update_image()

    # read all images in a directory
    def read_images(self, path):
        for filename in os.listdir(path):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                img = cv2.imread(os.path.join(path, filename))
                if img is not None:
                    self.images.append(img)
                    self.anno_dict[filename] = None

    # check repeated points
    def check_repeated_points(self, n):
        for point in self.clicked_points:
            if point[2] == n:
                return True
        return False

    # update image with self.clicked_points
    def update_image(self):
        self.img = self.images[self.curr_idx].copy()
        cv2.putText(self.img, f'Image {self.curr_idx+1}/{len(self.images)}', (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 20)
        for point in self.clicked_points:
            cv2.circle(self.img, (point[0], point[1]), 10, (255, 255, 255), -1)
            cv2.putText(self.img, str(point[2]), (point[0], point[1]), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 20)
        cv2.imshow('image', self.img)

    # save annotated points to a json file
    def save_annotated_points(self):
        with open(os.path.join(self.basedir, 'annotations.json'), 'w') as f:
            json.dump(self.anno_dict, f)

    # annotate a single image
    def annotate_image(self):
        self.img = self.images[self.curr_idx].copy()
        self.clicked_points = []

        # Set the callback function for mouse click events
        cv2.setMouseCallback('image', self.click_event)

        # Resize the window (change the dimensions as needed)
        cv2.resizeWindow('image', 800, 600)

        # Display the image
        self.update_image()

        # wait for annotation
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                exit()
            elif key == ord('n'):
                print("Next image")
                break

        self.anno_dict[list(self.anno_dict.keys())[self.curr_idx]] = self.clicked_points

    # annotate all images in the directory
    def annotate_all(self):
        # Create a window
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)

        # Annotate each image
        for i, image in enumerate(self.images):
            print(f"Annotating image {i+1}/{len(self.images)}")
            self.curr_idx = i
            self.annotate_image()

        # Save the annotated points to a text file
        self.save_annotated_points()

        cv2.destroyAllWindows()

if __name__ == '__main__':
    annotator = Annotator("images/")
    annotator.annotate_all()