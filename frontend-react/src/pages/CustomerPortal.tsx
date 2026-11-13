import React, { useState, useEffect } from 'react';
import HeaderBar from '../components/HeaderBar';
import TelecomLanding from '../components/TelecomLanding';
import ChatWidget, { AttachedImage } from '../components/ChatWidget';
import { Language } from '../data/appData';

export default function CustomerPortal() {
  const [lang, setLang] = useState<Language>('en');
  const [darkMode, setDarkMode] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [attachments, setAttachments] = useState<AttachedImage[]>([]);
  const [triggerUploadCount, setTriggerUploadCount] = useState(0);

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [darkMode]);

  const handleSelectSample = (sampleQuery: string, openUpload: boolean = false) => {
    if (sampleQuery) {
      setQuery(sampleQuery);
    }
    setIsChatOpen(true);
    if (openUpload) {
      setTriggerUploadCount((c) => c + 1);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      <HeaderBar
        lang={lang}
        setLang={setLang}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        onOpenChat={() => setIsChatOpen(true)}
      />

      <TelecomLanding
        lang={lang}
        onSelectSample={handleSelectSample}
      />

      <ChatWidget
        lang={lang}
        isOpen={isChatOpen}
        setIsOpen={setIsChatOpen}
        query={query}
        setQuery={setQuery}
        attachments={attachments}
        setAttachments={setAttachments}
        triggerUploadCount={triggerUploadCount}
      />
    </div>
  );
}