import React, { useEffect, useState } from 'react';
import ExpertSearchRow from '../../components/searchExpertsComponents/ExpertSearchRow';
import { tipsterApi, TipsterFilters } from '../../services/tipsterService';
import { followApi } from '../../services/followService';
import { TipsterPublic } from '../../types/interfaces';

const SearchExperts: React.FC = () => {
  const [tipsters, setTipsters] = useState<TipsterPublic[]>([]);
  const [followedIds, setFollowedIds] = useState<Set<number>>(new Set());
  const [filters, setFilters] = useState<TipsterFilters>({
    followingOnly: false,
    tagSearch: '',
    sortBy: 'followers',
  });
  const [tagInput, setTagInput] = useState('');

  const fetchTipsters = async () => {
    try {
      const [tipstersData, ids] = await Promise.all([
        tipsterApi.getAll(filters),
        followApi.getFollowedIds().catch(() => [] as number[]),
      ]);
      setTipsters(tipstersData);
      setFollowedIds(new Set(ids));
    } catch (error) {
      console.error('Failed to fetch tipsters:', error);
    }
  };

  useEffect(() => {
    fetchTipsters();
  }, [filters]);

  const handleToggleFollow = async (tipsterId: number, currentlyFollowing: boolean) => {
    try {
      if (currentlyFollowing) {
        await followApi.unfollow(tipsterId);
        setFollowedIds(prev => {
          const next = new Set(prev);
          next.delete(tipsterId);
          return next;
        });
        setTipsters(prev =>
          prev.map(t => t.id === tipsterId ? { ...t, followers_count: t.followers_count - 1 } : t)
        );
      } else {
        await followApi.follow(tipsterId);
        setFollowedIds(prev => new Set(prev).add(tipsterId));
        setTipsters(prev =>
          prev.map(t => t.id === tipsterId ? { ...t, followers_count: t.followers_count + 1 } : t)
        );
      }
    } catch {
      // silently fail
    }
  };

  const handleTagSearch = () => {
    setFilters(prev => ({ ...prev, tagSearch: tagInput }));
  };

  const handleTagKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleTagSearch();
    }
  };

  return (
    <div className="search-experts">
      <h1 className='italic-title'>Search Experts</h1>

      <div className="search-experts__filters card">
        <div className="search-experts__filter-group">
          <label className="search-experts__filter-label">
            <input
              type="checkbox"
              checked={filters.followingOnly}
              onChange={(e) => setFilters(prev => ({ ...prev, followingOnly: e.target.checked }))}
            />
            <span>Following Only</span>
          </label>
        </div>

        <div className="search-experts__filter-group search-experts__filter-group--tag">
          <input
            type="text"
            placeholder="Search by tag (e.g., NBA)"
            className="search-experts__tag-input"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyPress={handleTagKeyPress}
          />
          <button
            className="button_primary search-experts__tag-button"
            onClick={handleTagSearch}
          >
            Search
          </button>
        </div>

        <div className="search-experts__filter-group">
          <label className="search-experts__filter-label">Sort by:</label>
          <select
            className="search-experts__sort-select"
            value={filters.sortBy}
            onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value as TipsterFilters['sortBy'] }))}
          >
            <option value="followers">Followers</option>
            <option value="appreciation">Appreciation</option>
            <option value="recommendations">Current Picks</option>
          </select>
        </div>
      </div>

      {tipsters.map((tipster) => (
        <ExpertSearchRow
          key={tipster.id}
          tipster={tipster}
          isFollowing={followedIds.has(tipster.id)}
          onToggleFollow={handleToggleFollow}
        />
      ))}
    </div>
  );
};

export default SearchExperts;
