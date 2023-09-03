import numpy as np
import cv2
import os
import json

class PnP:
    def __init__(self, imgdir, shapedir):
        self.imgdir = imgdir
        self.shapedir = shapedir

        # load all images in the directory
        self.images = []
        self.read_images(self.imgdir)

        self.get_intrinsic_from_img(self.images[0])

        self.points_3d = {}
        self.read_points_3d(self.shapedir)

        self.points_2d = {}
        self.read_points_2d(self.imgdir)

        self.distortion = np.zeros((4, 1))

    # read all images in a directory
    def read_images(self, path):
        for filename in os.listdir(path):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                img = cv2.imread(os.path.join(path, filename))
                if img is not None:
                    self.images.append(img)

    # read 3d points from shapes folder
    def read_points_3d(self, path):
        for filename in os.listdir(path):
            if filename.endswith('.json'):
                with open(os.path.join(path, filename)) as f:
                    self.points_3d[filename[:-5]] = json.load(f)

    # read (annotated) 2d points from images folder
    def read_points_2d(self, path):
        with open(os.path.join(path, 'annotations.json')) as f:
            self.points_2d = json.load(f)

    # get camera intrisic matrix from an image
    def get_intrinsic_from_img(self, img):
        self.img = img
        self.h, self.w = img.shape[:2]

        # get the intrinsic matrix
        self.intrinsic = np.array([[self.w, 0, self.w / 2],
                                [0, self.w, self.h / 2],
                                [0, 0, 1]], dtype='double')

    def run_single_image(self, idx):
        print("Running PnP for image", idx, "...")

        points_2d = np.array(list(self.points_2d.values())[idx])

        # sort 2d points by their labels
        points_2d = points_2d[points_2d[:, 2].argsort()]

        # get the corresponding 3d points
        points_3d = self.points_3d['cube']
        points_3d = np.array([points_3d[str(int(point[2]))] for point in points_2d])

        points_2d = np.array(points_2d[:, :2], dtype='double')
        points_3d = np.array(points_3d, dtype='float64')

        success, rot, trans = cv2.solvePnP(points_3d, points_2d, self.intrinsic, self.distortion, flags=cv2.SOLVEPNP_SQPNP)

        print(f"success: {success}, rot: {rot}, trans: {trans}")

    # run the PnP algorithm for all images
    def run(self):
        for idx in range(len(self.images)):
            self.run_single_image(idx)


if __name__ == '__main__':
    pnp = PnP('images/', 'shapes/')
    pnp.run()

