import h5py
import numpy as np
from os import listdir, remove, mkdir
from os.path import isfile, join, isdir
import scipy.misc

img_size = 512
path_imgs = "/media/dnr/8EB49A21B49A0C39/data/DDSM-orig/mammograms"
path_masks = "/media/dnr/8EB49A21B49A0C39/data/DDSM-orig/masks"
#path_inf = "/media/dnr/8EB49A21B49A0C39/data/bone-orig/JonesBonesPart1C_PNG"
path_label = "/media/dnr/8EB49A21B49A0C39/data/DDSM-orig"
file_label = join(path_label, "mass_case_description.csv")

path_save = "/home/dnr/Documents/data/ddsm-512"
if not isdir(path_save):
    mkdir(path_save)
path_train = join(path_save, "training")
path_validation = join(path_save, "validation")
#path_inference = join(path_save, "inference")
if not isdir(path_train):
    mkdir(path_train)
if not isdir(path_validation):
    mkdir(path_validation)
#if not isdir(path_inference):
#    mkdir(path_inference)
#path_inference = join(path_inference, "inference")
#if not isdir(path_inference):
#    mkdir(path_inference)

pat_to_lab = {}
with open(file_label, 'r') as f:
    line = f.readline()
    line = f.readline()
    while line != "":
        line = line.split(',')
        pat_id = line[0] + '_' + line[2][0]
        label = 0
        if pat_id in pat_to_lab:
            label = pat_to_lab[pat_id]
        label = max(label, (line[9][0]=='M')+0)
        pat_to_lab[pat_id] = label
        line = f.readline()

list_imgs = listdir(path_imgs)
list_masks = listdir(path_masks)
list_val = []
list_train = []
for name_img in list_imgs:
    if name_img[0] == '.':
        continue
    if name_img[-4:] != '.tif':
        continue
    if name_img not in list_masks:
        continue
    name_pat = name_img[:9]
    if name_pat not in pat_to_lab:
        continue
    name_h5 = name_img[-6:-4] + '.h5'
    path_img = join(path_imgs, name_img)
    path_mask = join(path_masks, name_img)
    label = pat_to_lab[name_pat]
    print label
    # Converting image and mask to necessary format.
    img = scipy.misc.imread(path_img)
    img = img.astype(np.float32)
    if len(img.shape) == 3:
        img = np.mean(img, axis=2)
    height, width = img.shape
    img = scipy.misc.imresize(img, [img_size, img_size], interp='nearest')
    img = img.reshape([img_size, img_size, 1])
    img = img.astype(np.float32)
    img /= 255
    mask = scipy.misc.imread(path_mask)
    mask = mask.astype(np.float32)
    if len(mask.shape) == 3:
        mask = np.mean(mask, axis=2)
    mask = scipy.misc.imresize(mask, [img_size, img_size], interp='nearest')
    mask = (mask > 0) + 0
    mask = mask.astype(np.int32)
    # Save image and mask to h5.
    folder_save = name_pat
    if (np.random.choice(10) == 1 or name_pat in list_val) and name_pat not in list_train:
        if name_pat not in list_val:
            list_val.append(name_pat)
        if not isdir(join(path_validation, folder_save)):
            mkdir(join(path_validation, folder_save))
        path_save_file = join(path_validation,folder_save, name_h5)
    else:
        if name_pat not in list_train:
            list_train.append(name_pat)
        if not isdir(join(path_train, folder_save)):
            mkdir(join(path_train, folder_save))
        path_save_file = join(path_train, folder_save, name_h5)
    h5f = h5py.File(path_save_file, 'w')
    h5f.create_dataset('data', data=img)
    h5f.create_dataset('seg', data=mask)
    h5f.create_dataset('name', data=name_img)
    h5f.create_dataset('height', data=height)
    h5f.create_dataset('width', data=width)
    h5f.create_dataset('depth', data=1)
    h5f.create_dataset('label', data=label)
    h5f.close()

#list_imgs = listdir(path_inf)
#for name_img in list_imgs:
#    if name_img[0] == '.':
#        continue
#    if name_img[-4:] != '.png':
#        continue
#    path_img = join(path_inf, name_img)
#    # Converting image to necessary format
#    img = scipy.misc.imread(path_img)
#    img = img.astype(np.float32)
#    if len(img.shape) == 3:
#        img = np.mean(img, axis=2)
#    height, width = img.shape
#    img = scipy.misc.imresize(img, [img_size, img_size])
#    img = img.reshape([img_size, img_size, 1])
#    img = img.astype(np.float32)
#    img /= 255
#    # Save image to h5.
#    folder_save = name_save[:-4]
#    path_save_file = join(path_inference, name_img[:-4]+'.h5')
#    h5f = h5py.File(path_save_file, 'w')
#    h5f.create_dataset('data', data=img)
#    h5f.create_dataset('name', data=name_img)
#    h5f.create_dataset('height', data=height)
#    h5f.create_dataset('width', data=width)
#    h5f.create_dataset('depth', data=1)
#    h5f.close()
