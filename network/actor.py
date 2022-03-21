import torch
import torch.nn as nn 
from utils.net import build_mlp_extractor

LOG_STD_MIN = -20
LOG_STD_MAX = 2

# class StochasticActor(nn.Module):
#     def __init__(self, state_dim, hidden_size, action_dim, activation_fn=nn.Tanh):
#         super().__init__()
#         feature_extractor = build_mlp_extractor(state_dim, hidden_size, activation_fn)
#         if len(hidden_size)>0:
#             input_dim = hidden_size[-1]
#         else:
#             input_dim = state_dim
#         # mean and log std
#         mu = nn.Linear(input_dim, action_dim)
#         self.log_std = nn.Parameter(torch.zeros(1, action_dim), requires_grad=True)
        
#         # init parameter
#         mu.weight.data.mul_(0.1)
#         mu.bias.data.mul_(0.0)
        
#         # concat all the net
#         model = feature_extractor + [mu]
#         self.net = nn.Sequential(*model)
        
#     def forward(self, state):
#         action_mean = self.net(state)
#         action_log_std = self.log_std.expand_as(action_mean)
#         return action_mean, action_log_std.exp()

# class StochasticActor(nn.Module):
#     def __init__(self, state_dim, hidden_size, action_dim, activation_fn=nn.Tanh):
#         super().__init__()
#         self.feature_extractor = nn.Sequential(*build_mlp_extractor(state_dim, hidden_size, activation_fn))
#         if len(hidden_size)>0:
#             input_dim = hidden_size[-1]
#         else:
#             input_dim = state_dim
#         # mean and log std
#         self.mu, self.log_std = nn.Linear(input_dim, action_dim), nn.Linear(input_dim, action_dim)
#         # init parameter
#         self.mu.weight.data.mul_(0.1)
#         self.mu.bias.data.mul_(0.0)
        
#     def forward(self, state):
#         feature = self.feature_extractor(state)
#         action_mean, action_log_std = self.mu(feature), self.log_std(feature)
#         action_log_std = torch.clamp(action_log_std, LOG_STD_MIN, LOG_STD_MAX)
#         return action_mean, action_log_std.exp()

class StochasticActor(nn.Module):
    def __init__(self, state_dim, hidden_size, action_dim, activation_fn=nn.Tanh, state_std_independent=False):
        super().__init__()
        self.state_std_independent = state_std_independent
        self.feature_extractor = nn.Sequential(*build_mlp_extractor(state_dim, hidden_size, activation_fn))
        if len(hidden_size)>0:
            input_dim = hidden_size[-1]
        else:
            input_dim = state_dim
        # mean and log std
        self.mu = nn.Linear(input_dim, action_dim)
        # For mujoco, make std and state dependent can stable the evaluation curve,
        # and increase the final performance during evaluation
        if state_std_independent:
            self.log_std = nn.Parameter(torch.zeros(1, action_dim), requires_grad=True)
        else:
            self.log_std = nn.Linear(input_dim, action_dim)
        
        # init parameter
        self.mu.weight.data.mul_(0.1)
        self.mu.bias.data.mul_(0.0)
        
    def forward(self, state):
        feature = self.feature_extractor(state)
        action_mean = self.mu(feature)
        action_log_std = self.log_std if self.state_std_independent else self.log_std(feature)
        action_log_std = torch.clamp(action_log_std, LOG_STD_MIN, LOG_STD_MAX)
        return action_mean, action_log_std.exp()