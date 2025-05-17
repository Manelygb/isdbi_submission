import React from 'react';
import item_bg from '../../assets/bg_image.svg';
import './ch4.css';

function PurpleCard({ onClick , title , desc }) {
  return (
    <div className="bg_purple" onClick={onClick} style={{ cursor: 'pointer' }}>
      <img src={item_bg} alt="" className="background-img" />
      <div className="text-content">
        <p className="top-text">
          {title}
        </p>
        <p className="bottom-text">
        {desc}
        </p>
      </div>
      <button className="action-btn">
        Run Flow Now
      </button>
    </div>
  );
}

export default PurpleCard;
