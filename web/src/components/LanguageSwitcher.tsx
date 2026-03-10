import React from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageSwitcher.css';

export const LanguageSwitcher: React.FC = () => {
  const { i18n } = useTranslation();
  
  const languages = [
    { code: 'zh-CN', label: '中文', flag: '🇨🇳' },
    { code: 'en-US', label: 'English', flag: '🇺🇸' }
  ];
  
  const currentLanguage = languages.find(lang => lang.code === i18n.language) || languages[0];
  
  const handleLanguageChange = (langCode: string) => {
    i18n.changeLanguage(langCode);
  };
  
  return (
    <div className="language-switcher">
      <button className="language-button">
        <span className="language-flag">{currentLanguage.flag}</span>
        <span className="language-label">{currentLanguage.label}</span>
        <span className="language-arrow">▼</span>
      </button>
      
      <div className="language-dropdown">
        {languages.map((lang) => (
          <button
            key={lang.code}
            className={`language-option ${i18n.language === lang.code ? 'active' : ''}`}
            onClick={() => handleLanguageChange(lang.code)}
          >
            <span className="language-flag">{lang.flag}</span>
            <span className="language-label">{lang.label}</span>
            {i18n.language === lang.code && <span className="language-check">✓</span>}
          </button>
        ))}
      </div>
    </div>
  );
};
