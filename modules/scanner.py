# -*- coding: utf-8 -*-

"""
scanner | cell-scan | 3/06/18
<ENTER DESCRIPTION HERE>
"""
import os
from typing import List
import numpy as np
import cv2

from modules.ai.equalizer import Equalizer
from modules.ai.prediction import Prediction
from modules.data.slide import Slide
from tools.util.logger import Logger

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Scanner:
    def __init__(self, output_path: str):
        self.output_path: str = output_path
        from modules.ai.cell_net import CellNet

        self.equalizer = Equalizer()
        self.net = CellNet("cell_model")

    def process(self, slides: List[Slide]):
        """ Predict the results, and create a report for each scan. """
        for slide in slides:
            self._process_slide(slide)

    def _process_slide(self, slide: Slide):
        slide_path = os.path.join(self.output_path, slide.name)
        os.mkdir(slide_path)

        # Draw the slide image.
        image = slide.image
        image_path = os.path.join(slide_path, "image.png")
        Logger.log_special("Scanning {}".format(slide.name), with_gap=True)

        # Predict the cell masks from an image.
        predict_image = image
        if True:
            equalizer_image = self.equalizer.create_equalized_image(image)
            predict_image = equalizer_image

        # Get the sample prediction.
        prediction = self.net.cycle_predict(predict_image, None)
        self._process_prediction(image, slide_path, prediction)
        self._draw_prediction_mask(image, slide_path, prediction)
        cv2.imwrite(image_path, equalizer_image)

    def _process_prediction(self, image, path, prediction: Prediction):

        # Extract an image of each cell.
        n = 0
        for unit in prediction.units:
            r = unit.region
            n += 1
            ex_image = image[r.top:r.bottom, r.left:r.right]
            full_path = os.path.join(path, "cell_{}.png".format(n))
            cv2.imwrite(full_path, ex_image)

    def _draw_prediction_mask(self, image, path: str, prediction: Prediction):
        # For each prediction I also want to draw a mask.
        mask = np.zeros_like(image, dtype=np.uint8)

        for unit in prediction.units:
            r = unit.region
            cv2.rectangle(mask, (r.left, r.top), (r.right, r.bottom), color=(0, 255, 0), thickness=2)
            mask[unit.mask] = (0, 50, 0)

            # Find and draw the contour as well
            c_mask = np.zeros((image.shape[0], image.shape[1], 1), dtype=np.uint8)
            c_mask[unit.mask] = 255
            _, contours, _ = cv2.findContours(c_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            tam = 0
            contornoGrande = None

            for contorno in contours:
                if len(contorno) > tam:
                    contornoGrande = contorno
                    tam = len(contorno)

            if contornoGrande is not None:
                cv2.drawContours(mask, contornoGrande.astype('int'), -1, (0, 255, 0), 2)

        mask_path = os.path.join(path, "mask.png")
        cv2.imwrite(mask_path, mask)
        pass


