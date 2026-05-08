// Dynamic SEO meta tag translations for all subpages
// These update document.title, meta description, and OG tags client-side when language changes

const seoTranslations = {
  en: {
    quickies: {
      title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons | DadRock Tabs',
      description: 'Quick guitar and bass tab lessons from DadRock Tabs. Short, focused tutorials that get you playing classic rock and heavy metal riffs fast.',
    },
    comingSoon: {
      title: 'Upcoming Guitar Lessons Coming Soon | DadRock Tabs',
      description: 'See the upcoming guitar and bass tab lessons at DadRock Tabs. New classic rock, heavy metal, and hair metal tutorials added regularly.',
    },
    topLessons: {
      title: 'Top 10 Most Viewed Guitar Lessons | DadRock Tabs',
      description: 'Discover the most popular guitar and bass tab video lessons at DadRock Tabs. Our top 10 most-watched tutorials.',
    },
    artist: {
      title: '{artist} Guitar & Bass Tabs | DadRock Tabs',
      description: 'Learn to play {artist} songs with free guitar and bass tab video lessons from DadRock Tabs.',
    },
    song: {
      title: '{song} by {artist} - Guitar & Bass Tab | DadRock Tabs',
      description: 'Learn to play {song} by {artist} with free guitar and bass tab video lessons from DadRock Tabs.',
    },
  },
  es: {
    quickies: {
      title: 'DadRock Tabs Quickies - Lecciones Rápidas de Guitarra y Bajo | DadRock Tabs',
      description: 'Lecciones rápidas de tablatura de guitarra y bajo de DadRock Tabs. Tutoriales cortos y enfocados para tocar riffs de rock clásico y heavy metal.',
    },
    comingSoon: {
      title: 'Próximas Lecciones de Guitarra | DadRock Tabs',
      description: 'Descubre las próximas lecciones de guitarra y bajo en DadRock Tabs. Nuevos tutoriales de rock clásico y heavy metal.',
    },
    topLessons: {
      title: 'Top 10 Lecciones de Guitarra Más Vistas | DadRock Tabs',
      description: 'Descubre las lecciones de guitarra y bajo más populares en DadRock Tabs. Nuestros 10 tutoriales más vistos.',
    },
    artist: {
      title: '{artist} Tablaturas de Guitarra y Bajo | DadRock Tabs',
      description: 'Aprende a tocar canciones de {artist} con lecciones gratuitas de guitarra y bajo de DadRock Tabs.',
    },
    song: {
      title: '{song} de {artist} - Tablatura de Guitarra y Bajo | DadRock Tabs',
      description: 'Aprende a tocar {song} de {artist} con lecciones gratuitas de guitarra y bajo de DadRock Tabs.',
    },
  },
  pt: {
    quickies: {
      title: 'DadRock Tabs Quickies - Aulas Rápidas de Guitarra e Baixo | DadRock Tabs',
      description: 'Aulas rápidas de tablatura de guitarra e baixo do DadRock Tabs. Tutoriais curtos para tocar riffs de rock clássico e heavy metal.',
    },
    comingSoon: {
      title: 'Próximas Aulas de Guitarra | DadRock Tabs',
      description: 'Veja as próximas aulas de guitarra e baixo no DadRock Tabs. Novos tutoriais de rock clássico e heavy metal.',
    },
    topLessons: {
      title: 'Top 10 Aulas de Guitarra Mais Vistas | DadRock Tabs',
      description: 'Descubra as aulas de guitarra e baixo mais populares no DadRock Tabs.',
    },
    artist: {
      title: '{artist} Tablaturas de Guitarra e Baixo | DadRock Tabs',
      description: 'Aprenda a tocar músicas de {artist} com aulas gratuitas de guitarra e baixo do DadRock Tabs.',
    },
    song: {
      title: '{song} de {artist} - Tablatura de Guitarra e Baixo | DadRock Tabs',
      description: 'Aprenda a tocar {song} de {artist} com aulas gratuitas de guitarra e baixo do DadRock Tabs.',
    },
  },
  'pt-br': {
    quickies: {
      title: 'DadRock Tabs Quickies - Aulas Rápidas de Guitarra e Baixo | DadRock Tabs',
      description: 'Aulas rápidas de tablatura de guitarra e baixo do DadRock Tabs. Tutoriais curtos para tocar riffs de rock clássico e heavy metal.',
    },
    comingSoon: {
      title: 'Próximas Aulas de Guitarra | DadRock Tabs',
      description: 'Veja as próximas aulas de guitarra e baixo no DadRock Tabs. Novos tutoriais de rock clássico e heavy metal.',
    },
    topLessons: {
      title: 'Top 10 Aulas de Guitarra Mais Vistas | DadRock Tabs',
      description: 'Descubra as aulas de guitarra e baixo mais populares no DadRock Tabs.',
    },
    artist: {
      title: '{artist} Tablaturas de Guitarra e Baixo | DadRock Tabs',
      description: 'Aprenda a tocar músicas de {artist} com aulas gratuitas de guitarra e baixo do DadRock Tabs.',
    },
    song: {
      title: '{song} de {artist} - Tablatura de Guitarra e Baixo | DadRock Tabs',
      description: 'Aprenda a tocar {song} de {artist} com aulas gratuitas de guitarra e baixo do DadRock Tabs.',
    },
  },
  de: {
    quickies: {
      title: 'DadRock Tabs Quickies - Schnelle Gitarren- & Bass-Lektionen | DadRock Tabs',
      description: 'Schnelle Gitarren- und Bass-Tab-Lektionen von DadRock Tabs. Kurze Tutorials für Classic-Rock- und Heavy-Metal-Riffs.',
    },
    comingSoon: {
      title: 'Kommende Gitarrenlektionen | DadRock Tabs',
      description: 'Entdecken Sie die kommenden Gitarren- und Bass-Lektionen bei DadRock Tabs. Neue Classic-Rock- und Heavy-Metal-Tutorials.',
    },
    topLessons: {
      title: 'Top 10 Meistgesehene Gitarrenlektionen | DadRock Tabs',
      description: 'Entdecken Sie die beliebtesten Gitarren- und Bass-Tutorials auf DadRock Tabs.',
    },
    artist: {
      title: '{artist} Gitarren- & Bass-Tabs | DadRock Tabs',
      description: 'Lernen Sie {artist} Songs mit kostenlosen Gitarren- und Bass-Tab-Lektionen von DadRock Tabs.',
    },
    song: {
      title: '{song} von {artist} - Gitarren- & Bass-Tab | DadRock Tabs',
      description: 'Lernen Sie {song} von {artist} mit kostenlosen Gitarren- und Bass-Tab-Lektionen von DadRock Tabs.',
    },
  },
  fr: {
    quickies: {
      title: 'DadRock Tabs Quickies - Leçons Rapides de Guitare et Basse | DadRock Tabs',
      description: 'Leçons rapides de tablature guitare et basse de DadRock Tabs. Des tutoriels courts pour jouer des riffs de rock classique et heavy metal.',
    },
    comingSoon: {
      title: 'Prochaines Leçons de Guitare | DadRock Tabs',
      description: 'Découvrez les prochaines leçons de guitare et basse sur DadRock Tabs. Nouveaux tutoriels de rock classique et heavy metal.',
    },
    topLessons: {
      title: 'Top 10 des Leçons de Guitare les Plus Vues | DadRock Tabs',
      description: 'Découvrez les leçons de guitare et basse les plus populaires sur DadRock Tabs.',
    },
    artist: {
      title: 'Tablatures Guitare et Basse {artist} | DadRock Tabs',
      description: 'Apprenez à jouer les chansons de {artist} avec des leçons gratuites de guitare et basse de DadRock Tabs.',
    },
    song: {
      title: '{song} par {artist} - Tablature Guitare et Basse | DadRock Tabs',
      description: 'Apprenez à jouer {song} par {artist} avec des leçons gratuites de guitare et basse de DadRock Tabs.',
    },
  },
  it: {
    quickies: {
      title: 'DadRock Tabs Quickies - Lezioni Rapide di Chitarra e Basso | DadRock Tabs',
      description: 'Lezioni rapide di tablatura per chitarra e basso da DadRock Tabs. Tutorial brevi per suonare riff di rock classico e heavy metal.',
    },
    comingSoon: {
      title: 'Prossime Lezioni di Chitarra | DadRock Tabs',
      description: 'Scopri le prossime lezioni di chitarra e basso su DadRock Tabs. Nuovi tutorial di rock classico e heavy metal.',
    },
    topLessons: {
      title: 'Top 10 Lezioni di Chitarra Più Viste | DadRock Tabs',
      description: 'Scopri le lezioni di chitarra e basso più popolari su DadRock Tabs.',
    },
    artist: {
      title: 'Tablature Chitarra e Basso {artist} | DadRock Tabs',
      description: 'Impara a suonare le canzoni di {artist} con lezioni gratuite di chitarra e basso da DadRock Tabs.',
    },
    song: {
      title: '{song} di {artist} - Tablatura Chitarra e Basso | DadRock Tabs',
      description: 'Impara a suonare {song} di {artist} con lezioni gratuite di chitarra e basso da DadRock Tabs.',
    },
  },
  ja: {
    quickies: {
      title: 'DadRock Tabs クイッキー - クイックギター＆ベースレッスン | DadRock Tabs',
      description: 'DadRock Tabsのクイックギター＆ベースタブレッスン。クラシックロックやヘビーメタルのリフを素早く学べる短いチュートリアル。',
    },
    comingSoon: {
      title: '近日公開のギターレッスン | DadRock Tabs',
      description: 'DadRock Tabsの今後のギター＆ベースレッスンをチェック。クラシックロック、ヘビーメタルの新しいチュートリアル。',
    },
    topLessons: {
      title: 'トップ10人気ギターレッスン | DadRock Tabs',
      description: 'DadRock Tabsで最も人気のあるギター＆ベースタブチュートリアルを発見。',
    },
    artist: {
      title: '{artist} ギター＆ベースタブ | DadRock Tabs',
      description: 'DadRock Tabsの無料ギター＆ベースタブレッスンで{artist}の曲を弾こう。',
    },
    song: {
      title: '{song} - {artist} ギター＆ベースタブ | DadRock Tabs',
      description: 'DadRock Tabsの無料レッスンで{artist}の{song}を弾こう。',
    },
  },
  ko: {
    quickies: {
      title: 'DadRock Tabs Quickies - 빠른 기타 & 베이스 레슨 | DadRock Tabs',
      description: 'DadRock Tabs의 빠른 기타 및 베이스 탭 레슨. 클래식 록과 헤비 메탈 리프를 빠르게 배울 수 있는 짧은 튜토리얼.',
    },
    comingSoon: {
      title: '곧 공개될 기타 레슨 | DadRock Tabs',
      description: 'DadRock Tabs의 예정된 기타 및 베이스 레슨을 확인하세요. 클래식 록, 헤비 메탈 새 튜토리얼.',
    },
    topLessons: {
      title: '인기 기타 레슨 Top 10 | DadRock Tabs',
      description: 'DadRock Tabs에서 가장 인기 있는 기타 및 베이스 탭 튜토리얼을 발견하세요.',
    },
    artist: {
      title: '{artist} 기타 & 베이스 탭 | DadRock Tabs',
      description: 'DadRock Tabs의 무료 기타 및 베이스 탭 레슨으로 {artist} 곡을 배우세요.',
    },
    song: {
      title: '{song} - {artist} 기타 & 베이스 탭 | DadRock Tabs',
      description: 'DadRock Tabs의 무료 레슨으로 {artist}의 {song}을 배우세요.',
    },
  },
  zh: {
    quickies: {
      title: 'DadRock Tabs Quickies - 快速吉他和贝斯课程 | DadRock Tabs',
      description: 'DadRock Tabs的快速吉他和贝斯谱课程。短小精悍的教程，快速学习经典摇滚和重金属吉他即兴。',
    },
    comingSoon: {
      title: '即将推出的吉他课程 | DadRock Tabs',
      description: '查看DadRock Tabs即将推出的吉他和贝斯课程。经典摇滚、重金属新教程。',
    },
    topLessons: {
      title: '最受欢迎的10大吉他课程 | DadRock Tabs',
      description: '发现DadRock Tabs上最受欢迎的吉他和贝斯谱教程。',
    },
    artist: {
      title: '{artist} 吉他和贝斯谱 | DadRock Tabs',
      description: '用DadRock Tabs的免费吉他和贝斯谱课程学习{artist}的歌曲。',
    },
    song: {
      title: '{song} - {artist} 吉他和贝斯谱 | DadRock Tabs',
      description: '用DadRock Tabs的免费课程学习{artist}的{song}。',
    },
  },
  ru: {
    quickies: {
      title: 'DadRock Tabs Quickies - Быстрые Уроки Гитары и Баса | DadRock Tabs',
      description: 'Быстрые уроки по гитарным и басовым табам от DadRock Tabs. Короткие туториалы для изучения риффов классического рока и хэви-метала.',
    },
    comingSoon: {
      title: 'Предстоящие Уроки Гитары | DadRock Tabs',
      description: 'Узнайте о предстоящих уроках гитары и баса на DadRock Tabs. Новые туториалы по классическому року и хэви-металу.',
    },
    topLessons: {
      title: 'Топ-10 Самых Просматриваемых Уроков Гитары | DadRock Tabs',
      description: 'Откройте для себя самые популярные уроки по гитаре и басу на DadRock Tabs.',
    },
    artist: {
      title: 'Гитарные и Басовые Табы {artist} | DadRock Tabs',
      description: 'Научитесь играть песни {artist} с бесплатными уроками гитары и баса от DadRock Tabs.',
    },
    song: {
      title: '{song} - {artist} Гитарные и Басовые Табы | DadRock Tabs',
      description: 'Научитесь играть {song} от {artist} с бесплатными уроками от DadRock Tabs.',
    },
  },
  hi: {
    quickies: {
      title: 'DadRock Tabs Quickies - त्वरित गिटार और बेस पाठ | DadRock Tabs',
      description: 'DadRock Tabs से त्वरित गिटार और बेस टैब पाठ। क्लासिक रॉक और हेवी मेटल रिफ सीखने के लिए छोटे ट्यूटोरियल।',
    },
    comingSoon: {
      title: 'आगामी गिटार पाठ | DadRock Tabs',
      description: 'DadRock Tabs पर आगामी गिटार और बेस पाठ देखें। क्लासिक रॉक, हेवी मेटल के नए ट्यूटोरियल।',
    },
    topLessons: {
      title: 'शीर्ष 10 सबसे देखे गए गिटार पाठ | DadRock Tabs',
      description: 'DadRock Tabs पर सबसे लोकप्रिय गिटार और बेस टैब ट्यूटोरियल खोजें।',
    },
    artist: {
      title: '{artist} गिटार और बेस टैब | DadRock Tabs',
      description: 'DadRock Tabs से मुफ्त गिटार और बेस टैब पाठ के साथ {artist} के गाने सीखें।',
    },
    song: {
      title: '{song} - {artist} गिटार और बेस टैब | DadRock Tabs',
      description: 'DadRock Tabs से मुफ्त पाठ के साथ {artist} का {song} सीखें।',
    },
  },
  sv: {
    quickies: {
      title: 'DadRock Tabs Quickies - Snabba Gitarr- & Baslektioner | DadRock Tabs',
      description: 'Snabba gitarr- och bas-tablektioner från DadRock Tabs. Korta tutorials för att lära dig klassiska rock- och heavy metal-riff.',
    },
    comingSoon: {
      title: 'Kommande Gitarrlektioner | DadRock Tabs',
      description: 'Se kommande gitarr- och baslektioner på DadRock Tabs. Nya tutorials för klassisk rock och heavy metal.',
    },
    topLessons: {
      title: 'Topp 10 Mest Sedda Gitarrlektioner | DadRock Tabs',
      description: 'Upptäck de mest populära gitarr- och bas-tutorials på DadRock Tabs.',
    },
    artist: {
      title: '{artist} Gitarr- & Bas-Tabs | DadRock Tabs',
      description: 'Lär dig spela {artist}-låtar med gratis gitarr- och bas-tablektioner från DadRock Tabs.',
    },
    song: {
      title: '{song} av {artist} - Gitarr- & Bas-Tab | DadRock Tabs',
      description: 'Lär dig spela {song} av {artist} med gratis lektioner från DadRock Tabs.',
    },
  },
  fi: {
    quickies: {
      title: 'DadRock Tabs Quickies - Nopeat Kitara- & Bassotunnit | DadRock Tabs',
      description: 'Nopeita kitara- ja bassotablatuuritunteja DadRock Tabsilta. Lyhyitä tutoriaaleja klassisen rockin ja heavy metalin riffien oppimiseen.',
    },
    comingSoon: {
      title: 'Tulevat Kitaratunnit | DadRock Tabs',
      description: 'Katso tulevat kitara- ja bassotunnit DadRock Tabsissa. Uusia klassisen rockin ja heavy metalin tutoriaaleja.',
    },
    topLessons: {
      title: 'Top 10 Katsotuinta Kitaratuntia | DadRock Tabs',
      description: 'Löydä DadRock Tabsin suosituimmat kitara- ja bassotutoriaalit.',
    },
    artist: {
      title: '{artist} Kitara- & Bassotabit | DadRock Tabs',
      description: 'Opi soittamaan {artist}-kappaleita ilmaisilla kitara- ja bassotunneilla DadRock Tabsilta.',
    },
    song: {
      title: '{song} - {artist} Kitara- & Bassotabi | DadRock Tabs',
      description: 'Opi soittamaan {song} ({artist}) ilmaisilla tunneilla DadRock Tabsilta.',
    },
  },
};

/**
 * Get translated SEO meta for a specific page type
 * @param {string} lang - Language code
 * @param {string} pageType - 'quickies', 'comingSoon', 'topLessons', 'artist', 'song'
 * @param {object} params - Optional params for artist/song templates: { artist, song }
 * @returns {{ title: string, description: string }}
 */
export function getSeoMeta(lang, pageType, params = {}) {
  const translations = seoTranslations[lang] || seoTranslations.en;
  const meta = translations[pageType] || seoTranslations.en[pageType];
  
  if (!meta) return { title: 'DadRock Tabs', description: '' };

  let title = meta.title;
  let description = meta.description;

  // Replace placeholders
  if (params.artist) {
    title = title.replace(/{artist}/g, params.artist);
    description = description.replace(/{artist}/g, params.artist);
  }
  if (params.song) {
    title = title.replace(/{song}/g, params.song);
    description = description.replace(/{song}/g, params.song);
  }

  return { title, description };
}

/**
 * Update document meta tags dynamically (client-side)
 * Call this in useEffect when language changes
 */
export function updateDocumentMeta(title, description) {
  if (typeof document === 'undefined') return;

  // Update title
  document.title = title;

  // Update meta description
  let metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc) {
    metaDesc.setAttribute('content', description);
  } else {
    metaDesc = document.createElement('meta');
    metaDesc.setAttribute('name', 'description');
    metaDesc.setAttribute('content', description);
    document.head.appendChild(metaDesc);
  }

  // Update OG title
  let ogTitle = document.querySelector('meta[property="og:title"]');
  if (ogTitle) {
    ogTitle.setAttribute('content', title);
  } else {
    ogTitle = document.createElement('meta');
    ogTitle.setAttribute('property', 'og:title');
    ogTitle.setAttribute('content', title);
    document.head.appendChild(ogTitle);
  }

  // Update OG description
  let ogDesc = document.querySelector('meta[property="og:description"]');
  if (ogDesc) {
    ogDesc.setAttribute('content', description);
  } else {
    ogDesc = document.createElement('meta');
    ogDesc.setAttribute('property', 'og:description');
    ogDesc.setAttribute('content', description);
    document.head.appendChild(ogDesc);
  }

  // Update Twitter title
  let twTitle = document.querySelector('meta[name="twitter:title"]');
  if (twTitle) {
    twTitle.setAttribute('content', title);
  }

  // Update Twitter description
  let twDesc = document.querySelector('meta[name="twitter:description"]');
  if (twDesc) {
    twDesc.setAttribute('content', description);
  }
}

export default seoTranslations;
