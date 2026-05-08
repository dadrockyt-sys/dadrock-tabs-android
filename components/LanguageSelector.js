'use client';

import { useState, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { Globe, ChevronDown } from 'lucide-react';
import { locales, localeNames, localeFlags } from '@/lib/i18n';

const LANG_STORAGE_KEY = 'dadrock_language';

// Hook to use language across any component
export function useLanguage() {
  const [lang, setLang] = useState('en');

  useEffect(() => {
    const stored = localStorage.getItem(LANG_STORAGE_KEY);
    if (stored && locales.includes(stored)) {
      setLang(stored);
    }
  }, []);

  const changeLang = useCallback((newLang) => {
    setLang(newLang);
    localStorage.setItem(LANG_STORAGE_KEY, newLang);
    // Dispatch custom event so all LanguageSelector instances + pages update
    window.dispatchEvent(new CustomEvent('dadrock-lang-change', { detail: newLang }));
  }, []);

  useEffect(() => {
    const handler = (e) => {
      if (e.detail && locales.includes(e.detail)) {
        setLang(e.detail);
      }
    };
    window.addEventListener('dadrock-lang-change', handler);
    return () => window.removeEventListener('dadrock-lang-change', handler);
  }, []);

  return [lang, changeLang];
}

export default function LanguageSelector({ onLanguageChange }) {
  const [lang, changeLang] = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLanguageChange = (newLang) => {
    setIsOpen(false);
    changeLang(newLang);
    if (onLanguageChange) {
      onLanguageChange(newLang);
    }
  };

  // Modal content to be portaled to body
  const modalContent = isOpen && mounted ? createPortal(
    <div 
      style={{ 
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 99999,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '60px',
        backgroundColor: 'rgba(0,0,0,0.95)'
      }}
    >
      {/* Dark backdrop - click to close */}
      <div 
        style={{ 
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
        }}
        onClick={() => setIsOpen(false)}
      />
      
      {/* Language menu card */}
      <div 
        style={{ 
          position: 'relative',
          width: '320px',
          maxWidth: '90vw',
          maxHeight: '80vh',
          overflowY: 'auto',
          borderRadius: '16px',
          backgroundColor: '#262626',
          border: '2px solid #525252',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 1)'
        }}
      >
        {/* Header */}
        <div 
          style={{ 
            position: 'sticky',
            top: 0,
            padding: '16px',
            backgroundColor: '#262626',
            borderBottom: '1px solid #525252',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            zIndex: 1,
          }}
        >
          <span style={{ color: '#ffffff', fontWeight: 'bold', fontSize: '18px' }}>Select Language</span>
          <button 
            onClick={() => setIsOpen(false)}
            style={{
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '50%',
              backgroundColor: '#404040',
              color: '#ffffff',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>
        
        {/* Language options */}
        <div style={{ backgroundColor: '#262626' }}>
          {locales.map((locale) => (
            <button
              key={locale}
              onClick={() => handleLanguageChange(locale)}
              style={{ 
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '16px',
                fontSize: '16px',
                backgroundColor: locale === lang ? '#4a4a00' : '#262626',
                color: locale === lang ? '#fbbf24' : '#e4e4e7',
                borderBottom: '1px solid #404040',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <span style={{ fontSize: '24px' }}>{localeFlags[locale]}</span>
              <span style={{ flex: 1, fontWeight: '500' }}>{localeNames[locale]}</span>
              {locale === lang && <span style={{ color: '#fbbf24', fontWeight: 'bold', fontSize: '20px' }}>✓</span>}
            </button>
          ))}
        </div>
      </div>
    </div>,
    document.body
  ) : null;

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-sm font-medium text-zinc-300 hover:text-white bg-zinc-800/80 hover:bg-zinc-700 rounded-md transition-all border border-zinc-700/50"
      >
        <Globe className="w-4 h-4" />
        <span>{localeFlags[lang]}</span>
        <span className="text-xs uppercase">{lang}</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {modalContent}
    </>
  );
}
