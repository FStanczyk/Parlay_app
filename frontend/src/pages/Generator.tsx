import React from 'react';
import GeneratorComponent from '../components/Generator';

const Generator: React.FC = () => {
  return <GeneratorComponent isDemo={false} defaultEvents={4} />;
};

export default Generator;
