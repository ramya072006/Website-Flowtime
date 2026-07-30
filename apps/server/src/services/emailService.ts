import * as Brevo from '@getbrevo/brevo';
import { config } from '../config';
import { logger } from '../utils/logger';

// ── Lazy Brevo client ─────────────────────────────────────────────────────────
let _client: Brevo.TransactionalEmailsApi | null | undefined = undefined;

const getClient = (): Brevo.TransactionalEmailsApi | null => {
  if (_client !== undefined) return _client;

  const key = process.env.BREVO_API_KEY;
  if (!key) {
    logger.warn('BREVO_API_KEY not set — emails will not be sent');
    _client = null;
    return null;
  }

  const api = new Brevo.TransactionalEmailsApi();
  api.setApiKey(Brevo.TransactionalEmailsApiApiKeys.apiKey, key);
  _client = api;
  logger.info('Brevo email client initialized');
  return _client;
};

const SENDER_NAME = 'TaskManagement';
const SENDER_EMAIL = process.env.BREVO_FROM_EMAIL || 'ramyasribalivada@gmail.com';

// ── Shared HTML wrapper ────────────────────────────────────────────────────────
const wrap = (body: string) => `
  <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:560px;margin:0 auto;
              background:#fff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:32px 40px;">
      <h1 style="color:white;margin:0;font-size:24px;font-weight:700;">✅ TaskManagement</h1>
    </div>
    <div style="padding:32px 40px;">${body}</div>
    <div style="padding:16px 40px;background:#f9fafb;border-top:1px solid #e5e7eb;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">
        You received this because you have a TaskManagement account.
        If you didn't request this, you can safely ignore it.
      </p>
    </div>
  </div>
`;

// ── Core send ─────────────────────────────────────────────────────────────────
const send = async (to: string, subject: string, htmlContent: string): Promise<void> => {
  const client = getClient();
  if (!client) {
    logger.warn(`Email skipped — no Brevo client. To: ${to}`);
    return;
  }

  logger.info(`Sending email via Brevo to: ${to}`);

  const email = new Brevo.SendSmtpEmail();
  email.sender = { name: SENDER_NAME, email: SENDER_EMAIL };
  email.to = [{ email: to }];
  email.subject = subject;
  email.htmlContent = htmlContent;

  const result = await client.sendTransacEmail(email);
  logger.info(`Email sent — messageId: ${(result.body as { messageId?: string })?.messageId}, to: ${to}`);
};

// ── Public methods ────────────────────────────────────────────────────────────
export const emailService = {
  async sendOtpEmail(email: string, name: string, otp: string) {
    try {
      await send(
        email,
        'Your TaskManagement verification code',
        wrap(`
          <h2 style="color:#111827;margin-top:0;">Verify your email</h2>
          <p style="color:#374151;">Hi <strong>${name}</strong>, use the code below to verify your email address.</p>
          <div style="background:#f3f4f6;border-radius:8px;padding:24px;text-align:center;margin:24px 0;">
            <span style="font-size:40px;font-weight:800;letter-spacing:12px;color:#6366f1;">${otp}</span>
          </div>
          <p style="color:#6b7280;font-size:14px;">
            This code expires in <strong>10 minutes</strong>. Do not share it with anyone.
          </p>
        `)
      );
    } catch (err) {
      logger.error('sendOtpEmail failed:', err);
    }
  },

  async sendPasswordResetEmail(email: string, name: string, token: string) {
    const resetUrl = `${config.clientUrl}/reset-password?token=${token}&email=${encodeURIComponent(email)}`;
    try {
      await send(
        email,
        'Reset your TaskManagement password',
        wrap(`
          <h2 style="color:#111827;margin-top:0;">Reset your password</h2>
          <p style="color:#374151;">Hi <strong>${name}</strong>, we received a request to reset your password.</p>
          <div style="margin:24px 0;">
            <a href="${resetUrl}"
               style="background:#6366f1;color:white;padding:14px 28px;text-decoration:none;
                      border-radius:8px;display:inline-block;font-weight:600;font-size:15px;">
              Reset Password
            </a>
          </div>
          <p style="color:#6b7280;font-size:14px;">
            This link expires in <strong>1 hour</strong>. If you didn't request this, ignore this email.
          </p>
          <p style="color:#9ca3af;font-size:12px;word-break:break-all;">Or copy: ${resetUrl}</p>
        `)
      );
    } catch (err) {
      logger.error('sendPasswordResetEmail failed:', err);
    }
  },

  async sendPasswordChangedEmail(email: string, name: string) {
    try {
      await send(
        email,
        'Your TaskManagement password was changed',
        wrap(`
          <h2 style="color:#111827;margin-top:0;">Password changed</h2>
          <p style="color:#374151;">Hi <strong>${name}</strong>, your password was successfully changed.</p>
          <p style="color:#374151;">
            If you didn't do this,
            <a href="${config.clientUrl}/forgot-password" style="color:#6366f1;">reset your password immediately</a>.
          </p>
        `)
      );
    } catch (err) {
      logger.error('sendPasswordChangedEmail failed:', err);
    }
  },

  async sendNotificationEmail(email: string, subject: string, message: string) {
    try {
      await send(email, subject, wrap(`<p style="color:#374151;">${message}</p>`));
    } catch (err) {
      logger.error('sendNotificationEmail failed:', err);
    }
  },
};
