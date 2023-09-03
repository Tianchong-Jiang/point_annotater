import cv2
import os
import time
import numpy as np

class Annotator:
    def __init__(self):
        self.clicked_points = []
        self.click_times = []
        self.double_click_threshold = 0.2

    def click_event(self, event, x, y, flags, params):
        """Handles mouse click events."""

        # lable point when left double clicked
        if event == cv2.EVENT_LBUTTONDOWN:

            # Save the point coordinates when double clicked
            if len(self.click_times) > 0 and time.time() - self.click_times[-1] < self.double_click_threshold:

                self.update_image()

                cv2.circle(self.img, (x, y), 7, (255, 255, 255), -1)

                # show prompt
                cv2.putText(self.img, 'Enter number:', (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 10)

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

    # check repeated points
    def check_repeated_points(self, n):
        for point in self.clicked_points:
            if point[2] == n:
                return True
        return False

    # update image with self.clicked_points
    def update_image(self):
        self.img = self.orig_img.copy()
        for point in self.clicked_points:
            cv2.circle(self.img, (point[0], point[1]), 7, (255, 255, 255), -1)
            cv2.putText(self.img, str(point[2]), (point[0], point[1]), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 10)
        cv2.imshow('image', self.img)

    def save_annotated_points(self, image_path, points):
        """Saves the annotated points to a text file."""
        annotation_file_path = os.path.splitext(image_path)[0] + '_annotations.txt'
        with open(annotation_file_path, 'w') as f:
            for point in points:
                f.write(f"{point[0]}, {point[1]}, {point[2]}\n")

    def run(self, image_path):
        global img
        # Read the image
        self.orig_img = cv2.imread(image_path)
        self.img = self.orig_img.copy()

        # Create a window
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)

        # Set the callback function for mouse click events
        cv2.setMouseCallback('image', self.click_event)

        # Resize the window (change the dimensions as needed)
        cv2.resizeWindow('image', 800, 600)

        # Display the image
        cv2.imshow('image', self.img)

        # Wait for q key to exit
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        # Save the annotated points to a text file
        self.save_annotated_points(image_path, self.clicked_points)

        # Destroy all windows
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # Replace 'image.jpg' with the path to the image you want to annotate.
    image_path = 'image.jpg'
    annotator = Annotator()
    annotator.run(image_path)