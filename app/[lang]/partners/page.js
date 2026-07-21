import { locales } from '@/lib/i18n';
import { notFound } from 'next/navigation';
import PartnersPage from '../../../partners/page';

export async function generateStaticParams() {
  return locales
    .filter((lang) => lang !== 'en')
    .map((lang) => ({ lang }));
}

export default async function LocalizedPartnersPage({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang;

  if (!locales.includes(lang) || lang === 'en') {
    notFound();
  }

  return <PartnersPage />;
    }
