import torch
import torch.nn.functional as F
import numpy as np
import json
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import skimage.transform
import argparse
from imageio import imread
from skimage.transform import resize as imresize
from PIL import Image
import json

from caption import caption_image_beam_search

def get_text(encoder, decoder, word_map, path_to_image: str, beam_size):

    #parser = argparse.ArgumentParser(description='Show, Attend, and Tell - Tutorial - Generate Caption')

    #parser.add_argument('--img', '-i', help='path to image')
    #parser.add_argument('--model', '-m', help='path to model')
    #parser.add_argument('--word_map', '-wm', help='path to word map JSON')
    #parser.add_argument('--beam_size', '-b', default=5, type=int, help='beam size for beam search')
    #parser.add_argument('--dont_smooth', dest='smooth', action='store_false', help='do not smooth alpha overlay')

    #args = parser.parse_args()



    # Encode, decode with attention and beam search
    seq, alphas = caption_image_beam_search(encoder, decoder, path_to_image, word_map, beam_size)
    alphas = torch.FloatTensor(alphas)

    #print(seq)

    with open("WORDMAP_coco_5_cap_per_img_5_min_word_freq.json", "r") as f:
        obj = json.load(f)

    d2 = {}
    for key, value in obj.items():
        d2[value] = key
        #print(key, value)

    res = ' '.join([d2[i] for i in seq])
    res = res[7:-5:]
    print(res)
    return res
    #return ans
    # Visualize caption and attention of best sequence
    # visualize_att(args.img, seq, alphas, rev_word_map, args.smooth)


class ImageCaptioner:
    def __init__(self, path_to_model, path_to_word_map):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load model
        checkpoint = torch.load(path_to_model, map_location=str(device))
        self.decoder = checkpoint['decoder']
        self.decoder = self.decoder.to(device)
        self.decoder.eval()
        self.encoder = checkpoint['encoder']
        self.encoder = self.encoder.to(device)
        self.encoder.eval()

        # Load word map (word2ix)
        with open(path_to_word_map, "r") as f:
            self.word_map = json.load(f)

    def caption(self, path_to_image):
        res = get_text(self.encoder, self.decoder, self.word_map, path_to_image, 5)
        return res

image_captioner = ImageCaptioner("BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar", "WORDMAP_coco_5_cap_per_img_5_min_word_freq.json")

def make_text_from_image(path: str):
    return image_captioner.caption(path)