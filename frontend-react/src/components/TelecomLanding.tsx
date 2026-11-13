import React from 'react';
import {
  Smartphone,
  Gamepad2,
  Watch,
  Camera,
  MessageSquare,
  ShieldCheck,
  Clock,
  RefreshCw,
  ArrowRight,
  ArrowLeft,
} from 'lucide-react';
import { CATALOG_CARDS, LABELS, Language } from '../data/appData';

interface TelecomLandingProps {
  lang: Language;
  onSelectSample: (sampleQuery: string, openUpload?: boolean) => void;
}

export default function TelecomLanding({ lang, onSelectSample }: TelecomLandingProps) {
  const text = LABELS[lang];
  const isRtl = lang === 'ar';
  const ArrowIcon = isRtl ? ArrowLeft : ArrowRight;

  const getCategoryIcon = (category: 'smartphones' | 'gaming' | 'gadgets') => {
    if (category === 'smartphones') return <Smartphone className="w-5 h-5 text-qatar-maroon dark:text-qatar-gold" />;
    if (category === 'gaming') return <Gamepad2 className="w-5 h-5 text-qatar-maroon dark:text-qatar-gold" />;
    return <Watch className="w-5 h-5 text-qatar-maroon dark:text-qatar-gold" />;
  };

  return (
    <main dir={isRtl ? 'rtl' : 'ltr'} className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-10">
      {/* Clean Hero Section */}
      <section className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 sm:p-10 shadow-sm">
        <div className="max-w-3xl space-y-4">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-qatar-maroon/10 text-qatar-maroon dark:bg-qatar-gold/15 dark:text-qatar-gold">
            {text.heroBadge}
          </span>

          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
            {text.heroTitle}
          </h1>

          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
            {text.heroSub}
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onSelectSample('', false)}
              className="px-5 py-2.5 rounded-xl bg-qatar-maroon hover:opacity-95 text-white text-xs sm:text-sm font-bold flex items-center gap-2 shadow-sm transition"
            >
              <MessageSquare className="w-4 h-4 text-qatar-gold" />
              <span>{text.heroPrimaryBtn}</span>
            </button>

            <button
              onClick={() => onSelectSample('', true)}
              className="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 text-xs sm:text-sm font-bold flex items-center gap-2 border border-slate-200 dark:border-slate-700 transition"
            >
              <Camera className="w-4 h-4 text-qatar-maroon dark:text-qatar-gold" />
              <span>{text.heroSecondaryBtn}</span>
            </button>
          </div>
        </div>
      </section>

      {/* Catalog & Repair Triage Cards */}
      <section className="space-y-4">
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white">
            {text.sectionTitle}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            {text.sectionSub}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {CATALOG_CARDS.map((card) => (
            <div
              key={card.id}
              className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 flex flex-col justify-between space-y-4 hover:border-qatar-maroon/40 transition"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800">
                    {getCategoryIcon(card.category)}
                  </span>
                  <span className="text-[11px] font-semibold text-qatar-maroon dark:text-qatar-gold">
                    {isRtl ? card.badgeAr : card.badgeEn}
                  </span>
                </div>

                <h3 className="font-bold text-base text-slate-900 dark:text-white">
                  {isRtl ? card.titleAr : card.titleEn}
                </h3>

                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  {isRtl ? card.subtitleAr : card.subtitleEn}
                </p>
              </div>

              <button
                onClick={() =>
                  onSelectSample(isRtl ? card.sampleQueryAr : card.sampleQueryEn, false)
                }
                className="w-full py-2 px-3 rounded-xl bg-slate-50 hover:bg-qatar-maroon hover:text-white dark:bg-slate-800 dark:hover:bg-qatar-maroon text-slate-800 dark:text-slate-100 text-xs font-bold flex items-center justify-between border border-slate-200 dark:border-slate-700 transition"
              >
                <span>{text.tryPromptBtn}</span>
                <ArrowIcon className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Qatar Consumer Protection SLA Strip */}
      <section className="rounded-2xl bg-slate-100/80 dark:bg-slate-900/70 border border-slate-200 dark:border-slate-800 p-5 sm:p-6 space-y-4">
        <h2 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white">
          {text.slaTitle}
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-start gap-3">
            <ShieldCheck className="w-5 h-5 text-qatar-maroon dark:text-qatar-gold flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">{text.sla1Title}</div>
              <div className="text-xs text-slate-600 dark:text-slate-400">{text.sla1Desc}</div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-qatar-maroon dark:text-qatar-gold flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">{text.sla2Title}</div>
              <div className="text-xs text-slate-600 dark:text-slate-400">{text.sla2Desc}</div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <RefreshCw className="w-5 h-5 text-qatar-maroon dark:text-qatar-gold flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">{text.sla3Title}</div>
              <div className="text-xs text-slate-600 dark:text-slate-400">{text.sla3Desc}</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}