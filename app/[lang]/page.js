import { locales, localeNames } from '@/lib/i18n';

// Generate static params for all language routes
export async function generateStaticParams() {
  return locales.map((lang) => ({
    lang: lang,
  }));
}

// Generate metadata for each language
export async function generateMetadata({ params }) {
  const lang = params.lang || 'en';
  
  const titles = {
    en: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',
    es: 'DadRock Tabs - Tablaturas de Guitarra y Bajo para Rock Clásico',
    pt: 'DadRock Tabs - Tablaturas de Guitarra e Baixo para Rock Clássico',
    'pt-br': 'DadRock Tabs - Tablaturas de Guitarra e Baixo para Rock Clássico',
    de: 'DadRock Tabs - Gitarren- und Bass-Tabs für klassischen Rock',
    fr: 'DadRock Tabs - Tablatures Guitare et Basse pour le Rock Classique',
    it: 'DadRock Tabs - Tablature per Chitarra e Basso per Rock Classico',
    ja: 'DadRock Tabs - クラシックロックのギター＆ベースタブ譜',
    ko: 'DadRock Tabs - 클래식 록 기타 & 베이스 탭',
    zh: 'DadRock Tabs - 经典摇滚吉他和贝斯谱',
    ru: 'DadRock Tabs - Гитарные и басовые табулатуры классического рока',
    hi: 'DadRock Tabs - क्लासिक रॉक के लिए गिटार और बास टैब',
    sv: 'DadRock Tabs - Gitarr- och Bastabulatur för Klassisk Rock',
    fi: 'DadRock Tabs - Kitara- ja Bassotabulatuurit Klassiselle Rockille',
  };

  const descriptions = {
    en: 'Free guitar and bass tabs for classic rock hits. Learn to play Led Zeppelin, AC/DC, Van Halen, and more! Your go-to database for dad rock guitar tutorials.',
    es: 'Tablaturas gratuitas de guitarra y bajo para clásicos del rock. ¡Aprende a tocar Led Zeppelin, AC/DC, Van Halen y más! Tu base de datos de tutoriales de guitarra dad rock.',
    pt: 'Tablaturas gratuitas de guitarra e baixo para clássicos do rock. Aprenda a tocar Led Zeppelin, AC/DC, Van Halen e mais! Seu banco de dados de tutoriais de guitarra dad rock.',
    'pt-br': 'Tablaturas gratuitas de guitarra e baixo para clássicos do rock. Aprenda a tocar Led Zeppelin, AC/DC, Van Halen e mais! Seu banco de dados de tutoriais de guitarra dad rock.',
    de: 'Kostenlose Gitarren- und Bass-Tabs für klassische Rock-Hits. Lerne Led Zeppelin, AC/DC, Van Halen und mehr zu spielen! Deine Datenbank für Dad Rock Gitarren-Tutorials.',
    fr: 'Tablatures gratuites de guitare et basse pour les classiques du rock. Apprenez à jouer Led Zeppelin, AC/DC, Van Halen et plus! Votre base de données de tutoriels guitare dad rock.',
    it: 'Tablature gratuite per chitarra e basso per i classici del rock. Impara a suonare Led Zeppelin, AC/DC, Van Halen e altro! Il tuo database di tutorial per chitarra dad rock.',
    ja: 'クラシックロックヒットの無料ギター＆ベースタブ譜。Led Zeppelin、AC/DC、Van Halenなどの演奏を学ぼう！ダッドロックギターチュートリアルのデータベース。',
    ko: '클래식 록 히트곡의 무료 기타 & 베이스 탭. Led Zeppelin, AC/DC, Van Halen 등을 연주하는 법을 배우세요! 대드 록 기타 튜토리얼 데이터베이스.',
    zh: '经典摇滚热门歌曲的免费吉他和贝斯谱。学习演奏Led Zeppelin、AC/DC、Van Halen等！您的爸爸摇滚吉他教程数据库。',
    ru: 'Бесплатные гитарные и басовые табулатуры классических рок-хитов. Научитесь играть Led Zeppelin, AC/DC, Van Halen и других! Ваша база данных уроков гитары dad rock.',
    hi: 'क्लासिक रॉक हिट्स के लिए मुफ्त गिटार और बास टैब। Led Zeppelin, AC/DC, Van Halen और अधिक बजाना सीखें! डैड रॉक गिटार ट्यूटोरियल का आपका डेटाबेस।',
    sv: 'Gratis gitarr- och bastabulatur för klassiska rockhits. Lär dig spela Led Zeppelin, AC/DC, Van Halen och mer! Din databas för dad rock gitarrlektioner.',
    fi: 'Ilmaiset kitara- ja bassotabulatuurit klassisille rock-hiteille. Opi soittamaan Led Zeppelin, AC/DC, Van Halen ja paljon muuta! Tietokantasi dad rock kitaraoppaille.',
  };

  const keywords = {
    en: 'guitar tabs, bass tabs, classic rock, dad rock, guitar lessons, Led Zeppelin, AC/DC, Van Halen, Metallica, rock music tutorials',
    es: 'tablaturas guitarra, tablaturas bajo, rock clásico, dad rock, lecciones guitarra, Led Zeppelin, AC/DC, Van Halen, Metallica',
    pt: 'tablaturas guitarra, tablaturas baixo, rock clássico, dad rock, aulas guitarra, Led Zeppelin, AC/DC, Van Halen, Metallica',
    'pt-br': 'tablaturas guitarra, tablaturas baixo, rock clássico, dad rock, aulas guitarra, Led Zeppelin, AC/DC, Van Halen, Metallica',
    de: 'Gitarrentabs, Basstabs, klassischer Rock, Dad Rock, Gitarrenunterricht, Led Zeppelin, AC/DC, Van Halen, Metallica',
    fr: 'tablatures guitare, tablatures basse, rock classique, dad rock, cours guitare, Led Zeppelin, AC/DC, Van Halen, Metallica',
    it: 'tablature chitarra, tablature basso, rock classico, dad rock, lezioni chitarra, Led Zeppelin, AC/DC, Van Halen, Metallica',
    ja: 'ギタータブ, ベースタブ, クラシックロック, ダッドロック, ギターレッスン, Led Zeppelin, AC/DC, Van Halen, Metallica',
    ko: '기타 탭, 베이스 탭, 클래식 록, 대드 록, 기타 레슨, Led Zeppelin, AC/DC, Van Halen, Metallica',
    zh: '吉他谱, 贝斯谱, 经典摇滚, 爸爸摇滚, 吉他课程, Led Zeppelin, AC/DC, Van Halen, Metallica',
    ru: 'гитарные табы, басовые табы, классический рок, дэд рок, уроки гитары, Led Zeppelin, AC/DC, Van Halen, Metallica',
    hi: 'गिटार टैब, बास टैब, क्लासिक रॉक, डैड रॉक, गिटार सबक, Led Zeppelin, AC/DC, Van Halen, Metallica',
    sv: 'gitarrtabs, bastabs, klassisk rock, dad rock, gitarrlektioner, Led Zeppelin, AC/DC, Van Halen, Metallica',
    fi: 'kitaratabulatuurit, bassotabulatuurit, klassinen rock, dad rock, kitaratunnit, Led Zeppelin, AC/DC, Van Halen, Metallica',
  };

  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://dadrocktabs.com';

  // Generate alternate language links
  const languages = {};
  locales.forEach(l => {
    languages[l] = l === 'en' ? baseUrl : `${baseUrl}/${l}`;
  });

  return {
    title: titles[lang] || titles.en,
    description: descriptions[lang] || descriptions.en,
    keywords: keywords[lang] || keywords.en,
    alternates: {
      canonical: lang === 'en' ? baseUrl : `${baseUrl}/${lang}`,
      languages: languages,
    },
    openGraph: {
      title: titles[lang] || titles.en,
      description: descriptions[lang] || descriptions.en,
      type: 'website',
      locale: lang,
      alternateLocale: locales.filter(l => l !== lang),
      url: lang === 'en' ? baseUrl : `${baseUrl}/${lang}`,
      siteName: 'DadRock Tabs',
    },
    twitter: {
      card: 'summary_large_image',
      title: titles[lang] || titles.en,
      description: descriptions[lang] || descriptions.en,
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
  };
}

// Import and re-export the main page component with lang param
import HomePage from '../page';

export default function LangPage({ params }) {
  return <HomePage initialLang={params.lang} />;
}
