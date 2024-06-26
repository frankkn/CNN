import random
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import os
from data_aug.bbox_util import *

lib_path = os.path.join(os.path.realpath("."), "data_aug")
sys.path.append(lib_path)


class RandomHorizontalFlip(object):
    """Randomly horizontally flips the Image with the probability *p*

    Parameters
    ----------
    p: float
        The probability with which the image is flipped

    Returns
    -------

    numpy.ndarray
        Flipped image in the numpy format of shape `HxWxC`

    """

    def __init__(self, p=0.5):
        self.p = p

    def __call__(self, img):
        img_center = np.array(img.shape[:2])[::-1]/2
        img_center = np.hstack((img_center, img_center))
        if random.random() < self.p:
            img = img[:, ::-1, :]

        return img


class HorizontalFlip(object):
    """Randomly horizontally flips the Image with the probability *p*

    Parameters
    ----------
    p: float
        The probability with which the image is flipped

    Returns
    -------

    numpy.ndarray
        Flipped image in the numpy format of shape `HxWxC`

    """

    def __init__(self):
        pass

    def __call__(self, img):
        img_center = np.array(img.shape[:2])[::-1] / 2
        img_center = np.hstack((img_center, img_center))

        img = img[:, ::-1, :]

        return img


class RandomScale(object):
    """Randomly scales an image    
    
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    Parameters
    ----------
    scale: float or tuple(float)
        if **float**, the image is scaled by a factor drawn 
        randomly from a range (1 - `scale` , 1 + `scale`). If **tuple**,
        the `scale` is drawn randomly from values specified by the 
        tuple
        
    Returns
    -------
    
    numpy.ndarray
        Scaled image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, scale=0.2, diff=False):
        self.scale = scale

        if type(self.scale) == tuple:
            assert len(self.scale) == 2, "Invalid range"
            assert self.scale[0] > -1, "Scale factor can't be less than -1"
            assert self.scale[1] > -1, "Scale factor can't be less than -1"
        else:
            assert self.scale > 0, "Please input a positive float"
            self.scale = (max(-1, -self.scale), self.scale)

        self.diff = diff

    def __call__(self, img):
        # Chose a random digit to scale by
        img_shape = img.shape

        if self.diff:
            scale_x = random.uniform(*self.scale)
            scale_y = random.uniform(*self.scale)
        else:
            scale_x = random.uniform(*self.scale)
            scale_y = scale_x

        resize_scale_x = 1 + scale_x
        resize_scale_y = 1 + scale_y

        img = cv2.resize(img, None, fx=resize_scale_x, fy=resize_scale_y)

        canvas = np.zeros(img_shape, dtype=np.uint8)

        y_lim = int(min(resize_scale_y, 1) * img_shape[0])
        x_lim = int(min(resize_scale_x, 1) * img_shape[1])

        canvas[:y_lim, :x_lim, :] = img[:y_lim, :x_lim, :]

        img = canvas

        return img


class Scale(object):
    """Scales the image    
        
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    
    Parameters
    ----------
    scale_x: float
        The factor by which the image is scaled horizontally
        
    scale_y: float
        The factor by which the image is scaled vertically
        
    Returns
    -------
    
    numpy.ndarray
        Scaled image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, scale_x=0.2, scale_y=0.2):
        self.scale_x = scale_x
        self.scale_y = scale_y

    def __call__(self, img):
        img_shape = img.shape

        resize_scale_x = 1 + self.scale_x
        resize_scale_y = 1 + self.scale_y

        img = cv2.resize(img, None, fx=resize_scale_x, fy=resize_scale_y)

        canvas = np.zeros(img_shape, dtype=np.uint8)

        y_lim = int(min(resize_scale_y, 1) * img_shape[0])
        x_lim = int(min(resize_scale_x, 1) * img_shape[1])

        canvas[:y_lim, :x_lim, :] = img[:y_lim, :x_lim, :]

        img = canvas

        return img

    
class RandomTranslate(object):
    """Randomly Translates the image    
    
    
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    Parameters
    ----------
    translate: float or tuple(float)
        if **float**, the image is translated by a factor drawn 
        randomly from a range (1 - `translate` , 1 + `translate`). If **tuple**,
        `translate` is drawn randomly from values specified by the 
        tuple
        
    Returns
    -------
    
    numpy.ndarray
        Translated image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, translate=0.2, diff=False):
        self.translate = translate
        
        if type(self.translate) == tuple:
            assert len(self.translate) == 2, "Invalid range"  
            assert 0 < self.translate[0] < 1 and 0 < self.translate[1] < 1

        else:
            assert 0 < self.translate < 1
            self.translate = (-self.translate, self.translate)
            
        self.diff = diff

    def __call__(self, img):
        # Chose a random digit to translate by 
        img_shape = img.shape
        
        # Translate the image
        
        # Percentage of the dimension of the image to translate
        translate_factor_x = random.uniform(*self.translate)
        translate_factor_y = random.uniform(*self.translate)
        
        if not self.diff:
            translate_factor_y = translate_factor_x
            
        canvas = np.zeros(img_shape).astype(np.uint8)
    
        corner_x = int(translate_factor_x * img.shape[1])
        corner_y = int(translate_factor_y * img.shape[0])
        
        # Change the origin to the top-left corner of the translated box
        orig_box_cords = [max(0, corner_y), max(corner_x, 0), min(img_shape[0], corner_y + img.shape[0]), min(img_shape[1], corner_x + img.shape[1])]
    
        mask = img[max(-corner_y, 0):min(img.shape[0], -corner_y + img_shape[0]), max(-corner_x, 0):min(img.shape[1], -corner_x + img_shape[1]), :]
        canvas[orig_box_cords[0]:orig_box_cords[2], orig_box_cords[1]:orig_box_cords[3], :] = mask
        img = canvas
        
        return img

    
class Translate(object):
    """Randomly Translates the image    
    
    
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    Parameters
    ----------
    translate_x: float
        The factor by which the image is translated horizontally
        
    translate_y: float
        The factor by which the image is translated vertically
        
    Returns
    -------
    
    numpy.ndarray
        Translated image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, translate_x=0.2, translate_y=0.2):
        self.translate_x = translate_x
        self.translate_y = translate_y

        assert 0 < self.translate_x < 1
        assert 0 < self.translate_y < 1
 

    def __call__(self, img):
        # Chose a random digit to translate by 
        img_shape = img.shape
        
        # Translate the image
        
        # Percentage of the dimension of the image to translate
        translate_factor_x = self.translate_x
        translate_factor_y = self.translate_y
            
        canvas = np.zeros(img_shape).astype(np.uint8)

        # Get the top-left corner co-ordinates of the shifted box 
        corner_x = int(translate_factor_x * img.shape[1])
        corner_y = int(translate_factor_y * img.shape[0])
        
        # Change the origin to the top-left corner of the translated box
        orig_box_cords = [max(0, corner_y), max(corner_x, 0), min(img_shape[0], corner_y + img.shape[0]), min(img_shape[1], corner_x + img.shape[1])]

        mask = img[max(-corner_y, 0):min(img.shape[0], -corner_y + img_shape[0]), max(-corner_x, 0):min(img.shape[1], -corner_x + img_shape[1]), :]
        canvas[orig_box_cords[0]:orig_box_cords[2], orig_box_cords[1]:orig_box_cords[3], :] = mask
        img = canvas
        
        return img

    
class RandomRotate(object):
    """Randomly rotates an image    
    
    
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    Parameters
    ----------
    angle: float or tuple(float)
        if **float**, the image is rotated by a factor drawn 
        randomly from a range (-`angle`, `angle`). If **tuple**,
        the `angle` is drawn randomly from values specified by the 
        tuple
        
    Returns
    -------
    
    numpy.ndarray
        Rotated image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, angle=10):
        self.angle = angle
        
        if type(self.angle) == tuple:
            assert len(self.angle) == 2, "Invalid range"  
            
        else:
            self.angle = (-self.angle, self.angle)
            
    def __call__(self, img):
        """
        Args:
            img (numpy.ndarray): Image to be rotated.

        Returns:
            numpy.ndarray: Rotated image.
        """
    
        angle = random.uniform(*self.angle)
    
        w, h = img.shape[1], img.shape[0]
        cx, cy = w // 2, h // 2
    
        img = rotate_im(img, angle)
    
        return img

        
class Rotate(object):
    """Rotates an image    
    
    
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    Parameters
    ----------
    angle: float
        The angle by which the image is to be rotated 
        
        
    Returns
    -------
    
    numpy.ndarray
        Rotated image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, angle):
        self.angle = angle
        

    def __call__(self, img):
        """
        Args:
            img (numpy.ndarray): Image to be rotated.

        Returns:
            numpy.ndarray: Rotated image.
        """
        
        angle = self.angle
        print(self.angle)
        
        w, h = img.shape[1], img.shape[0]
        cx, cy = w // 2, h // 2

        img = rotate_im(img, angle)
        
        return img


class RandomShear(object):
    """Randomly shears an image in horizontal direction   
    
    
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    Parameters
    ----------
    shear_factor: float or tuple(float)
        if **float**, the image is sheared horizontally by a factor drawn 
        randomly from a range (-`shear_factor`, `shear_factor`). If **tuple**,
        the `shear_factor` is drawn randomly from values specified by the 
        tuple
        
    Returns
    -------
    
    numpy.ndarray
        Sheared image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, shear_factor=0.2):
        self.shear_factor = shear_factor
        
        if type(self.shear_factor) == tuple:
            assert len(self.shear_factor) == 2, "Invalid range for shearing factor"   
        else:
            self.shear_factor = (-self.shear_factor, self.shear_factor)
        
    def __call__(self, img):
        shear_factor = random.uniform(*self.shear_factor)
    
        w, h = img.shape[1], img.shape[0]
    
        if shear_factor < 0:
            img = HorizontalFlip()(img)
    
        M = np.array([[1, abs(shear_factor), 0],[0,1,0]])
    
        nW =  img.shape[1] + abs(shear_factor * img.shape[0])
    
        img = cv2.warpAffine(img, M, (int(nW), img.shape[0]))
    
        if shear_factor < 0:
            img = HorizontalFlip()(img)
    
        img = cv2.resize(img, (w, h))
    
        return img


class Shear(object):
    """Shears an image in horizontal direction   
    
    
    Bounding boxes which have an area of less than 25% in the remaining in the 
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.
    
    Parameters
    ----------
    shear_factor: float
        Factor by which the image is sheared in the x-direction
       
    Returns
    -------
    
    numpy.ndarray
        Sheared image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, shear_factor=0.2):
        self.shear_factor = shear_factor
        
    
    def __call__(self, img):
        shear_factor = self.shear_factor
        if shear_factor < 0:
            img = HorizontalFlip()(img)

        M = np.array([[1, abs(shear_factor), 0],[0,1,0]])
                
        nW =  img.shape[1] + abs(shear_factor * img.shape[0])
        
        img = cv2.warpAffine(img, M, (int(nW), img.shape[0]))
        
        if shear_factor < 0:
            img = HorizontalFlip()(img)
        
        return img

    
class Resize(object):
    """Resize the image in accordance with the `image_letter_box` function in darknet 
    
    The aspect ratio is maintained. The longer side is resized to the input 
    size of the network, while the remaining space on the shorter side is filled 
    with black color. **This should be the last transform**
    
    
    Parameters
    ----------
    inp_dim : tuple(int)
        tuple containing the size to which the image will be resized.
        
    Returns
    -------
    
    numpy.ndarray
        Resized image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, inp_dim):
        self.inp_dim = inp_dim

    def __call__(self, img):
        w, h = img.shape[1], img.shape[0]
        img = letterbox_image(img, self.inp_dim)

        scale = min(self.inp_dim / h, self.inp_dim / w)

        new_w = scale * w
        new_h = scale * h
        inp_dim = self.inp_dim   

        del_h = (inp_dim - new_h) / 2
        del_w = (inp_dim - new_w) / 2

        add_matrix = np.array([[del_w, del_h, del_w, del_h]]).astype(int)

        img = img.astype(np.uint8)

        return img

    
class RandomHSV(object):
    """HSV Transform to vary hue saturation and brightness
    
    Hue has a range of 0-179
    Saturation and Brightness have a range of 0-255. 
    Choose the amount you want to change the above quantities accordingly. 
    
    
    Parameters
    ----------
    hue : None or int or tuple (int)
        If None, the hue of the image is left unchanged. If int, 
        a random int is uniformly sampled from (-hue, hue) and added to the 
        hue of the image. If tuple, the int is sampled from the range 
        specified by the tuple.   
        
    saturation : None or int or tuple(int)
        If None, the saturation of the image is left unchanged. If int, 
        a random int is uniformly sampled from (-saturation, saturation) 
        and added to the hue of the image. If tuple, the int is sampled
        from the range specified by the tuple.   
        
    brightness : None or int or tuple(int)
        If None, the brightness of the image is left unchanged. If int, 
        a random int is uniformly sampled from (-brightness, brightness) 
        and added to the hue of the image. If tuple, the int is sampled
        from the range specified by the tuple.   
    
    Returns
    -------
    
    numpy.ndarray
        Transformed image in the numpy format of shape `HxWxC`
    
    """

    def __init__(self, hue=None, saturation=None, brightness=None):
        if hue:
            self.hue = hue 
        else:
            self.hue = 0
            
        if saturation:
            self.saturation = saturation 
        else:
            self.saturation = 0
            
        if brightness:
            self.brightness = brightness
        else:
            self.brightness = 0
            
        if type(self.hue) != tuple:
            self.hue = (-self.hue, self.hue)
            
        if type(self.saturation) != tuple:
            self.saturation = (-self.saturation, self.saturation)
        
        if type(self.brightness) != tuple:
            self.brightness = (-self.brightness, self.brightness)
    
    def __call__(self, img):
        hue = random.randint(*self.hue)
        saturation = random.randint(*self.saturation)
        brightness = random.randint(*self.brightness)
        
        img = img.astype(int)
        
        a = np.array([hue, saturation, brightness]).astype(int)
        img += np.reshape(a, (1, 1, 3))
        
        img = np.clip(img, 0, 255)
        img[:, :, 0] = np.clip(img[:, :, 0], 0, 179)
        
        img = img.astype(np.uint8)
        
        return img

    
class Sequence(object):
    def __init__(self, augmentations, probs=1):
        self.augmentations = augmentations
        self.probs = probs
        
    def __call__(self, images):
        for i, augmentation in enumerate(self.augmentations):
            if type(self.probs) == list:
                prob = self.probs[i]
            else:
                prob = self.probs
                
            if random.random() < prob:
                images = augmentation(images)
        return images
