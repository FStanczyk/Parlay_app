import torch
from torch import nn
from philip_snat_models.khl.ai.models.model_utils import WINNER_STRATEGY, GOALS_STRATEGY


class WinnerModel(torch.nn.Module):
    def __init__(self):
        super(WinnerModel, self).__init__()
        self.fc1 = nn.Linear(in_features=len(WINNER_STRATEGY["attributes"]), out_features=6)
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
        total_probs = self.softmax(self.fc_total(x))
        home_probs = self.softmax(self.fc_home(x))
        away_probs = self.softmax(self.fc_away(x))
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

        self.ML1 = 0
        self.ML2 = 0
        self.X = 0
        self.homeReg = 0
        self.awayReg = 0
        self.X1 = 0
        self.X2 = 0
        self.o35 = 0
        self.o45 = 0
        self.o55 = 0
        self.o65 = 0
        self.o75 = 0
        self.o85 = 0
        self.u35 = 0
        self.u45 = 0
        self.u55 = 0
        self.u65 = 0
        self.u75 = 0
        self.u85 = 0
        self.homeOver15 = 0
        self.homeOver25 = 0
        self.homeOver35 = 0
        self.homeOver45 = 0
        self.awayOver15 = 0
        self.awayOver25 = 0
        self.awayOver35 = 0
        self.awayOver45 = 0
        self.homeHandi15 = 0
        self.awayHandi15 = 0
        self.homeAndOver45 = 0
        self.homeAndOver55 = 0
        self.homeAndOver65 = 0
        self.homeAndUnder45 = 0
        self.homeAndUnder55 = 0
        self.homeAndUnder65 = 0
        self.awayAndOver45 = 0
        self.awayAndOver55 = 0
        self.awayAndOver65 = 0
        self.awayAndUnder45 = 0
        self.awayAndUnder55 = 0
        self.awayAndUnder65 = 0

    def add_total_goal(self, goal_count, probability):
        self.total_goals[goal_count] = probability

    def add_home_goal(self, goal_count, probability):
        self.home_goals[goal_count] = probability

    def add_away_goal(self, goal_count, probability):
        self.away_goals[goal_count] = probability

    def add_winner(self, winner):
        self.winner = winner

    def calculate_events(self):
        self.ML1 = 1 - self.winner
        self.ML2 = self.winner

        self.X = sum(
            self.home_goals.get(count, 0) * self.away_goals.get(count, 0)
            for count in range(6)
        )

        prob_home_win = 0
        prob_away_win = 0
        prob_home_win_by_15_plus = 0
        prob_away_win_by_15_plus = 0

        for home_count in range(6):
            for away_count in range(6):
                prob_home_goals = self.home_goals.get(home_count, 0)
                prob_away_goals = self.away_goals.get(away_count, 0)
                match_prob = prob_home_goals * prob_away_goals

                if home_count > away_count:
                    prob_home_win += match_prob
                    if home_count - away_count > 1.5:
                        prob_home_win_by_15_plus += match_prob
                elif away_count > home_count:
                    prob_away_win += match_prob
                    if away_count - home_count > 1.5:
                        prob_away_win_by_15_plus += match_prob

        self.homeReg = prob_home_win
        self.awayReg = prob_away_win
        self.X1 = 1 - prob_away_win
        self.X2 = 1 - prob_home_win
        self.homeHandi15 = prob_home_win_by_15_plus
        self.awayHandi15 = prob_away_win_by_15_plus

        self.o35 = 1 - sum(self.total_goals.get(i, 0) for i in range(4))
        self.o45 = 1 - sum(self.total_goals.get(i, 0) for i in range(5))
        self.o55 = 1 - sum(self.total_goals.get(i, 0) for i in range(6))
        self.o65 = 1 - sum(self.total_goals.get(i, 0) for i in range(7))
        self.o75 = 1 - sum(self.total_goals.get(i, 0) for i in range(8))
        self.o85 = 1 - sum(self.total_goals.get(i, 0) for i in range(9))

        self.u35 = sum(self.total_goals.get(i, 0) for i in range(3))
        self.u45 = sum(self.total_goals.get(i, 0) for i in range(4))
        self.u55 = sum(self.total_goals.get(i, 0) for i in range(6))
        self.u65 = sum(self.total_goals.get(i, 0) for i in range(7))
        self.u75 = sum(self.total_goals.get(i, 0) for i in range(8))
        self.u85 = sum(self.total_goals.get(i, 0) for i in range(9))

        self.homeOver15 = 1 - sum(self.home_goals.get(i, 0) for i in range(2))
        self.homeOver25 = 1 - sum(self.home_goals.get(i, 0) for i in range(3))
        self.homeOver35 = 1 - sum(self.home_goals.get(i, 0) for i in range(4))
        self.homeOver45 = 1 - sum(self.home_goals.get(i, 0) for i in range(5))

        self.awayOver15 = 1 - sum(self.away_goals.get(i, 0) for i in range(2))
        self.awayOver25 = 1 - sum(self.away_goals.get(i, 0) for i in range(3))
        self.awayOver35 = 1 - sum(self.away_goals.get(i, 0) for i in range(4))
        self.awayOver45 = 1 - sum(self.away_goals.get(i, 0) for i in range(5))

        self.homeAndOver45 = self.o45 * self.homeReg
        self.homeAndOver55 = self.o55 * self.homeReg
        self.homeAndOver65 = self.o65 * self.homeReg
        self.homeAndUnder45 = self.u45 * self.homeReg
        self.homeAndUnder55 = self.u55 * self.homeReg
        self.homeAndUnder65 = self.u65 * self.homeReg

        self.awayAndOver45 = self.o45 * self.awayReg
        self.awayAndOver55 = self.o55 * self.awayReg
        self.awayAndOver65 = self.o65 * self.awayReg
        self.awayAndUnder45 = self.u45 * self.awayReg
        self.awayAndUnder55 = self.u55 * self.awayReg
        self.awayAndUnder65 = self.u65 * self.awayReg
