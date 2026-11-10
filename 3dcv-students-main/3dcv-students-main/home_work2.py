from torch.optim import sparse_adam

from vll.utils.download import download_mnist
import numpy as np
import matplotlib.pyplot as plt

import skimage
import skimage.io

import torch
import torch.nn.functional as F
from torchvision import transforms

from models.mnist.simple_cnn import Net

##----------------------------------------------------
def task1():
    # Create a numpy array that looks like this: [0, 1, 2, ..., 19]
    arr = np.arange(0, 20)

    # Convert the numpy array to a torch tensor
    tensor = torch.from_numpy(arr)
    print(tensor)

    # Create a tensor that contains random numbers.
    # It should have the same size like the numpy array.
    # Multiply it with the previous tensor.
    rand_tensor = torch.randn_like(tensor, dtype=torch.float)
    tensor = rand_tensor * tensor
    print(tensor)

    # Create a tensor that contains only 1s.
    # It should have the same size like the numpy array.
    # Substract it from the previous tensor.
    tensor = torch.ones(arr.size)
    print(tensor)

    # Get the 5th element using a index.
    element = tensor[4]
    print(element)

    # Create a tensor that contains only 0s.
    # It should have the same size likes the numpy array.
    # Multiply it with the previous tensor without any assignment (in place).
    tensor_zeros = tensor.new_zeros(arr.size)
    print(tensor_zeros.mul(tensor))


##---------------------------------------------------
def task2():
    # Load the image from the last exercise as RGB image.
    image = skimage.io.imread('./data/pepo.jpg')

    # Convert the image to a tensor
    image = torch.from_numpy(image)

    # Print its shape
    print(image.shape)

    # Flatten the image
    image = image.flatten()
    print(len(image))

    # Add another dimension resulting in a 1x78642 tensor
    image = image.unsqueeze(0)
    print(image.shape)

    # Revert the last action
    image = image.squeeze()
    print(image.shape)
    #
    # Reshape the tensor, so that it has the original 2D dimensions
    image = image.reshape([512, 512, 3])
    print(image.shape)
    #
    # Calculate the sum, mean and max of the tensor
    print(torch.sum(image))

    print(torch.mean(image.float()))
    print(torch.max(image))


##----------------------------------------------------
def task3():
    # Create a random 2x2 tensor which requires gradients
    x = torch.randn([2,2],requires_grad=True)
    print(x)

    # Create another tensor by adding 2.0
    y = x+2.0
    print(y)

    # Create a third tensor z = y^2
    z = y**2
    print(z)

    # Compute out as the mean of values in z
    out = torch.mean(z.float())
    print(out)

    # Perform back propagation on out
    out.backward()
    # Print the gradients dout/dx
    print(x.grad)

    # Create a copy of y whithout gradients
    y2 = y.clone().detach()
    print(y2.requires_grad)

    # Perform the mean operation on z
    # with gradients globally disabled
    with torch.no_grad():
        out2 = torch.mean(z)
    print(out2.requires_grad)

def task4():
    import os

    download_mnist()

    class MNIST:
        """Dataset class for MNIST."""

        def __init__(self, root, transform=None):
            self.transform = transform

            # 类别文件夹，例如 "0", "1", ..., "9"
            self.classes = sorted(
                [
                    name for name in os.listdir(root)
                    if os.path.isdir(os.path.join(root, name))
                ],
                key=lambda name: int(name)
            )

            # 保存 (图片路径, 标签)
            self.samples = []
            valid_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")

            for class_name in self.classes:
                class_dir = os.path.join(root, class_name)
                label = int(class_name)

                for filename in sorted(os.listdir(class_dir)):
                    if filename.lower().endswith(valid_extensions):
                        image_path = os.path.join(class_dir, filename)
                        self.samples.append((image_path, label))

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, index):
            image_path, label = self.samples[index]

            # MNIST 是灰度图；skimage 读入后转成 float32
            image = skimage.io.imread(image_path, as_gray=True)
            image = np.asarray(image, dtype=np.float32)

            if self.transform is not None:
                image = self.transform(image)

            return image, label

    def validate(model, data_loader):
        fig, axes = plt.subplots(10, 10, figsize=(12, 12))
        axes = axes.flatten()

        model.eval()
        correct = 0
        total = 0
        device = next(model.parameters()).device

        with torch.no_grad():
            for i, (images, labels) in enumerate(data_loader):
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                predictions = outputs.argmax(dim=1)

                correct += (predictions == labels).sum().item()
                total += labels.size(0)

                # 显示前 100 张图
                if i < 100:
                    image_to_show = images[0, 0].cpu().numpy()

                    # 撤销 Normalize，便于正常显示图片
                    image_to_show = image_to_show * 0.3081 + 0.1307
                    image_to_show = np.clip(image_to_show, 0, 1)

                    axes[i].imshow(
                        image_to_show,
                        cmap="gray",
                        vmin=0,
                        vmax=1
                    )

                    predicted_label = predictions[0].item()
                    true_label = labels[0].item()

                    # 错误预测用红色显示
                    title_color = (
                        "red" if predicted_label != true_label else "black"
                    )
                    axes[i].set_title(
                        f"pred: {predicted_label}",
                        color=title_color,
                        fontsize=8
                    )
                    axes[i].axis("off")

        plt.tight_layout()
        plt.show()

        accuracy = 100 * correct / total
        print(f"Prediction accuracy: {accuracy:.2f}%")

    data_loader = torch.utils.data.DataLoader(
        MNIST(
            "data/mnist/testing",
            transform=transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])
        ),
        batch_size=1,
        shuffle=True
    )

    model = Net()
    model.load_state_dict(torch.load("models/mnist/simple_cnn.pt"))

    validate(model, data_loader)

if __name__ == '__main__':
    # task1()
    # task2()
    # task3()
    task4()