import React, { useEffect, useState } from 'react';
import { FaCheckCircle, FaHeart, FaLightbulb, FaUsers } from 'react-icons/fa';
import { useParams } from 'react-router-dom';
import Flag from 'react-world-flags';
import ExpertPickPanel from '../../components/ExpertPickPanel';
import { followApi } from '../../services/followService';
import { BetRecommendation, tipsterApi } from '../../services/tipsterService';
import '../../styles/expert-profile.scss';
import { TipsterPublic } from '../../types/interfaces';

type Tab = 'current' | 'resolved';

const ExpertProfile: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [tipster, setTipster] = useState<TipsterPublic | null>(null);
  const [recommendations, setRecommendations] = useState<BetRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('current');

  useEffect(() => {
    if (id) {
      const tipsterId = parseInt(id);
      Promise.all([
        tipsterApi.getById(tipsterId),
        tipsterApi.getRecommendations(tipsterId),
        followApi.getFollowedIds().catch(() => [] as number[]),
      ])
        .then(([tipsterData, recommendationsData, followedIds]) => {
          setTipster(tipsterData);
          setRecommendations(recommendationsData);
          setIsFollowing(followedIds.includes(tipsterId));
          setLoading(false);
        })
        .catch(() => {
          setLoading(false);
        });
    }
  }, [id]);

  const isUnresolved = (result?: string) =>
    !result || result === 'TO_RESOLVE' || result === 'UNKNOWN';

  const ongoingPicks = recommendations.filter((rec) => {
    const result = rec.bet_event?.result;
    const isPast = rec.bet_event?.game?.datetime
      ? new Date(rec.bet_event.game.datetime) <= new Date()
      : false;
    return isUnresolved(result) && isPast;
  });

  const upcomingPicks = recommendations.filter((rec) => {
    const result = rec.bet_event?.result;
    const isFuture = rec.bet_event?.game?.datetime
      ? new Date(rec.bet_event.game.datetime) > new Date()
      : true;
    return isUnresolved(result) && isFuture;
  });

  const resolvedPicks = recommendations.filter((rec) => {
    const result = rec.bet_event?.result;
    const isPast = rec.bet_event?.game?.datetime
      ? new Date(rec.bet_event.game.datetime) <= new Date()
      : false;
    return result && result !== 'TO_RESOLVE' && result !== 'UNKNOWN' && isPast;
  });

  const handleToggleFollow = async () => {
    if (!tipster || followLoading) return;
    setFollowLoading(true);
    try {
      if (isFollowing) {
        await followApi.unfollow(tipster.id);
        setIsFollowing(false);
        setTipster(prev => prev ? { ...prev, followers_count: prev.followers_count - 1 } : prev);
      } else {
        await followApi.follow(tipster.id);
        setIsFollowing(true);
        setTipster(prev => prev ? { ...prev, followers_count: prev.followers_count + 1 } : prev);
      }
    } catch {
      // silently fail
    } finally {
      setFollowLoading(false);
    }
  };

  if (loading) {
    return <div className="expert-profile">Loading...</div>;
  }

  if (!tipster) {
    return <div className="expert-profile">Expert not found</div>;
  }

  const tags = [tipster.tag_1, tipster.tag_2, tipster.tag_3].filter(Boolean) as string[];

  const now = new Date();
  const date = now.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
  });
  const time = now
    .toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
    .replace(' AM', 'am')
    .replace(' PM', 'pm');
  const lastUploadLabel = `${date} ${time}`;

  return (
    <section className="card expert-profile">
      <div className="expert-profile__top">
        <div className="expert-profile__identity">
          <h1 className="expert-profile__identity__name">
            {tipster.full_name}
            {tipster.is_verified && (
              <FaCheckCircle className="expert-profile__verified" />
            )}
          </h1>
          {tags.length > 0 && (
            <div className="expert-profile__identity__tags">| {tags.join(', ')}</div>
          )}
          {tipster.country && (
            <div className="expert-profile__identity__flag">
              <Flag code={tipster.country} />
            </div>
          )}
        </div>

        <div className="expert-profile__actions">
          <p className="expert-profile__last-upload">
            last upload: {lastUploadLabel}
          </p>
          <button
            className="button_primary expert-profile__action-button"
            onClick={handleToggleFollow}
            disabled={followLoading}
          >
            {isFollowing ? 'Unfollow' : 'Follow'}
          </button>
          <button className="button_primary expert-profile__action-button">Stats</button>
        </div>
      </div>

      <div className="expert-profile__metrics">
        <div className="expert-profile__metric">
          <span className="expert-profile__metric-label">
            Followers {tipster.followers_count}
          </span>
          <FaHeart className="expert-profile__metric-icon" />
        </div>

        <div className="expert-profile__metric">
          <span className="expert-profile__metric-label">
            Current picks {tipster.recommendations_count}
          </span>
          <FaLightbulb className="expert-profile__metric-icon" />
        </div>

        <div className="expert-profile__metric">
          <span className="expert-profile__metric-label">
            Appreciation {tipster.appreciation}
          </span>
          <FaUsers className="expert-profile__metric-icon" />
        </div>
      </div>

      {tipster.description && (
        <p className="expert-profile__description">{tipster.description}</p>
      )}

      {!tipster.description && (
        <p className="expert-profile__description">
          High risk high reward type plays. I got 43% ROI/year. Check my NFL bets for the best parlays.
        </p>
      )}

      <div className="expert-profile__tabs">
        <button
          className={`expert-profile__tab ${activeTab === 'current' ? 'expert-profile__tab--active' : ''}`}
          onClick={() => setActiveTab('current')}
        >
          Current picks
          {(ongoingPicks.length + upcomingPicks.length) > 0 && (
            <span className="expert-profile__tab-count">{ongoingPicks.length + upcomingPicks.length}</span>
          )}
        </button>
        <button
          className={`expert-profile__tab ${activeTab === 'resolved' ? 'expert-profile__tab--active' : ''}`}
          onClick={() => setActiveTab('resolved')}
        >
          Resolved picks
          {resolvedPicks.length > 0 && (
            <span className="expert-profile__tab-count">{resolvedPicks.length}</span>
          )}
        </button>
      </div>

      {activeTab === 'current' && (
        <section className="expert-profile__picks">
          {ongoingPicks.length === 0 && upcomingPicks.length === 0 ? (
            <div className="expert-profile__picks-empty">No active picks at the moment</div>
          ) : (
            <div className="expert-profile__picks-list">
              {ongoingPicks.map((rec) => (
                <ExpertPickPanel key={rec.id} recommendation={rec} ongoing />
              ))}
              {upcomingPicks.map((rec) => (
                <ExpertPickPanel key={rec.id} recommendation={rec} />
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === 'resolved' && (
        <section className="expert-profile__picks">
          {resolvedPicks.length === 0 ? (
            <div className="expert-profile__picks-empty">No resolved picks yet</div>
          ) : (
            <div className="expert-profile__picks-list">
              {resolvedPicks.map((rec) => (
                <ExpertPickPanel key={rec.id} recommendation={rec} resolved />
              ))}
            </div>
          )}
        </section>
      )}
    </section>
  );
};

export default ExpertProfile;
