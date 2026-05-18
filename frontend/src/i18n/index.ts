import { createI18n } from 'vue-i18n';
import en from '@/locales/en.json';
import ru from '@/locales/ru.json';

export type SupportedLocale = 'en' | 'ru';
export const SUPPORTED_LOCALES: { value: SupportedLocale; label: string }[] = [
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Русский' },
];

const savedLocale = localStorage.getItem('locale') as SupportedLocale | null;
const browserLocale = navigator.language.split('-')[0] as SupportedLocale;
const defaultLocale: SupportedLocale =
  savedLocale ||
  (SUPPORTED_LOCALES.some((l) => l.value === browserLocale) ? browserLocale : 'en');

export const i18n = createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    ru,
  },
});

export function setLocale(locale: SupportedLocale) {
  i18n.global.locale.value = locale;
  localStorage.setItem('locale', locale);
  document.documentElement.lang = locale;
}

export function getCurrentLocale(): SupportedLocale {
  return i18n.global.locale.value as SupportedLocale;
}
