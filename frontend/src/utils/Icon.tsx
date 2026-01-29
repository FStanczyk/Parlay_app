import React from 'react';

export const Icon: React.FC<{
  component: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  className?: string;
  'aria-hidden'?: boolean;
}> = ({ component: Component, className, 'aria-hidden': ariaHidden }) => {
  return <Component className={className} aria-hidden={ariaHidden} />;
};
