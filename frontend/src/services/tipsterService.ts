import { TipsterPublic } from '../types/interfaces';
import { publicApiGet } from '../utils/api';

export const tipsterApi = {
  getAll: (): Promise<TipsterPublic[]> => {
    return publicApiGet<TipsterPublic[]>('/tipsters/');
  },
};
