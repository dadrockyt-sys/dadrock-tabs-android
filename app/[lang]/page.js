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
    en: 'DadRock Tabs - Free Guitar & Bass Tabs for 70s 80s 90s Classic Rock, Heavy Metal & Blues',
    es: 'DadRock Tabs - Tablaturas Gratis de Guitarra y Bajo para Rock Clásico de los 70s 80s 90s',
    pt: 'DadRock Tabs - Tablaturas Grátis de Guitarra e Baixo para Rock Clássico dos Anos 70 80 90',
    'pt-br': 'DadRock Tabs - Tablaturas Grátis de Guitarra e Baixo para Rock Clássico dos Anos 70 80 90',
    de: 'DadRock Tabs - Kostenlose Gitarren & Bass Tabs für 70er 80er 90er Classic Rock & Heavy Metal',
    fr: 'DadRock Tabs - Tablatures Gratuites Guitare & Basse pour Rock Classique des Années 70 80 90',
    it: 'DadRock Tabs - Tablature Gratuite Chitarra e Basso per Rock Classico Anni 70 80 90',
    ja: 'DadRock Tabs - 70年代80年代90年代クラシックロック＆ヘビーメタルの無料ギター＆ベースタブ譜',
    ko: 'DadRock Tabs - 70년대 80년대 90년대 클래식 록 & 헤비 메탈 무료 기타 & 베이스 탭',
    zh: 'DadRock Tabs - 70年代80年代90年代经典摇滚和重金属免费吉他贝斯谱',
    ru: 'DadRock Tabs - Бесплатные табы для гитары и баса классического рока 70-х 80-х 90-х',
    hi: 'DadRock Tabs - 70s 80s 90s क्लासिक रॉक और हेवी मेटल के लिए मुफ्त गिटार और बास टैब',
    sv: 'DadRock Tabs - Gratis Gitarr & Bas Tabs för 70-tal 80-tal 90-tal Klassisk Rock & Heavy Metal',
    fi: 'DadRock Tabs - Ilmaiset Kitara & Basso Tabit 70- 80- 90-luvun Klassiselle Rockille',
  };

  const descriptions = {
    en: 'Learn to play guitar and bass with free tabs for classic rock, heavy metal, hair metal, and blues. Perfect for beginners to advanced players. Featuring Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, Ozzy Osbourne, Def Leppard, Guns N\' Roses, and more 70s 80s 90s rock legends. Electric and acoustic guitar tutorials.',
    es: 'Aprende a tocar guitarra y bajo con tablaturas gratis de rock clásico, heavy metal, hair metal y blues. Perfecto para principiantes y avanzados. Led Zeppelin, AC/DC, Van Halen, Metallica y más leyendas del rock de los 70s 80s 90s. Tutoriales de guitarra eléctrica y acústica.',
    pt: 'Aprenda a tocar guitarra e baixo com tablaturas grátis de rock clássico, heavy metal, hair metal e blues. Perfeito para iniciantes e avançados. Led Zeppelin, AC/DC, Van Halen, Metallica e mais lendas do rock dos anos 70 80 90. Tutoriais de guitarra elétrica e acústica.',
    'pt-br': 'Aprenda a tocar guitarra e baixo com tablaturas grátis de rock clássico, heavy metal, hair metal e blues. Perfeito para iniciantes e avançados. Led Zeppelin, AC/DC, Van Halen, Metallica e mais lendas do rock dos anos 70 80 90. Tutoriais de guitarra elétrica e acústica.',
    de: 'Lerne Gitarre und Bass mit kostenlosen Tabs für Classic Rock, Heavy Metal, Hair Metal und Blues. Perfekt für Anfänger bis Fortgeschrittene. Led Zeppelin, AC/DC, Van Halen, Metallica und mehr Rock-Legenden der 70er 80er 90er. E-Gitarre und Akustikgitarre Tutorials.',
    fr: 'Apprenez la guitare et la basse avec des tablatures gratuites de rock classique, heavy metal, hair metal et blues. Parfait pour débutants et avancés. Led Zeppelin, AC/DC, Van Halen, Metallica et plus de légendes rock des années 70 80 90. Tutoriels guitare électrique et acoustique.',
    it: 'Impara a suonare chitarra e basso con tablature gratuite di rock classico, heavy metal, hair metal e blues. Perfetto per principianti e avanzati. Led Zeppelin, AC/DC, Van Halen, Metallica e altre leggende rock degli anni 70 80 90. Tutorial chitarra elettrica e acustica.',
    ja: 'クラシックロック、ヘビーメタル、ヘアメタル、ブルースの無料タブ譜でギターとベースを学ぼう。初心者から上級者まで対応。Led Zeppelin、AC/DC、Van Halen、Metallicaなど70年代80年代90年代のロックレジェンドを収録。エレキギターとアコースティックギターのチュートリアル。',
    ko: '클래식 록, 헤비 메탈, 헤어 메탈, 블루스의 무료 탭으로 기타와 베이스를 배우세요. 초보자부터 고급자까지. Led Zeppelin, AC/DC, Van Halen, Metallica 등 70년대 80년대 90년대 록 레전드 수록. 일렉트릭 및 어쿠스틱 기타 튜토리얼.',
    zh: '通过经典摇滚、重金属、华丽金属和布鲁斯的免费谱子学习吉他和贝斯。适合初学者到高级玩家。收录Led Zeppelin、AC/DC、Van Halen、Metallica等70年代80年代90年代摇滚传奇。电吉他和原声吉他教程。',
    ru: 'Научитесь играть на гитаре и басу с бесплатными табулатурами классического рока, хэви-метала, хэйр-метала и блюза. Подходит для начинающих и продвинутых. Led Zeppelin, AC/DC, Van Halen, Metallica и другие легенды рока 70-х 80-х 90-х. Уроки электро и акустической гитары.',
    hi: 'क्लासिक रॉक, हेवी मेटल, हेयर मेटल और ब्लूज़ के मुफ्त टैब्स से गिटार और बास बजाना सीखें। शुरुआती से लेकर विशेषज्ञ तक के लिए उपयुक्त। Led Zeppelin, AC/DC, Van Halen, Metallica और 70s 80s 90s के रॉक लीजेंड्स। इलेक्ट्रिक और एकॉस्टिक गिटार ट्यूटोरियल।',
    sv: 'Lär dig spela gitarr och bas med gratis tabulatur för klassisk rock, heavy metal, hair metal och blues. Perfekt för nybörjare till avancerade spelare. Led Zeppelin, AC/DC, Van Halen, Metallica och fler rocklegender från 70- 80- 90-talet. Elgitarr och akustisk gitarr tutorials.',
    fi: 'Opi soittamaan kitaraa ja bassoa ilmaisilla tabulatuureilla klassiselle rockille, heavy metalille, hair metalille ja bluesille. Sopii aloittelijoista edistyneisiin. Led Zeppelin, AC/DC, Van Halen, Metallica ja muita 70- 80- 90-luvun rock-legendoja. Sähkö- ja akustisen kitaran oppaat.',
  };

  const keywords = {
    en: 'guitar tabs, bass tabs, free guitar tabs, beginner guitar tabs, easy guitar tabs, classic rock tabs, heavy metal tabs, hair metal tabs, blues guitar tabs, 70s rock, 80s rock, 90s rock, Led Zeppelin tabs, AC/DC tabs, Van Halen tabs, Metallica tabs, Black Sabbath tabs, Ozzy Osbourne tabs, Def Leppard tabs, Guns N Roses tabs, electric guitar lessons, acoustic guitar tabs, learn guitar, guitar tutorials, bass guitar tabs, rock guitar riffs',
    es: 'tablaturas guitarra gratis, tabs guitarra fácil, rock clásico tabs, heavy metal tabs, hair metal, blues guitarra, rock años 70 80 90, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, lecciones guitarra eléctrica, guitarra acústica, aprender guitarra, bajo eléctrico',
    pt: 'tablaturas guitarra grátis, tabs guitarra fácil, rock clássico tabs, heavy metal tabs, hair metal, blues guitarra, rock anos 70 80 90, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, aulas guitarra elétrica, guitarra acústica, aprender guitarra, baixo',
    'pt-br': 'tablaturas guitarra grátis, tabs guitarra fácil, rock clássico tabs, heavy metal tabs, hair metal, blues guitarra, rock anos 70 80 90, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, aulas guitarra elétrica, guitarra acústica, aprender guitarra, baixo',
    de: 'Gitarrentabs kostenlos, einfache Gitarrentabs, Classic Rock Tabs, Heavy Metal Tabs, Hair Metal, Blues Gitarre, 70er 80er 90er Rock, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, E-Gitarre lernen, Akustikgitarre, Bass Tabs',
    fr: 'tablatures guitare gratuites, tabs guitare facile, rock classique tabs, heavy metal tabs, hair metal, blues guitare, rock années 70 80 90, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, cours guitare électrique, guitare acoustique, apprendre guitare, basse',
    it: 'tablature chitarra gratis, tabs chitarra facile, rock classico tabs, heavy metal tabs, hair metal, blues chitarra, rock anni 70 80 90, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, lezioni chitarra elettrica, chitarra acustica, imparare chitarra, basso',
    ja: 'ギタータブ無料, 簡単ギタータブ, クラシックロックタブ, ヘビーメタルタブ, ヘアメタル, ブルースギター, 70年代80年代90年代ロック, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, エレキギターレッスン, アコースティックギター, ベースタブ',
    ko: '기타 탭 무료, 쉬운 기타 탭, 클래식 록 탭, 헤비 메탈 탭, 헤어 메탈, 블루스 기타, 70년대 80년대 90년대 록, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, 일렉트릭 기타 레슨, 어쿠스틱 기타, 베이스 탭',
    zh: '吉他谱免费, 简单吉他谱, 经典摇滚谱, 重金属谱, 华丽金属, 布鲁斯吉他, 70年代80年代90年代摇滚, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, 电吉他课程, 原声吉他, 贝斯谱',
    ru: 'гитарные табы бесплатно, простые табы гитара, классический рок табы, хэви-метал табы, хэйр-метал, блюз гитара, рок 70-х 80-х 90-х, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, уроки электрогитары, акустическая гитара, бас табы',
    hi: 'गिटार टैब मुफ्त, आसान गिटार टैब, क्लासिक रॉक टैब, हेवी मेटल टैब, हेयर मेटल, ब्लूज़ गिटार, 70s 80s 90s रॉक, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, इलेक्ट्रिक गिटार लेसन, एकॉस्टिक गिटार, बास टैब',
    sv: 'gitarrtabs gratis, enkla gitarrtabs, klassisk rock tabs, heavy metal tabs, hair metal, blues gitarr, 70-tal 80-tal 90-tal rock, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, elgitarr lektioner, akustisk gitarr, bas tabs',
    fi: 'kitaratabulatuurit ilmaiset, helpot kitaratabit, klassinen rock tabit, heavy metal tabit, hair metal, blues kitara, 70- 80- 90-luvun rock, Led Zeppelin, AC/DC, Van Halen, Metallica, Black Sabbath, sähkökitara oppitunnit, akustinen kitara, basso tabit',
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
