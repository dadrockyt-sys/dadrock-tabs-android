import { createBlankTabPDF } from '@/lib/tabRenderer/pdf';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const pdfBytes = await createBlankTabPDF();

    return new Response(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline; filename="dadrock-preview.pdf"',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
      },
    });
  } catch (error) {
    console.error('PDF preview error:', error);

    return Response.json(
      {
        error: 'Failed to generate PDF preview',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
