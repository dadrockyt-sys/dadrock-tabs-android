export {
  default,
  generateMetadata
} from '../../../learn/[slug]/page';

// Localized guide pages need the dynamic [lang] param at request time.
// Re-exporting the English route's slug-only generateStaticParams caused
// Next.js to treat /[lang]/learn/[slug] as SSG without a concrete lang,
// producing DYNAMIC_SERVER_USAGE 500s for translated guide URLs.
export const dynamic = 'force-dynamic';
