import React from 'react';
import { FaCheckCircle, FaHeart, FaLightbulb, FaUsers } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import Flag from 'react-world-flags';
import { TipsterPublic } from '../../types/interfaces';

interface ExpertSearchRowProps {
  tipster: TipsterPublic;
  isFollowing: boolean;
  onToggleFollow: (tipsterId: number, currentlyFollowing: boolean) => void;
}

const ExpertSearchRow: React.FC<ExpertSearchRowProps> = ({ tipster, isFollowing, onToggleFollow }) => {
  const navigate = useNavigate();

  const handleViewProfile = () => {
    navigate(`/experts/${tipster.id}`);
  };

  return (
    <div className='card expert-list-row'>
      <div className='expert-list-row__left'>
        <div className='expert-list-row__left__country'>
          {tipster.country && <Flag code={tipster.country} />}
        </div>
        <div className='expert-list-row__left__top'>

          <div className='expert-list-row__left__top__name' onClick={handleViewProfile} style={{ cursor: 'pointer' }}>
            {tipster.full_name}
            {tipster.is_verified &&
              <FaCheckCircle />
            }
          </div>
          <div className='expert-list-row__left__top__tags'>
            | {tipster.tag_1} | {tipster.tag_2} | {tipster.tag_3}
          </div>
        </div>
        <div className='expert-list-row__left__bottom'>
          <div className='expert-list-row__right__appreciation'>
            <FaHeart /> {tipster.appreciation}
          </div>
          <div className='expert-list-row__right__followers'>
            <FaUsers /> {tipster.followers_count}
          </div>
          <div className='expert-list-row__right__recommendations'>
            <FaLightbulb /> {tipster.recommendations_count}
          </div>
        </div>

      </div>
      <div className='expert-list-row__right'>

        <button
          className='button_primary button_list_row'
          onClick={() => onToggleFollow(tipster.id, isFollowing)}
        >
          {isFollowing ? 'Unfollow' : 'Follow'}
        </button>
        <button className='button_primary button_list_row' onClick={handleViewProfile}>View Profile</button>
      </div>
    </div>
  );
};

export default ExpertSearchRow;
