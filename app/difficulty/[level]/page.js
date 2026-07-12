import { DIFFICULTY_LEVELS, getArtistsByDifficulty } from '@/lib/difficultyData';
import { notFound } from 'next/navigation';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import Link from 'next/link';
import DifficultyHeader from './DifficultyHeader';
import { headers } from 'next/headers';
function getLocalizedPath(path, lang) {
  if (!lang || lang === 'en') return path;
  return path === '/' ? `/${lang}` : `/${lang}${path}`;
}

const difficultyT = {
  en: {
    home: 'Home',
    difficultyLevel: 'Difficulty Level',
    artists: 'Artists',
    lessons: 'Lessons',
    whatToExpect: 'What to Expect',
    songs: 'Songs',
    availableArtists: 'available artists',
    browseSongs: 'Browse Songs',

    levels: {
      beginner: {
        name: 'Beginner',
        title: 'Beginner Guitar Tabs',
        description:
          'Easy songs perfect for new guitar players. Simple riffs, basic chords, and slow tempos.',
        longDescription:
          'These songs are ideal for guitarists in their first 6 months of playing. They feature simple power chord progressions, slow-to-moderate tempos, basic strumming patterns, and straightforward single-note riffs. Most can be learned in a single practice session.'
      },

      intermediate: {
        name: 'Intermediate',
        title: 'Intermediate Guitar Tabs',
        description:
          'Songs that challenge your technique with faster riffs, barre chords, and moderate solos.',
        longDescription:
          'Intermediate songs require comfort with barre chords, palm muting at moderate speeds, basic lead techniques such as bending, hammer-ons, and pull-offs, and the ability to switch between clean and distorted sections. Expect faster tempos and more complex song structures.'
      },

      advanced: {
        name: 'Advanced',
        title: 'Advanced Guitar Tabs',
        description:
          'Complex songs featuring fast shredding, intricate solos, and demanding techniques.',
        longDescription:
          'Advanced songs demand mastery of speed picking, including alternate picking and downpicking at high BPM, sweep picking, tapping, complex time signatures, extended solos, and multi-part arrangements. These are the songs that separate serious guitarists from casual players.'
      }
    }
  },

    es: {
    home: 'Inicio',
    difficultyLevel: 'Nivel de dificultad',
    artists: 'Artistas',
    lessons: 'Lecciones',
    whatToExpect: 'Qué esperar',
    songs: 'Canciones',
    availableArtists: 'artistas disponibles',
    browseSongs: 'Ver canciones',

    levels: {
      beginner: {
        name: 'Principiante',
        title: 'Tablaturas de guitarra para principiantes',
        description:
          'Canciones fáciles, perfectas para nuevos guitarristas. Riffs sencillos, acordes básicos y tempos lentos.',
        longDescription:
          'Estas canciones son ideales para guitarristas durante sus primeros 6 meses de aprendizaje. Incluyen progresiones sencillas de acordes de quinta, tempos lentos o moderados, patrones básicos de rasgueo y riffs directos de una sola nota. La mayoría puede aprenderse en una sola sesión de práctica.'
      },

      intermediate: {
        name: 'Intermedio',
        title: 'Tablaturas de guitarra de nivel intermedio',
        description:
          'Canciones que desafían tu técnica con riffs más rápidos, acordes con cejilla y solos moderados.',
        longDescription:
          'Las canciones de nivel intermedio requieren comodidad con los acordes con cejilla, palm muting a velocidades moderadas, técnicas básicas de guitarra solista como bends, hammer-ons y pull-offs, y la capacidad de cambiar entre secciones limpias y distorsionadas. Encontrarás tempos más rápidos y estructuras más complejas.'
      },

      advanced: {
        name: 'Avanzado',
        title: 'Tablaturas de guitarra avanzadas',
        description:
          'Canciones complejas con shredding rápido, solos elaborados y técnicas exigentes.',
        longDescription:
          'Las canciones avanzadas exigen dominar la púa rápida, tanto alternada como hacia abajo a BPM altos, sweep picking, tapping, compases complejos, solos extensos y arreglos de varias partes. Son las canciones que distinguen a los guitarristas serios de los músicos ocasionales.'
      }
    }
  },

  pt: {
  home: 'Início',
  difficultyLevel: 'Nível de dificuldade',
  artists: 'Artistas',
  lessons: 'Lições',
  whatToExpect: 'O que esperar',
  songs: 'Músicas',
  availableArtists: 'artistas disponíveis',
  browseSongs: 'Explorar músicas',
  about: 'Sobre',
  browseOtherLevels: 'Explorar outros níveis de dificuldade',

  levels: {
    beginner: {
      name: 'Iniciante',
      title: 'Tabs de Guitarra para Iniciantes',
      description:
        'Músicas fáceis, perfeitas para novos guitarristas. Riffs simples, acordes básicos e andamentos lentos.',
      longDescription:
        'Estas músicas são ideais para guitarristas nos seus primeiros 6 meses de aprendizado. Incluem progressões simples de power chords, andamentos lentos a moderados, padrões básicos de dedilhado e riffs simples de uma única nota. A maioria pode ser aprendida em uma única sessão de prática.'
    },

    intermediate: {
      name: 'Intermediário',
      title: 'Tabs de Guitarra Intermediárias',
      description:
        'Músicas que desafiam sua técnica com riffs mais rápidos, acordes com pestana e solos de dificuldade moderada.',
      longDescription:
        'As músicas intermediárias exigem familiaridade com acordes com pestana, palm muting em velocidades moderadas, técnicas básicas de solo como bends, hammer-ons e pull-offs, além da capacidade de alternar entre partes limpas e distorcidas. Espere andamentos mais rápidos e estruturas musicais mais complexas.'
    },

    advanced: {
      name: 'Avançado',
      title: 'Tabs de Guitarra Avançadas',
      description:
        'Músicas complexas com shredding rápido, solos intrincados e técnicas exigentes.',
      longDescription:
        'As músicas avançadas exigem domínio de speed picking, incluindo alternate picking e downpicking em altos BPM, sweep picking, tapping, compassos complexos, solos longos e arranjos com várias partes. Estas são as músicas que diferenciam guitarristas dedicados dos casuais.'
    }
  }
},

  'pt-br': {
  home: 'Início',
  difficultyLevel: 'Nível de dificuldade',
  artists: 'Artistas',
  lessons: 'Lições',
  whatToExpect: 'O que esperar',
  songs: 'Músicas',
  availableArtists: 'artistas disponíveis',
  browseSongs: 'Explorar músicas',
  about: 'Sobre',
  browseOtherLevels: 'Explorar outros níveis de dificuldade',

  levels: {
    beginner: {
      name: 'Iniciante',
      title: 'Tabs de Guitarra para Iniciantes',
      description:
        'Músicas fáceis, perfeitas para quem está começando na guitarra. Riffs simples, acordes básicos e andamento lento.',
      longDescription:
        'Essas músicas são ideais para guitarristas nos primeiros seis meses de aprendizado. Elas apresentam progressões simples de power chords, andamentos lentos a moderados, padrões básicos de palhetada e riffs de uma única nota. A maioria pode ser aprendida em apenas uma sessão de prática.'
    },

    intermediate: {
      name: 'Intermediário',
      title: 'Tabs de Guitarra Intermediárias',
      description:
        'Músicas que desafiam sua técnica com riffs mais rápidos, acordes com pestana e solos de dificuldade moderada.',
      longDescription:
        'As músicas intermediárias exigem domínio de acordes com pestana, palm muting em velocidades moderadas, técnicas básicas de solo como bends, hammer-ons e pull-offs, além da capacidade de alternar entre partes limpas e distorcidas. Espere andamentos mais rápidos e estruturas musicais mais complexas.'
    },

    advanced: {
      name: 'Avançado',
      title: 'Tabs de Guitarra Avançadas',
      description:
        'Músicas complexas com shredding rápido, solos intrincados e técnicas exigentes.',
      longDescription:
        'As músicas avançadas exigem domínio de speed picking, incluindo alternate picking e downpicking em altos BPM, sweep picking, tapping, compassos complexos, solos longos e arranjos com várias partes. Essas são as músicas que diferenciam guitarristas dedicados dos casuais.'
    }
  }
},

  de: {
  home: 'Startseite',
  difficultyLevel: 'Schwierigkeitsgrad',
  artists: 'Künstler',
  lessons: 'Lektionen',
  whatToExpect: 'Was dich erwartet',
  songs: 'Songs',
  availableArtists: 'verfügbare Künstler',
  browseSongs: 'Songs durchsuchen',
  about: 'Über',
  browseOtherLevels: 'Weitere Schwierigkeitsstufen entdecken',

  levels: {
    beginner: {
      name: 'Anfänger',
      title: 'Gitarren-Tabs für Anfänger',
      description:
        'Einfache Songs – perfekt für neue Gitarristen. Leichte Riffs, grundlegende Akkorde und langsame Tempi.',
      longDescription:
        'Diese Songs sind ideal für Gitarristen in den ersten sechs Monaten des Lernens. Sie enthalten einfache Powerchord-Folgen, langsame bis mittlere Tempi, grundlegende Anschlagmuster und unkomplizierte Einzelnoten-Riffs. Die meisten können in einer einzigen Übungseinheit gelernt werden.'
    },

    intermediate: {
      name: 'Fortgeschritten',
      title: 'Gitarren-Tabs für Fortgeschrittene',
      description:
        'Songs, die deine Technik mit schnelleren Riffs, Barré-Akkorden und mittelschweren Soli herausfordern.',
      longDescription:
        'Fortgeschrittene Songs setzen Sicherheit bei Barré-Akkorden, Palm Muting in mittlerem Tempo, grundlegenden Lead-Techniken wie Bendings, Hammer-ons und Pull-offs sowie den Wechsel zwischen Clean- und Distortion-Parts voraus. Freue dich auf schnellere Tempi und komplexere Songstrukturen.'
    },

    advanced: {
      name: 'Experte',
      title: 'Fortgeschrittene Gitarren-Tabs',
      description:
        'Komplexe Songs mit schnellem Shredding, anspruchsvollen Soli und fortgeschrittenen Spieltechniken.',
      longDescription:
        'Diese Songs erfordern sicheres Speed Picking mit Alternate Picking und schnellem Downpicking, Sweep Picking, Tapping, komplexe Taktarten, lange Soli und mehrteilige Arrangements. Sie unterscheiden engagierte Gitarristen von Gelegenheitsspielern.'
    }
  }
},

  fr: {
  home: 'Accueil',
  difficultyLevel: 'Niveau de difficulté',
  artists: 'Artistes',
  lessons: 'Leçons',
  whatToExpect: 'À quoi s’attendre',
  songs: 'Chansons',
  availableArtists: 'artistes disponibles',
  browseSongs: 'Parcourir les chansons',
  about: 'À propos',
  browseOtherLevels: 'Explorer les autres niveaux de difficulté',

  levels: {
    beginner: {
      name: 'Débutant',
      title: 'Tabs de guitare pour débutants',
      description:
        'Des chansons faciles, parfaites pour les nouveaux guitaristes. Riffs simples, accords de base et tempos lents.',
      longDescription:
        'Ces chansons sont idéales pour les guitaristes durant leurs six premiers mois d’apprentissage. Elles proposent des progressions simples de power chords, des tempos lents à modérés, des rythmiques de base et des riffs à une seule note. La plupart peuvent être apprises en une seule séance de pratique.'
    },

    intermediate: {
      name: 'Intermédiaire',
      title: 'Tabs de guitare intermédiaires',
      description:
        'Des chansons qui mettent votre technique à l’épreuve avec des riffs plus rapides, des accords barrés et des solos de difficulté moyenne.',
      longDescription:
        'Les morceaux intermédiaires nécessitent une bonne maîtrise des accords barrés, du palm muting à vitesse modérée, des techniques de solo de base comme les bends, hammer-ons et pull-offs, ainsi que la capacité de passer des sons clairs aux sons saturés. Attendez-vous à des tempos plus rapides et à des structures plus complexes.'
    },

    advanced: {
      name: 'Avancé',
      title: 'Tabs de guitare avancées',
      description:
        'Des morceaux complexes avec du shredding rapide, des solos élaborés et des techniques exigeantes.',
      longDescription:
        'Les morceaux avancés demandent une excellente maîtrise du speed picking, y compris l’alternate picking et le downpicking à haute vitesse, du sweep picking, du tapping, des signatures rythmiques complexes, de longs solos et des arrangements en plusieurs parties. Ce sont les morceaux qui distinguent les guitaristes passionnés des joueurs occasionnels.'
    }
  }
},

  it: {
  home: 'Home',
  difficultyLevel: 'Livello di difficoltà',
  artists: 'Artisti',
  lessons: 'Lezioni',
  whatToExpect: 'Cosa aspettarsi',
  songs: 'Brani',
  availableArtists: 'artisti disponibili',
  browseSongs: 'Sfoglia i brani',
  about: 'Informazioni',
  browseOtherLevels: 'Esplora gli altri livelli di difficoltà',

  levels: {
    beginner: {
      name: 'Principiante',
      title: 'Tab per chitarra per principianti',
      description:
        'Brani facili, perfetti per chi inizia a suonare la chitarra. Riff semplici, accordi di base e tempi lenti.',
      longDescription:
        'Questi brani sono ideali per i chitarristi nei loro primi sei mesi di studio. Presentano semplici progressioni di power chord, tempi lenti o moderati, schemi di pennata di base e riff a nota singola facili da eseguire. La maggior parte può essere imparata in una sola sessione di pratica.'
    },

    intermediate: {
      name: 'Intermedio',
      title: 'Tab per chitarra di livello intermedio',
      description:
        'Brani che mettono alla prova la tua tecnica con riff più veloci, accordi con barrè e assoli di media difficoltà.',
      longDescription:
        'I brani di livello intermedio richiedono dimestichezza con gli accordi con barrè, il palm muting a velocità moderata, tecniche solistiche di base come bend, hammer-on e pull-off, oltre alla capacità di passare da parti pulite a parti distorte. Aspettati tempi più veloci e strutture musicali più complesse.'
    },

    advanced: {
      name: 'Avanzato',
      title: 'Tab per chitarra avanzate',
      description:
        'Brani complessi con shredding veloce, assoli elaborati e tecniche impegnative.',
      longDescription:
        'I brani avanzati richiedono una solida padronanza dello speed picking, inclusi alternate picking e downpicking ad alti BPM, sweep picking, tapping, tempi complessi, lunghi assoli e arrangiamenti articolati. Sono i brani che distinguono i chitarristi più esperti da quelli occasionali.'
    }
  }
},

  ja: {
  home: 'ホーム',
  difficultyLevel: '難易度',
  artists: 'アーティスト',
  lessons: 'レッスン',
  whatToExpect: '学べる内容',
  songs: '曲',
  availableArtists: '利用可能なアーティスト',
  browseSongs: '曲を探す',
  about: '概要',
  browseOtherLevels: '他の難易度を見る',

  levels: {
    beginner: {
      name: '初心者',
      title: '初心者向けギタータブ',
      description:
        'ギターを始めたばかりの人に最適な簡単な曲。シンプルなリフ、基本的なコード、ゆっくりしたテンポが特徴です。',
      longDescription:
        'これらの曲は、ギターを始めて最初の6か月以内のプレイヤーに最適です。シンプルなパワーコード進行、ゆっくりから中程度のテンポ、基本的なストロークパターン、そして分かりやすい単音リフで構成されています。ほとんどの曲は1回の練習で習得できます。'
    },

    intermediate: {
      name: '中級',
      title: '中級者向けギタータブ',
      description:
        'より速いリフ、バレーコード、適度な難易度のソロでテクニックを磨ける曲。',
      longDescription:
        '中級レベルの曲では、バレーコード、適度な速さでのパームミュート、ベンド・ハンマーオン・プリングオフなどの基本的なリードテクニック、さらにクリーントーンとディストーションを切り替える技術が求められます。より速いテンポと複雑な曲構成に挑戦できます。'
    },

    advanced: {
      name: '上級',
      title: '上級者向けギタータブ',
      description:
        '高速シュレッド、複雑なソロ、高度な演奏テクニックを必要とする難しい曲。',
      longDescription:
        '上級レベルの曲では、オルタネイトピッキングや高速ダウンピッキングを含むスピードピッキング、スウィープピッキング、タッピング、複雑な拍子、長いソロ、そして複数パートのアレンジを習得していることが求められます。熟練したギタリストと趣味で弾くプレイヤーとの差を生み出す楽曲です。'
    }
  }
},

  ko: {
  home: '홈',
  difficultyLevel: '난이도',
  artists: '아티스트',
  lessons: '레슨',
  whatToExpect: '배울 내용',
  songs: '곡',
  availableArtists: '이용 가능한 아티스트',
  browseSongs: '곡 둘러보기',
  about: '소개',
  browseOtherLevels: '다른 난이도 살펴보기',

  levels: {
    beginner: {
      name: '초급',
      title: '초급 기타 탭',
      description:
        '기타를 처음 배우는 사람에게 완벽한 쉬운 곡입니다. 간단한 리프, 기본 코드, 느린 템포로 구성되어 있습니다.',
      longDescription:
        '이 곡들은 기타를 시작한 지 약 6개월 이내의 연주자에게 이상적입니다. 간단한 파워 코드 진행, 느리거나 중간 정도의 템포, 기본적인 스트러밍 패턴, 이해하기 쉬운 단일 음 리프로 구성되어 있습니다. 대부분 한 번의 연습만으로도 익힐 수 있습니다.'
    },

    intermediate: {
      name: '중급',
      title: '중급 기타 탭',
      description:
        '더 빠른 리프, 바레 코드, 적당한 난이도의 솔로를 통해 연주 실력을 향상시킬 수 있는 곡입니다.',
      longDescription:
        '중급 곡은 바레 코드, 중간 속도의 팜 뮤트, 벤드·해머온·풀오프와 같은 기본 리드 테크닉, 그리고 클린 톤과 디스토션 톤을 자연스럽게 전환하는 능력이 필요합니다. 더 빠른 템포와 복잡한 곡 구조를 기대할 수 있습니다.'
    },

    advanced: {
      name: '고급',
      title: '고급 기타 탭',
      description:
        '빠른 슈레딩, 복잡한 솔로, 고난도 연주 기법이 필요한 곡입니다.',
      longDescription:
        '고급 곡은 얼터네이트 피킹과 고속 다운피킹을 포함한 스피드 피킹, 스윕 피킹, 태핑, 복잡한 박자, 긴 솔로, 그리고 여러 파트로 구성된 편곡을 소화할 수 있어야 합니다. 이러한 곡들은 숙련된 기타리스트와 취미 연주자를 구분해 주는 도전적인 곡들입니다.'
    }
  }
},

  zh: {
  home: '首页',
  difficultyLevel: '难度等级',
  artists: '艺术家',
  lessons: '课程',
  whatToExpect: '学习内容',
  songs: '歌曲',
  availableArtists: '位可浏览的艺术家',
  browseSongs: '浏览歌曲',
  about: '关于',
  browseOtherLevels: '浏览其他难度等级',

  levels: {
    beginner: {
      name: '初级',
      title: '初级吉他谱',
      description:
        '适合新手吉他手的简单歌曲。包含简单的Riff、基础和弦和较慢的节奏。',
      longDescription:
        '这些歌曲非常适合学习吉他前六个月的演奏者。内容包括简单的强力和弦进行、较慢到中等速度的节奏、基础拨弦模式以及简单的单音Riff。大多数歌曲都可以在一次练习中学会。'
    },

    intermediate: {
      name: '中级',
      title: '中级吉他谱',
      description:
        '通过更快的Riff、横按和弦和中等难度的Solo来提升你的技巧。',
      longDescription:
        '中级歌曲要求你熟练掌握横按和弦、中速Palm Muting、基础主音技巧（如推弦、击弦和勾弦），以及能够在清音和失真音色之间切换。你将面对更快的速度和更复杂的歌曲结构。'
    },

    advanced: {
      name: '高级',
      title: '高级吉他谱',
      description:
        '包含高速Shredding、复杂Solo和高难度演奏技巧的歌曲。',
      longDescription:
        '高级歌曲要求熟练掌握高速拨弦，包括交替拨弦和高速下拨、Sweep Picking、Tapping、复杂拍号、长篇Solo以及多段式编曲。这些歌曲能够真正区分专业投入的吉他手和普通爱好者。'
    }
  }
},

  ru: {
  home: 'Главная',
  difficultyLevel: 'Уровень сложности',
  artists: 'Исполнители',
  lessons: 'Уроки',
  whatToExpect: 'Чего ожидать',
  songs: 'Песни',
  availableArtists: 'доступных исполнителей',
  browseSongs: 'Просмотреть песни',
  about: 'О сайте',
  browseOtherLevels: 'Посмотреть другие уровни сложности',

  levels: {
    beginner: {
      name: 'Начальный',
      title: 'Гитарные табы для начинающих',
      description:
        'Простые песни, идеально подходящие для начинающих гитаристов. Лёгкие риффы, базовые аккорды и медленный темп.',
      longDescription:
        'Эти песни идеально подходят для гитаристов в первые шесть месяцев обучения. Они включают простые последовательности пауэр-аккордов, медленный или средний темп, базовые ритмические рисунки и несложные одноголосные риффы. Большинство из них можно выучить за одно занятие.'
    },

    intermediate: {
      name: 'Средний',
      title: 'Гитарные табы среднего уровня',
      description:
        'Песни, которые развивают технику благодаря более быстрым риффам, баррэ и соло средней сложности.',
      longDescription:
        'Песни среднего уровня требуют уверенного владения баррэ, palm muting на средней скорости, базовыми соло-техниками, такими как бенды, hammer-on и pull-off, а также умения переключаться между чистым и перегруженным звучанием. Ожидайте более высокий темп и более сложные структуры песен.'
    },

    advanced: {
      name: 'Продвинутый',
      title: 'Продвинутые гитарные табы',
      description:
        'Сложные песни с быстрым шреддингом, виртуозными соло и продвинутыми техниками исполнения.',
      longDescription:
        'Продвинутые песни требуют уверенного владения скоростным медиаторным штрихом, включая alternate picking и быстрый downpicking, sweep picking, tapping, сложные размеры, длинные соло и многослойные аранжировки. Именно такие композиции отличают опытных гитаристов от любителей.'
    }
  }
},

  hi: {
  home: 'होम',
  difficultyLevel: 'कठिनाई स्तर',
  artists: 'कलाकार',
  lessons: 'पाठ',
  whatToExpect: 'क्या सीखेंगे',
  songs: 'गाने',
  availableArtists: 'उपलब्ध कलाकार',
  browseSongs: 'गाने देखें',
  about: 'परिचय',
  browseOtherLevels: 'अन्य कठिनाई स्तर देखें',

  levels: {
    beginner: {
      name: 'शुरुआती',
      title: 'शुरुआती गिटार टैब्स',
      description:
        'नए गिटार वादकों के लिए आसान गाने। सरल रिफ़, बुनियादी कॉर्ड और धीमी गति वाले गीत।',
      longDescription:
        'ये गाने उन गिटारवादकों के लिए आदर्श हैं जिन्होंने पिछले छह महीनों के भीतर सीखना शुरू किया है। इनमें सरल पावर कॉर्ड प्रोग्रेशन, धीमी से मध्यम गति, बुनियादी स्ट्रमिंग पैटर्न और आसान सिंगल-नोट रिफ़ शामिल हैं। अधिकांश गाने एक ही अभ्यास सत्र में सीखे जा सकते हैं।'
    },

    intermediate: {
      name: 'मध्यम',
      title: 'मध्यम स्तर के गिटार टैब्स',
      description:
        'तेज़ रिफ़, बैरे कॉर्ड और मध्यम कठिनाई वाले सोलो के साथ आपकी तकनीक को चुनौती देने वाले गाने।',
      longDescription:
        'मध्यम स्तर के गानों के लिए बैरे कॉर्ड, मध्यम गति पर पाम म्यूटिंग, बेंड, हैमर-ऑन और पुल-ऑफ जैसी बुनियादी लीड तकनीकों तथा क्लीन और डिस्टॉर्शन टोन के बीच आसानी से बदलने की क्षमता आवश्यक है। इनमें तेज़ गति और अधिक जटिल गीत संरचनाएँ होती हैं।'
    },

    advanced: {
      name: 'उन्नत',
      title: 'उन्नत गिटार टैब्स',
      description:
        'तेज़ श्रेडिंग, जटिल सोलो और उन्नत तकनीकों वाले चुनौतीपूर्ण गाने।',
      longDescription:
        'उन्नत स्तर के गानों के लिए स्पीड पिकिंग, जिसमें अल्टरनेट पिकिंग और तेज़ डाउनपिकिंग, स्वीप पिकिंग, टैपिंग, जटिल टाइम सिग्नेचर, लंबे सोलो और बहु-भाग वाले अरेंजमेंट शामिल हैं, में महारत आवश्यक है। ये वही गाने हैं जो समर्पित गिटारवादकों को सामान्य शौकिया वादकों से अलग करते हैं।'
    }
  }
},

  sv: {
  home: 'Hem',
  difficultyLevel: 'Svårighetsgrad',
  artists: 'Artister',
  lessons: 'Lektioner',
  whatToExpect: 'Vad du kan förvänta dig',
  songs: 'Låtar',
  availableArtists: 'tillgängliga artister',
  browseSongs: 'Bläddra bland låtar',
  about: 'Om',
  browseOtherLevels: 'Utforska andra svårighetsgrader',

  levels: {
    beginner: {
      name: 'Nybörjare',
      title: 'Gitarrtabs för nybörjare',
      description:
        'Lätta låtar som är perfekta för nya gitarrister. Enkla riff, grundläggande ackord och långsamma tempon.',
      longDescription:
        'Dessa låtar är perfekta för gitarrister under sina första sex månader av spelande. De innehåller enkla powerackordsföljder, långsamma till medelsnabba tempon, grundläggande komp och lättspelade ensträngade riff. De flesta kan läras in under ett enda övningspass.'
    },

    intermediate: {
      name: 'Medelnivå',
      title: 'Gitarrtabs för medelnivå',
      description:
        'Låtar som utmanar din teknik med snabbare riff, barréackord och solon på medelnivå.',
      longDescription:
        'Låtar på medelnivå kräver att du behärskar barréackord, palm muting i måttliga tempon, grundläggande solotekniker som bends, hammer-ons och pull-offs samt att du kan växla mellan rent och distat ljud. Förvänta dig högre tempo och mer komplexa låtstrukturer.'
    },

    advanced: {
      name: 'Avancerad',
      title: 'Avancerade gitarrtabs',
      description:
        'Komplexa låtar med snabb shredding, avancerade solon och krävande speltekniker.',
      longDescription:
        'Avancerade låtar kräver att du behärskar speed picking, inklusive alternate picking och snabb downpicking, sweep picking, tapping, komplexa taktarter, långa solon och flerdelade arrangemang. Det här är låtarna som skiljer dedikerade gitarrister från mer tillfälliga spelare.'
    }
  }
},

  fi: {
  home: 'Etusivu',
  difficultyLevel: 'Vaikeustaso',
  artists: 'Artistit',
  lessons: 'Oppitunnit',
  whatToExpect: 'Mitä odottaa',
  songs: 'Kappaleet',
  availableArtists: 'saatavilla olevaa artistia',
  browseSongs: 'Selaa kappaleita',
  about: 'Tietoa',
  browseOtherLevels: 'Tutustu muihin vaikeustasoihin',

  levels: {
    beginner: {
      name: 'Aloittelija',
      title: 'Kitaratabit aloittelijoille',
      description:
        'Helppoja kappaleita uusille kitaristeille. Yksinkertaisia riffejä, perussointuja ja hitaita tempoja.',
      longDescription:
        'Nämä kappaleet sopivat erinomaisesti kitaristeille ensimmäisten kuuden soittokuukauden aikana. Ne sisältävät yksinkertaisia power-sointukiertoja, hitaita tai keskinopeita tempoja, peruskomppikuvioita ja selkeitä yhden nuotin riffejä. Suurin osa voidaan oppia yhden harjoituskerran aikana.'
    },

    intermediate: {
      name: 'Keskitaso',
      title: 'Keskitason kitaratabit',
      description:
        'Kappaleita, jotka kehittävät tekniikkaasi nopeammilla riffeillä, barré-soinnuilla ja keskitason sooloilla.',
      longDescription:
        'Keskitason kappaleet edellyttävät barré-sointujen hallintaa, palm mutingia keskinopeilla tempoilla, perussolotekniikoita kuten bendit, hammer-onit ja pull-offit sekä kykyä vaihtaa puhtaan ja särösoundin välillä. Odotettavissa on nopeampia tempoja ja monimutkaisempia kappalerakenteita.'
    },

    advanced: {
      name: 'Edistynyt',
      title: 'Edistyneet kitaratabit',
      description:
        'Monimutkaisia kappaleita, joissa on nopeaa shreddausta, vaativia sooloja ja edistyneitä tekniikoita.',
      longDescription:
        'Edistyneet kappaleet vaativat speed pickingin hallintaa, mukaan lukien alternate picking ja nopea downpicking, sweep picking, tapping, monimutkaiset tahtilajit, pitkät soolot ja useista osista koostuvat sovitukset. Nämä kappaleet erottavat omistautuneet kitaristit satunnaisista soittajista.'
        }
  }
}
};


export async function generateMetadata({ params }) {
  const { level, lang } = await params;
const difficulty = DIFFICULTY_LEVELS[level];

  const title = `${difficulty.name} Guitar Tabs - Easy ${difficulty.name} Songs to Learn | DadRock Tabs`;
  const description = `${difficulty.longDescription.substring(0, 155)}...`;

  return {
    title,
    description,
    keywords: `${difficulty.name.toLowerCase()} guitar tabs, easy guitar songs, ${difficulty.name.toLowerCase()} rock songs, learn guitar ${difficulty.name.toLowerCase()}, free tabs for ${difficulty.name.toLowerCase()}s`,
    openGraph: {
      title: `${difficulty.name} Guitar & Bass Tabs`,
      description,
      type: 'website',
      url: `https://dadrocktabs.com/difficulty/${level}`,
      siteName: 'DadRock Tabs',
    },
  };
}

export function generateStaticParams() {
  return Object.keys(DIFFICULTY_LEVELS).map(level => ({ level }));
}

export default async function DifficultyPage({ params }) {
  const { level, lang } = await params;
const currentLang = lang || 'en';
const t = difficultyT[currentLang] || difficultyT.en;
const difficulty = DIFFICULTY_LEVELS[level];

  if (!difficulty) {
    notFound();
  }

  const artistSlugs = getArtistsByDifficulty(level);
  const db = await getDb();
  const artistData = [];

  for (const slug of artistSlugs) {
    // Convert slug back to search pattern
    const pattern = slug.replace(/-/g, ' ');
    const escapedPattern = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    const count = await db.collection('videos').countDocuments({
      artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') }
    });

    if (count > 0) {
      const video = await db.collection('videos').findOne(
        { artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') } },
        { projection: { thumbnail: 1, artist: 1 } }
      );

      artistData.push({
        name: video?.artist?.replace(/ -$/, '').trim() || pattern,
        slug,
        lessonCount: count,
        thumbnail: video?.thumbnail || null,
      });
    }
  }

  artistData.sort((a, b) => b.lessonCount - a.lessonCount);
  const totalLessons = artistData.reduce((sum, a) => sum + a.lessonCount, 0);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': `${difficulty.name} Guitar Tabs`,
    'description': difficulty.longDescription,
    'url': `https://dadrocktabs.com/difficulty/${level}`,
    'isPartOf': { '@id': 'https://dadrocktabs.com/#website' },
    'mainEntity': {
      '@type': 'ItemList',
      'numberOfItems': artistData.length,
      'itemListElement': artistData.map((artist, i) => ({
        '@type': 'ListItem',
        'position': i + 1,
        'item': {
          '@type': 'MusicGroup',
          'name': artist.name,
          'url': `https://dadrocktabs.com/artist/${artist.slug}`,
        }
      }))
    }
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="min-h-screen bg-zinc-950 text-white">
        <DifficultyHeader lang={currentLang} level={level} />

        <main className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Breadcrumb */}
          <nav className="mb-6 text-sm text-zinc-400">
            <Link href={getLocalizedPath('/', currentLang)} className="hover:text-amber-400 transition-colors">{t.home}</Link>
            <span className="mx-2">/</span>
            <span className="text-white">{difficulty.name} {t.songs}</span>
          </nav>

          {/* Hero */}
          <div className="relative mb-10 p-8 sm:p-12 rounded-3xl overflow-hidden bg-zinc-900/50 border border-zinc-800">
            <div className={`absolute inset-0 bg-gradient-to-br ${difficulty.color} opacity-10`} />
            <div className="relative z-10">
              <div className="flex flex-col sm:flex-row sm:items-end gap-4 sm:gap-8">
                <div className="flex-1">
                  <span className="text-4xl mb-3 block">{difficulty.icon}</span>
                  <p className="text-sm font-medium text-amber-500/80 uppercase tracking-widest mb-2">
                    {t.difficultyLevel}
            </p>
                  <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4">
  {t.levels[level].title}
</h1>

<p className="text-zinc-300 text-lg max-w-2xl leading-relaxed">
  {t.levels[level].description}
</p>
                </div>
                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="px-5 py-3 rounded-2xl text-center bg-zinc-800/80 border border-zinc-700">
                    <div className="text-3xl font-bold text-amber-500">{artistData.length}</div>
                    <div className="text-xs text-zinc-400 uppercase tracking-wider">Artists</div>
                  </div>
                  <div className="px-5 py-3 rounded-2xl text-center bg-zinc-800/80 border border-zinc-700">
                    <div className="text-3xl font-bold text-amber-500">{totalLessons}</div>
                    <div className="text-xs text-zinc-400 uppercase tracking-wider">Lessons</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* About */}
          <div className="mb-10 p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
            <h2 className="text-xl font-bold mb-3 text-amber-500">{t.about}</h2>
            <p className="text-zinc-300 leading-relaxed">{difficulty.longDescription}</p>
            <p className="text-zinc-500 text-sm mt-3"><strong>Key criteria:</strong> {difficulty.criteria}</p>
          </div>

          {/* Artist Grid */}
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6 text-white">
  {difficulty.name} {t.artists} ({artistData.length})
</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {artistData.map((artist, index) => (
                <Link
                  key={artist.slug}
                  href={getLocalizedPath(`/artist/${artist.slug}`, currentLang)}
                  className="group bg-zinc-900/80 rounded-xl border border-zinc-800 overflow-hidden hover:border-amber-500/50 transition-all duration-300"
                >
                  <div className="relative h-36 overflow-hidden">
                    {artist.thumbnail ? (
                      <img
                        src={artist.thumbnail}
                        alt={`${artist.name} Guitar Tabs`}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                        loading="lazy"
                      />
                    ) : (
                      <div className={`w-full h-full bg-gradient-to-br ${difficulty.color} opacity-20`} />
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/50 to-transparent" />
                    <div className="absolute top-3 right-3 text-xs font-bold text-black px-2.5 py-1 rounded-lg bg-amber-500">
                      {artist.lessonCount} {t.lessons}
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-bold text-lg text-white group-hover:text-amber-500 transition-colors">
                      {artist.name}
                    </h3>
                    <p className="text-sm text-zinc-500">{difficulty.name} • {artist.lessonCount} tabs</p>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* Other Difficulty Levels */}
          <section className="mt-12 p-8 rounded-2xl border border-zinc-800 bg-zinc-900/30">
            <h2 className="text-xl font-bold mb-4">{t.browseOtherLevels}</h2>
            <div className="flex flex-wrap gap-4">
              {Object.entries(DIFFICULTY_LEVELS)
                .filter(([key]) => key !== level)
                .map(([key, diff]) => (
                  <Link
                    key={key}
                    href={getLocalizedPath(`/difficulty/${key}`, currentLang)}
                    className="flex items-center gap-2 px-5 py-3 bg-zinc-800 hover:bg-amber-500 hover:text-black rounded-full font-medium transition-all border border-zinc-700 hover:border-amber-500"
                  >
                    <span>{diff.icon}</span>
                    {diff.name}
                  </Link>
                ))}
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t border-zinc-800">
          <div className="container mx-auto px-4 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-zinc-500 text-sm">© {new Date().getFullYear()} DadRock Tabs. Free guitar & bass lessons.</p>
            <Link href={getLocalizedPath('/', currentLang)} className="text-zinc-500 hover:text-amber-400 transition-colors">{t.home}</Link>
          </div>
        </footer>
      </div>
    </>
  );
}
