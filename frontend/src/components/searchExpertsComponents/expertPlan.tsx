import React from 'react';
import { FaCheckCircle, FaHeart, FaLightbulb, FaUsers } from 'react-icons/fa';
import Flag from 'react-world-flags';
import { TipsterPublic } from '../../types/interfaces';

interface ExpertPlanProps {
  tipster: TipsterPublic;
}

const ExpertListRow: React.FC<ExpertPlanProps> = ({ tipster }) => {
  return (
    <div className='expert-list-row'>
      <div className='expert-list-row__left'>
        <div className='expert-list-row__left__name'>
          {tipster.full_name}
        </div>
        {!tipster.is_verified &&
          <div className='expert-list-row__left__is_verified'>
          <FaCheckCircle />
          </div>
        }
        <div className='expert-list-row__left__country'>
          {tipster.country && <Flag code={tipster.country} />}
        </div>
      </div>
      <div className='expert-list-row__right'>
        <div className='expert-list-row__right__appreciation'>
          <FaHeart /> {tipster.appreciation}
        </div>
        <div className='expert-list-row__right__followers'>
          <FaUsers /> {tipster.followers_count}
        </div>
        <div className='expert-list-row__right__recommendations'>
          <FaLightbulb /> {tipster.recommendations_count}
        </div>
        <button className='button_list_row'>Follow</button>
        <button className='button_list_row'>View Profile</button>
      </div>
    </div>
  );
};

export default ExpertListRow;
