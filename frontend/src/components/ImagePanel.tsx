import React from 'react';

interface ImagePanelProps {
  path: string;
}

const ImagePanel: React.FC<ImagePanelProps> = ({ path }) => (
  <div className="image-panel">
    <img className="image-panel__image" src={path} alt="" />
  </div>
);

export default ImagePanel;
