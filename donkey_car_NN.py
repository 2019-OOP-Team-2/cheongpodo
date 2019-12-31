import time

import cv2 as cv
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable

import jetson_nano_move as jm
from console_input import getch


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
        self.fc1 = nn.Linear(6960, 910)  # 157x87 = 13659
        self.fc2 = nn.Linear(910, 60)
        self.fc3 = nn.Linear(60, 1)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 13659)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


net: Net = Net()
net.cuda()
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

jm.set_throttle(0)
time.sleep(1)
# camera init
img = jm.cap

try:
    while True:
        _, raw_img = img.read()
        b, g, r = cv.split(raw_img)
        b, g, r = torch.from_numpy(b), torch.from_numpy(g), torch.from_numpy(r)
        input_tensor = torch.cat((b.unsqueeze_(0), g.unsqueeze_(0), r.unsqueeze_(0))).unsqueeze_(0)
        optimizer.zero_grad()
        inputs = Variable(input_tensor.cuda()).float()
        in_char = getch()
        deg = 0
        cv.imshow('judge', raw_img)
        if (in_char == 'a'):
            deg = jm.MAX_STEER_DEV
        elif (in_char == 'd'):
            deg = -jm.MAX_STEER_DEV
        label = Variable(torch.tensor([deg]).cuda())
        outputs = net(inputs)
        loss = criterion(outputs, label)
        loss.backward()
        optimizer.step()

except KeyboardInterrupt:
    print('ctrl + C trapped')

finish_program(img)
