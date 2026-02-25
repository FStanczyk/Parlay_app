from app.models.bet_event import BetEvent
from app.models.sport import Sport
from app.models.league import League
from app.models.user import User
from app.models.bet_recommendation import BetRecommendation
from app.models.tipster import Tipster
from app.models.tipster_tier import TipsterTier
from app.models.tipster_ranges import TipsterRange
from app.models.tipster_main_stats import TipsterMainStats
from app.models.tipster_tier_stats import TipsterTierStats
from app.models.tipster_main_range_stats import TipsterMainRangeStats
from app.models.tipster_tiers_range_stats import TipsterTiersRangeStats
from app.models.game import Game
from app.models.subscription_plan import SubscriptionPlan
from app.models.user_subscription import UserSubscription
from app.models.subscription_payment import SubscriptionPayment
from app.models.user_tipster_follow import UserTipsterFollow
from app.models.coupon import Coupon
from app.models.bet_event_on_coupon import BetEventOnCoupon
from app.models.philip_snat_sport import PhilipSnatSport
from app.models.philip_snat_prediction_file import PhilipSnatPredictionFile
from app.models.philip_snat_nhl_game import PhilipSnatNhlGame
from app.models.philip_snat_league import PhilipSnatLeague
from app.models.philip_snat_ai_model import PhilipSnatAiModel

__all__ = [
    "BetEvent",
    "Sport",
    "League",
    "User",
    "BetRecommendation",
    "Tipster",
    "TipsterTier",
    "TipsterRange",
    "TipsterMainStats",
    "TipsterTierStats",
    "TipsterMainRangeStats",
    "TipsterTiersRangeStats",
    "Game",
    "SubscriptionPlan",
    "UserSubscription",
    "SubscriptionPayment",
    "UserTipsterFollow",
    "Coupon",
    "BetEventOnCoupon",
    "PhilipSnatSport",
    "PhilipSnatPredictionFile",
    "PhilipSnatNhlGame",
    "PhilipSnatLeague",
    "PhilipSnatAiModel",
]
