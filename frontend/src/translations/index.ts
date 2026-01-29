import { en } from './en';
import { pl } from './pl';

export type Language = 'en' | 'pl';

export type TranslationKeys = typeof en;

const deepMerge = <T extends Record<string, any>>(target: T, source: Partial<T> & Record<string, any>): T => {
  const result = { ...target } as T;
  for (const key in source) {
    if (source.hasOwnProperty(key)) {
      const sourceValue = source[key];
      if (sourceValue && typeof sourceValue === 'object' && !Array.isArray(sourceValue)) {
        (result as any)[key] = deepMerge((result as any)[key] || {}, sourceValue);
      } else if (sourceValue !== undefined) {
        (result as any)[key] = sourceValue;
      }
    }
  }
  return result;
};

export const translations = {
  en,
  pl: deepMerge(en, pl as unknown as Partial<typeof en>),
} as const;

export const defaultLanguage: Language = 'en';

export const availableLanguages: Language[] = ['en'];
