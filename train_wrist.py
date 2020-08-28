import sys
import torch
from network import wristNetwork
import torch.nn as nn
from utils import *

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
out_joints = [3,4,5]
in_joints = [3,4,5]
window = 20
skip = 5

data = sys.argv[1]
train_path = '../data/csv/val/' + data + '/'
val_path = '../data/csv/val/' + data + '/'
root = Path('checkpoints' ) 
folder = data + "_wrist_window" + str(window) + '_' + str(skip)

lr = 1e-2
batch_size = 4096
epochs = 1000
validate_each = 5
use_previous_model = False
epoch_to_use = 5

networks = []
for j in range(len(out_joints)):
    networks.append(wristNetwork(window, len(in_joints)))
    networks[j].to(device)
                          
model = jointLearner(data, folder, networks, window, skip, out_joints, in_joints, batch_size, lr, device)

if use_previous_model:
    model.load_prev(epoch_to_use)
    epoch = epoch_to_use + 1
else:
    epoch = 1

print('Training for ' + str(epochs))
for e in range(epoch, epochs + 1):

    model.train_step(e)
    
    if e % validate_each == 0:
        model.val_step(e)
