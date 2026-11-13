import React from 'react';
import { Cpu, Moon, Sun } from 'lucide-react';
import { LABELS, Language } from '../data/appData';

interface HeaderBarProps {
  lang: Language;
  setLang: (lang: Language) => void;
  darkMode: boolean;
  setDarkMode: (dark: boolean) => void;
}

export default function HeaderBar({
  lang,
  setLang,
  darkMode,
  setDarkMode,
}: HeaderBarProps) {
  const text = LABELS[lang];
  const isRtl = lang === 'ar';

  return (
    <header
      dir={isRtl ? 'rtl' : 'ltr'}
      className="sticky top-0 z-40 bg-qatar-maroon text-white shadow-md border-b border-qatar-gold/25"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Brand Identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-qatar-gold text-qatar-maroon flex items-center justify-center shadow-sm flex-shrink-0">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm sm:text-base tracking-tight">
                {text.brandName}
              </span>
              <span className="px-2 py-0.5 rounded-full bg-qatar-gold text-qatar-maroon text-[10px] font-extrabold tracking-wide uppercase">
                {isRtl ? 'أجهزة وصيانة' : 'DEVICES & REPAIR'}
              </span>
            </div>
            <div className="text-[10px] text-qatar-gold/90 font-medium tracking-wider">
              {text.brandTag}
            </div>
          </div>
        </div>

        {/* Language & Theme Controls */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-black/25 p-1 rounded-xl border border-white/10 text-xs font-bold">
            <button
              type="button"
              onClick={() => setLang('en')}
              className={`px-2.5 py-1 rounded-lg transition ${
                lang === 'en'
                  ? 'bg-qatar-gold text-qatar-maroon shadow-sm'
                  : 'text-white/80 hover:text-white'
              }`}
            >
              EN
            </button>
            <button
              type="button"
              onClick={() => setLang('ar')}
              className={`px-2.5 py-1 rounded-lg transition ${
                lang === 'ar'
                  ? 'bg-qatar-gold text-qatar-maroon shadow-sm'
                  : 'text-white/80 hover:text-white'
              }`}
            >
              عربي
            </button>
          </div>

          <button
            type="button"
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle Dark Mode"
            className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-qatar-gold transition"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}