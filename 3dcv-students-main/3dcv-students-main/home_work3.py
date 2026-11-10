
import numpy as np
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
# from debugpy.launcher import output
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR


def train(model, use_cuda, train_loader, optimizer, epoch, log_interval):
    """
    Train one epoch

    model -- the neural network
    use_cuda -- true if GPU should be used
    train_loader -- data loader
    optimizer -- network optimizer
    epoch -- number of current epoch
    log_interval -- number of training steps between logs
    """
    # TODO: set the model to train mode
    model.train()

    # TODO: enumerate over the dataloader to get mini batches
    #       of images and ground truth labels
    # HINT: the builtin python function enumerate() also gives you indices
    for batch_idx, (data, target) in enumerate(train_loader):
        if use_cuda:
            data = data.cuda()
            target = target.cuda()
        # TODO: set the optimizers gradients to zero
        optimizer.zero_grad()

        # TODO: run the network
        output = model(data)

        # TODO: compute negative log likelihood loss
        loss = F.nll_loss(output, target)

        # TODO: do backpropagation
        loss.backward()

        # TODO: optimize
        optimizer.step()
        # TODO: print current loss for every nth ("log_interval"th) iteration
        if batch_idx % log_interval == 0:
            print(loss.item())


def validate(model, use_cuda, test_loader):
    """
    Compute test metrics

    model -- the neural network
    use_cuda -- true if GPU should be used
    test_loader -- data loader
    """
    # create a 10x10 grid of subplots
    _, axis = plt.subplots(10, 10)

    # set model to evaluation mode
    model.eval()
    test_loss = 0
    correct = 0
    plotted = 0

    # disable gradients globally
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(test_loader):
            # for each batch
            if use_cuda:
                # transfer to GPU
                data = data.cuda()
                target = target.cuda()

            # run network and compute metrics
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability

            img_correct = pred.eq(target.view_as(pred))
            correct += pred.eq(target.view_as(pred)).sum().item()

            # plot the first 100 images
            img_idx = 0
            data = data.cpu().numpy()

            while plotted < 100 and img_idx < data.shape[0]:
                # compute position of ith image in the grid
                y = plotted % 10
                x = plotted // 10

                # convert image tensor to numpy array and normalize to [0, 1]
                img = data[img_idx, 0]
                img = (img - np.min(img)) / (np.max(img) - np.min(img))

                # make wrongly predicted images red
                img = np.stack([img] * 3, 2)
                if img_correct[img_idx] == 0:
                    img[:, :, 1:] = 0.0

                # disable axis and show image
                axis[y][x].axis('off')
                axis[y][x].imshow(img)

                # show the predicted class next to each image
                axis[y][x].text(30, 25, pred[img_idx].item())

                plotted += 1
                img_idx += 1

    test_loss /= len(test_loader.dataset)

    # show results
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))
    plt.show()


class FCNet1(nn.Module):
    """
    Fully Connected Neural Network

    Five fully connected layers with sigmoid non-linearity

    Dimensions
    784->200->100->60->30->10
    """

    def __init__(self):
        super(FCNet1, self).__init__()
        # TODO: initialize network layers
        # HINT: take a look at "torch.nn" (imported as "nn")
        self.fc1 = nn.Linear(784, 200)
        self.fc2 = nn.Linear(200, 100)
        self.fc3 = nn.Linear(100, 60)
        self.fc4 = nn.Linear(60, 30)
        self.fc5 = nn.Linear(30, 10)

    def forward(self, x):
        # TODO: reshape batch of images to batch of 1D vectors
        x = torch.flatten(x, 1)

        # TODO: run network layers
        x = torch.sigmoid(self.fc1(x))
        x = torch.sigmoid(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        x = torch.sigmoid(self.fc4(x))
        x = self.fc5(x)
        # TODO: compute log softmax over the output
        # HINT: take a look at "torch.nn.functional" (imported as "F")
        output = F.log_softmax(x, dim=1)
        return output


class FCNet2(nn.Module):
    def __init__(self):
        super(FCNet2, self).__init__()
        self.fc1 = nn.Linear(784, 200)
        self.fc2 = nn.Linear(200, 100)
        self.fc3 = nn.Linear(100, 60)
        self.fc4 = nn.Linear(60, 30)
        self.fc5 = nn.Linear(30, 10)

    def forward(self, x):
        # TODO: reshape batch of images to batch of 1D vectors
        x = torch.flatten(x, 1)

        # TODO: run network layers
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.relu(self.fc4(x))
        x = self.fc5(x)
        # TODO: compute log softmax over the output
        # HINT: take a look at "torch.nn.functional" (imported as "F")
        output = F.log_softmax(x, dim=1)
        return output


class FCNet3(nn.Module):
    def __init__(self):
        super(FCNet3, self).__init__()
        self.fc1 = nn.Linear(784, 200)
        self.fc2 = nn.Linear(200, 100)
        self.fc3 = nn.Linear(100, 60)
        self.fc4 = nn.Linear(60, 30)
        self.fc5 = nn.Linear(30, 10)
        self.bn1 = nn.BatchNorm1d(200)
        self.bn3 = nn.BatchNorm1d(60)

    def forward(self, x):
        # TODO: reshape batch of images to batch of 1D vectors
        x = torch.flatten(x, 1)
        # TODO: run network layers
        x = torch.relu(self.bn1(self.fc1(x)))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.bn3(self.fc3(x)))
        x = torch.relu(self.fc4(x))
        x = self.fc5(x)
        # TODO: compute log softmax over the output
        # HINT: take a look at "torch.nn.functional" (imported as "F")
        output = F.log_softmax(x, dim=1)
        return output


class ConvNet1(nn.Module):
    """
    Convolutional Neural Network

    Two convolutional layers and two fully connected layers

    Dimensions:
    1x28x28->32x26x26->64x12x12->128->10
    """

    def __init__(self):
        super(ConvNet1, self).__init__()

        # TODO: initialize network layers
        self.conv1 = nn.Conv2d(1, 32, 3)
        self.conv2 = nn.Conv2d(32, 64, 3, stride=2)
        self.fc1 = nn.Linear(64 * 12 * 12, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        # TODO: run convolutional layers
        output = F.relu(self.conv1(x))
        output = F.relu(self.conv2(output))
        # TODO: rehape batch of images to batch of 1D vectors
        output = torch.flatten(output, start_dim=1)

        # TODO: run fully connected layers
        output = F.relu(self.fc1(output))
        output = F.log_softmax(self.fc2(output), 1)
        # TODO: compute log softmax over the output

        return output


class ConvNet2(nn.Module):
    def __init__(self):
        super(ConvNet2, self).__init__()

        # TODO: initialize network layers
        self.conv1 = nn.Conv2d(1, 32, 3)
        self.conv2 = nn.Conv2d(32, 64, 3, stride=2)
        self.fc1 = nn.Linear(64 * 12 * 12, 128)
        self.fc2 = nn.Linear(128, 10)
        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm1d(128)

    def forward(self, x):
        # TODO: run convolutional layers
        output = F.relu(self.bn1(self.conv1(x)))

        output = F.relu(self.conv2(output))
        # TODO: rehape batch of images to batch of 1D vectors
        output = torch.flatten(output, start_dim=1)

        # TODO: run fully connected layers
        output = F.relu(self.bn2(self.fc1(output)))
        output = F.log_softmax(self.fc2(output), 1)
        # TODO: compute log softmax over the output

        return output


class ConvNet3(nn.Module):
    def __init__(self):
        super(ConvNet3, self).__init__()

        self.conv1 = nn.Conv2d(1, 32, 3)
        self.conv2 = nn.Conv2d(32, 64, 3, stride=1)
        self.pool1 = nn.MaxPool2d(2, 2)

        """ what
        A max pooling layer moves a small window across a feature map 
        and returns the largest value inside each window.
         
        Input feature map         Output
        1 3 | 2 4                  5 4
        5 2 | 1 0                  8 9
        ----+-----
        6 8 | 3 1
        2 4 | 7 9
        """

        """ why
        The first reason is to reduce spatial resolution while keeping strong
         local responses. For image classification, 
         we often care whether a useful feature appears in a region, 
         rather than its exact pixel position. 
        
        """
        self.fc1 = nn.Linear(64 * 12 * 12, 128)
        self.fc2 = nn.Linear(128, 10)
        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm1d(128)



    def forward(self, x):
        output = F.relu(self.bn1(self.conv1(x)))
        # 1 * 28 * 28 -> 32 * 26 * 26
        # floor((length − window) / stride) + 1 (28-3)/1+1

        output = self.pool1(F.relu(self.conv2(output)))
        #64 * 24 * 24 -> 64 * 12 *12

        output = torch.flatten(output, start_dim=1)

        output = F.relu(self.bn2(self.fc1(output)))

        output = F.log_softmax(self.fc2(output), 1)

        return output

if __name__ == '__main__':

    # hyper parameters
    batch_size = 64
    test_batch_size = 1000

    epochs = 10
    lr = 1.0
    gamma = 0.7
    log_interval = 100


    # use GPU if available
    use_cuda = torch.cuda.is_available()
    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}

    print("PyTorch 版本：", torch.__version__)
    print("PyTorch 的 CUDA 版本：", torch.version.cuda)
    print("CUDA 是否可用：", torch.cuda.is_available())


    # initialize data loaders
    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST('../data', train=True, download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])), batch_size=batch_size, shuffle=True, **kwargs)

    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST('../data', train=False,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])),
        batch_size=test_batch_size, shuffle=True, **kwargs)

    model = FCNet3()
    if use_cuda:
        model = model.cuda()
    print("模型所在设备：", next(model.parameters()).device)

    # initialize optimizer and scheduler
    optimizer = optim.Adadelta(model.parameters(), lr=lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=gamma)

    for epoch in range(1, epochs + 1):
        # train one epoch
        train(model, use_cuda, train_loader, optimizer, epoch, log_interval)

        # run on test dataset
        validate(model, use_cuda, test_loader)
        scheduler.step()

        torch.save(model.state_dict(), "models/mnist/checkpoint.pt")
