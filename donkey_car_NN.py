import time

import cv2 as cv
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable

import jetson_nano_move as jm


def finish_program(video_capture: cv.VideoCapture) -> None:
    video_capture.release()
    jm.set_throttle(0)
    cv.destroyAllWindows()


class Net(nn.Module):  # 640 x 360 input
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(6960, 910)
        self.fc2 = nn.Linear(910, 60)
        self.fc3 = nn.Linear(60, 3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(1, -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def debug_print(a):
    if debug:
        print(a)


net: Net = Net().cuda()
criterion = nn.CrossEntropyLoss().cuda()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

jm.set_throttle(0)
time.sleep(1)
# camera init
img = jm.cap

debug = True
learn = True
try:
    while True:
        _, raw_img = img.read()
        b, g, r = cv.split(raw_img)
        b, g, r = torch.from_numpy(b), torch.from_numpy(g), torch.from_numpy(r)
        input_tensor = torch.cat((b.unsqueeze_(0), g.unsqueeze_(0), r.unsqueeze_(0))).unsqueeze_(0)
        optimizer.zero_grad()
        inputs = Variable(input_tensor.cuda()).float()
        deg = 1  # straight
        cv.imshow('judge', raw_img)

        in_char = cv.waitKey(1)  # getch()
        if in_char == 'a':
            deg = 0  # jm.MAX_STEER_DEV
        elif in_char == 'd':
            deg = 2  # -jm.MAX_STEER_DEV
        elif in_char == 'w':
            learn = False

        debug_print(f'input: {in_char}')
        label = Variable(torch.tensor([deg]).cuda()).long()
        outputs = net(inputs)
        debug_print(f'label: {label}')
        debug_print(f'output: {outputs}')

        if learn:
            loss = criterion(outputs, label).cuda()
            loss.backward()
            optimizer.step()

except KeyboardInterrupt:
    print('ctrl + C trapped')

finish_program(img)
