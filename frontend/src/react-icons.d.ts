declare module 'react-icons/fi' {
  import { FC, SVGProps } from 'react';

  export const FiMenu: FC<SVGProps<SVGSVGElement>>;
  export const FiX: FC<SVGProps<SVGSVGElement>>;
  export const FiLock: FC<SVGProps<SVGSVGElement>>;
  export const FiUnlock: FC<SVGProps<SVGSVGElement>>;
  export const FiChevronDown: FC<SVGProps<SVGSVGElement>>;
  export const FiChevronUp: FC<SVGProps<SVGSVGElement>>;
  export const FiChevronRight: FC<SVGProps<SVGSVGElement>>;
  export const FiClock: FC<SVGProps<SVGSVGElement>>;
  export const FiShuffle: FC<SVGProps<SVGSVGElement>>;
}

declare module 'react-icons/fa6' {
  import { FC, SVGProps } from 'react';

  export const FaFileLines: FC<SVGProps<SVGSVGElement>>;
  export const FaUsers: FC<SVGProps<SVGSVGElement>>;
  export const FaChartLine: FC<SVGProps<SVGSVGElement>>;
  export const FaDollarSign: FC<SVGProps<SVGSVGElement>>;
}

declare module 'react-icons/fa' {
  import { FC, SVGProps } from 'react';

  export const FaHeart: FC<SVGProps<SVGSVGElement>>;
  export const FaUsers: FC<SVGProps<SVGSVGElement>>;
  export const FaLightbulb: FC<SVGProps<SVGSVGElement>>;
  export const FaCheckCircle: FC<SVGProps<SVGSVGElement>>;
  export const FaTimesCircle: FC<SVGProps<SVGSVGElement>>;
}

declare module 'react-world-flags' {
  import { FC } from 'react';

  interface FlagProps {
    code: string;
    style?: React.CSSProperties;
    className?: string;
    height?: number | string;
    width?: number | string;
    fallback?: React.ReactNode;
  }

  const Flag: FC<FlagProps>;
  export default Flag;
}
