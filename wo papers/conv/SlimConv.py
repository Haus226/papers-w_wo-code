import torch
from torch import nn

class SlimConv:
    def __init__(self, input_channels, r_se, r_1, r_2):
        self.se = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(input_channels, input_channels // r_se, 1),
            nn.BatchNorm2d(input_channels // r_se),
            nn.ReLU(),
            nn.Conv2d(input_channels // r_se, input_channels, 1),
            nn.Sigmoid()
        )

        self.conv_top = nn.Sequential(
            nn.Conv2d(input_channels // r_1, input_channels // r_1, 3),
            nn.BatchNorm2d(input_channels // r_1)
        )

        self.conv_bot = nn.Sequential(
            nn.Conv2d(input_channels // r_1, input_channels //r_1, 1),
            nn.BatchNorm2d(input_channels // r_1),
            nn.ReLU(),
            nn.Conv2d(input_channels // r_1, input_channels // r_2, 3),
            nn.BatchNorm2d(input_channels // r_2)
        )

        self.r_1 = r_1
        self.r_2 = r_2

    def forward(self, x):
        B, C, H, W = x.size()
        att = self.se(x)
        top = x * att
        bot = x * torch.flip(att, dims=[1]) 
        top_= torch.split(top, C // self.r_1, 1)
        bot_ = torch.split(bot, C // self.r_1, 1)
        top = torch.sum(torch.stack(top_), dim=0)
        bot = torch.sum(torch.stack(bot_), dim=0)
        top = self.conv_top(top)
        bot = self.conv_bot(bot)
        # Output features have C_in // r_1 + C_in // r_2 channels
        return torch.cat([top, bot], 1)

if __name__ == "__main__":
    t = torch.rand(32, 6, 21, 21)
    slim = SlimConv(6, 1, 3, 2)
    print(slim.forward(t).size())
