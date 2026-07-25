import { NextResponse } from 'next/server';
import { createBlankTabPDF } from '@/lib/tabRenderer/pdf';

export async function GET() {
  try {
      const pdfBytes = await createBlankTabPDF();

          return new NextResponse(pdfBytes, {
                headers: {
                        'Content-Type': 'application/pdf',
                                'Content-Disposition': 'inline; filename="dadrock-preview.pdf"',
                                      },
                                          });
                                            } catch (error) {
                                                console.error(error);

                                                    return NextResponse.json(
                                                          {
                                                                  error: 'Failed to generate PDF',
                                                                        },
                                                                              {
                                                                                      status: 500,
                                                                                            }
                                                                                                );
                                                                                                  }
                                                                                                  }