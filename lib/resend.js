import { Resend } from 'resend';

function getResendClient() {
  const apiKey = process.env.RESEND_API_KEY;

  if (!apiKey) {
    throw new Error('RESEND_API_KEY is not configured.');
  }

  return new Resend(apiKey);
}

export const resend = {
  emails: {
    async send(...args) {
      const client = getResendClient();
      return client.emails.send(...args);
    },
  },
};
