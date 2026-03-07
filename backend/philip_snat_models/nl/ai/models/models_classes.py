import torch
from torch import nn


class WinnerModel(torch.nn.Module):
    def __init__(self, num_features):
        super(WinnerModel, self).__init__()
        self.fc1 = nn.Linear(in_features=num_features, out_features=6)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.1)
        self.fc2 = nn.Linear(in_features=6, out_features=1)
        self.sigm2 = nn.Sigmoid()

    def forward(self, inputs):
        x = self.fc1(inputs)
        x = self.relu1(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        x = self.sigm2(x)
        return x


class GoalsModel(torch.nn.Module):
    def __init__(self, strategy):
        super(GoalsModel, self).__init__()
        self.fc1 = nn.Linear(in_features=len(strategy["attributes"]), out_features=16)
        self.tanh1 = nn.Tanh()

        self.fc_total = nn.Linear(in_features=16, out_features=11)
        self.fc_home = nn.Linear(in_features=16, out_features=6)
        self.fc_away = nn.Linear(in_features=16, out_features=6)

        self.softmax = nn.Softmax(dim=1)

    def forward(self, inputs):
        x = self.fc1(inputs)
        x = self.tanh1(x)

        total_logits = self.fc_total(x)
        home_logits = self.fc_home(x)
        away_logits = self.fc_away(x)

        total_probs = self.softmax(total_logits)
        home_probs = self.softmax(home_logits)
        away_probs = self.softmax(away_logits)

        return {"total": total_probs, "home": home_probs, "away": away_probs}


class Prediction:
    def __init__(self, home_team, away_team, game_id, date):
        self.home_team = home_team
        self.away_team = away_team
        self.game_id = game_id
        self.date = date
        self.total_goals = {}
        self.home_goals = {}
        self.away_goals = {}
        self.winner = None

    def add_total_goal(self, goal_count, probability):
        self.total_goals[goal_count] = probability

    def add_home_goal(self, goal_count, probability):
        self.home_goals[goal_count] = probability

    def add_away_goal(self, goal_count, probability):
        self.away_goals[goal_count] = probability

    def add_winner(self, winner):
        self.winner = winner

    def calculate_events(self):
        pass
